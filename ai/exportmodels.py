import torch
from ai.neural import AlphaTiger
from game.constants import GAME_VECTOR_LENGTH

# 1. Initialize and load your trained weights
model = AlphaTiger()
model.load_state_dict(torch.load("path_to_your_trained_weights.pth"))
model.eval() # CRITICAL for ONNX export

# 2. Create the dummy input based on your GAME_VECTOR_LENGTH
# The '1' is the batch size.
dummy_input = torch.randn(1, GAME_VECTOR_LENGTH)

# 3. Export to ONNX with TWO output names
torch.onnx.export(
    model,
    (dummy_input,),
    "public/alphatiger.onnx",
    export_params=True,
    opset_version=14,
    do_constant_folding=True,
    input_names=['board_state'],
    output_names=['value', 'policy_logits'] # Map to the two outputs of forward()
)
print("Two-head model successfully exported to ONNX!")