import torch
import torch.nn as nn


class TigerNet(nn.Module):

    def __init__(self, input_dim=138, action_dim=636, hidden_sizes=(512, 256, 256)):
        super().__init__()

        # Shared trunk
        layers = []
        prev = input_dim
        for h in hidden_sizes:
            layers.append(nn.Linear(prev, h))
            layers.append(nn.BatchNorm1d(h))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.1))
            prev = h
        self.trunk = nn.Sequential(*layers)

        # Policy head: raw logits over action space
        self.policy_head = nn.Sequential(
            nn.Linear(prev, 256),
            nn.ReLU(),
            nn.Linear(256, action_dim)
        )

        # Value head: scalar in [-1, 1]
        self.value_head = nn.Sequential(
            nn.Linear(prev, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Tanh()
        )

    def forward(self, x):
        """Batch inference.
        Args: x — (batch, 138) float tensor
        Returns: (policy_logits, value) — (batch, 636), (batch,)
        """
        shared = self.trunk(x)
        policy_logits = self.policy_head(shared)
        value = self.value_head(shared)
        return policy_logits, value.squeeze(-1)

    def predict(self, state_vector):
        """Single-state inference for MCTS. No gradient computation.
        Args: state_vector — numpy array of shape (138,)
        Returns: (policy_logits_np, value_float)
        """
        self.eval()
        with torch.no_grad():
            x = torch.FloatTensor(state_vector).unsqueeze(0)
            policy_logits, value = self.forward(x)
            return policy_logits.squeeze(0).numpy(), value.item()


def save_checkpoint(model, optimizer, iteration, path):
    torch.save({
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'iteration': iteration,
    }, path)


def load_checkpoint(model, optimizer, path):
    checkpoint = torch.load(path, weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    if optimizer is not None:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    return checkpoint.get('iteration', 0)
