import torch
import torch.nn as nn
import torch.nn.functional as F
from game.constants import *

class AlphaTiger(nn.Module):
    def __init__(self, input_size=GAME_VECTOR_LENGTH, hidden_size=256):
        super(AlphaTiger, self).__init__()

        # factorization of RN and ST
        self.rn_size = NODES * len(COASTAL_INDICES)
        self.st_size = NODES * len(COASTAL_INDICES)

        target_indices = []
        offset = 0
        for name, size, move_type in MOVE_SPACE:
            if name == "Royal Navy":
                self.rn_start = offset
            elif name == "Sea Trade":
                self.st_start = offset
            else:
                target_indices.extend(range(offset, offset + size))
            offset += size

        self.base_size = len(target_indices)
        self.factorized_size = len(target_indices) + NODES * 4
        self.register_buffer("base_idx_map", torch.tensor(target_indices, dtype=torch.long))

        rn_src_list, rn_dest_list = [], []
        st_src_list, st_dest_list = [], []

        for idx in range(self.rn_size):
            node_idx = idx // len(COASTAL_INDICES)
            coast_idx = COASTAL_INDICES[idx % len(COASTAL_INDICES)]

            rn_src_list.append(node_idx)
            rn_dest_list.append(coast_idx)

            st_src_list.append(coast_idx)
            st_dest_list.append(node_idx)
        
        # buffer everything to gpu
        self.register_buffer("rn_src_idx", torch.tensor(rn_src_list, dtype=torch.long))
        self.register_buffer("rn_dest_idx", torch.tensor(rn_dest_list, dtype=torch.long))
        self.register_buffer("st_src_idx", torch.tensor(st_src_list, dtype=torch.long))
        self.register_buffer("st_dest_idx", torch.tensor(st_dest_list, dtype=torch.long))

        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size)

        self.value_fc1 = nn.Linear(hidden_size, 64)
        self.value_fc2 = nn.Linear(64, 1)

        self.policy_fc1 = nn.Linear(hidden_size, hidden_size)
        # return factorized output
        self.policy_fc2 = nn.Linear(hidden_size, self.factorized_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))

        value = F.relu(self.value_fc1(x))
        value = torch.tanh(self.value_fc2(value))

        policy = F.relu(self.policy_fc1(x))
        raw_logits = self.policy_fc2(policy)
        
        batch_size = raw_logits.shape[0]
        
        # unfactorize RN and ST for the game engine
        idx = 0
        base_logits = raw_logits[:, idx : idx + self.base_size]; idx += self.base_size

        rn_src  = raw_logits[:, idx : idx + NODES]; idx += NODES
        rn_dest = raw_logits[:, idx : idx + NODES]; idx += NODES
        
        st_src  = raw_logits[:, idx : idx + NODES]; idx += NODES
        st_dest = raw_logits[:, idx : idx + NODES]

        final_logits = torch.zeros((batch_size, MOVE_VECTOR_LENGTH), device=raw_logits.device)
        final_logits[:, self.base_idx_map] = base_logits
        final_logits[:, self.rn_start : self.rn_start + self.rn_size] = rn_src[:, self.rn_src_idx] + rn_dest[:, self.rn_dest_idx]
        final_logits[:, self.st_start : self.st_start + self.st_size] = st_src[:, self.st_src_idx] + st_dest[:, self.st_dest_idx]

        # return evaluation and policy logits
        return value, final_logits
    
    @torch.no_grad()
    def predict(self, state):
        device = next(self.parameters()).device
        x = torch.tensor(state.vector, dtype=torch.float32, device=device).unsqueeze(0)
        value, policy_logits = self.forward(x)
        return value.item(), policy_logits.squeeze(0).cpu().numpy()
    
def save_checkpoint(model, optimizer, iteration, path):
    torch.save({
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'iteration': iteration,
    }, path)

def load_checkpoint(model, optimizer, path):
    checkpoint = torch.load(path, map_location=torch.device('cpu'), weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    if optimizer is not None:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    return checkpoint.get('iteration', 0)