import os
from importlib import import_module

for k in os.listdir(os.path.dirname(__file__)):
    if not os.path.isdir(os.path.join(os.path.dirname(__file__), k)) or k.startswith("_"):
        continue
    import_module(f".{k}", __name__)
