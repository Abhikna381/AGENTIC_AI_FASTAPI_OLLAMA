import torch
print(f"Is CUDA available? {torch.cuda.is_available()}")
print(f"GPU Name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")

import torch
from packaging import version

# Force-check the version to see what you are running
print(f"Current Torch Version: {torch.__version__}")

# If you are below 2.6, some newer Gemma 3 features might glitch.
# Updating is the only 100% reliable fix for the mask_function error.