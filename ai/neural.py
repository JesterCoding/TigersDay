import torch
import torch.nn as nn
import torch.nn.functional as F
from game.constants import *

class AlphaTiger(nn.Module):
    def __init__(self, input_size=GAME_VECTOR_LENGTH, hidden_size=256, output_size=MOVE_VECTOR_LENGTH):
        super(AlphaTiger, self).__init__()

        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size)

        self.value_fc1 = nn.Linear(hidden_size, 64)
        self.value_fc2 = nn.Linear(64, 1)

        self.policy_fc1 = nn.Linear(hidden_size, hidden_size)
        self.policy_fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))

        value = F.relu(self.value_fc1(x))
        value = torch.tanh(self.value_fc2(value))

        policy = F.relu(self.policy_fc1(x))
        policy = self.policy_fc2(policy)

        # return evaluation and policy logits
        return value, policy
    
    @torch.no_grad()
    def predict(self, state):
        x = torch.tensor(state.vector, dtype=torch.float32).unsqueeze(0)
        value, policy_logits = self.forward(x)
        policy = F.softmax(policy_logits, dim=-1)
        return value.item(), policy.squeeze(0).numpy()
