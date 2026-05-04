import argparse
import torch
import matplotlib.pyplot as plt
import seaborn as sns
from game.constants import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a heatmap for AlphaTiger model weights.")
    parser.add_argument(
        '--ckpt', 
        type=str, 
        default=DEFAULT_MODEL, 
        help='Path to the model checkpoint file (default: uses DEFAULT_MODEL from constants)'
    )
    args = parser.parse_args()

    checkpoint = torch.load(args.ckpt, map_location='cpu', weights_only=False)
    state_dict = checkpoint.get('model_state_dict', checkpoint)

    weights = state_dict['fc1.weight'].numpy()

    plt.figure(figsize=(16, 8))
    sns.heatmap(weights, cmap='RdBu_r', center=0, 
                cbar_kws={'label': 'Weight Magnitude'})

    plt.title('AlphaTiger Policy Layer Weights (policy_fc2)', fontsize=16)
    plt.xlabel('Game State Neurons (Input: 148)', fontsize=12)
    plt.ylabel('Hidden Layer Slots (Output: 256)', fontsize=12)
    plt.tight_layout()

    plt.show()