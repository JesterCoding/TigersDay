import torch
import matplotlib.pyplot as plt
import seaborn as sns
from game.constants import *

if __name__ == "__main__":
    # 1. Load the model weights (safely mapping to CPU)
    checkpoint = torch.load(DEFAULT_MODEL, map_location='cpu', weights_only=False)
    state_dict = checkpoint.get('model_state_dict', checkpoint)

    # 2. Extract the weights for your final policy layer
    # This pulls the actual 2D grid of floating-point numbers
    weights = state_dict['fc1.weight'].numpy()

    # 3. Create the visual heatmap
    plt.figure(figsize=(16, 8))
    # 'RdBu_r' gives a nice Red (positive) to Blue (negative) gradient
    sns.heatmap(weights, cmap='RdBu_r', center=0, 
                cbar_kws={'label': 'Weight Magnitude'})

    plt.title('AlphaTiger Policy Layer Weights (policy_fc2)', fontsize=16)
    plt.xlabel('Game State Neurons (Input: 148)', fontsize=12)
    plt.ylabel('Hidden Layer Slots (Output: 256)', fontsize=12)
    plt.tight_layout()

    # 4. Show the window!
    plt.show()