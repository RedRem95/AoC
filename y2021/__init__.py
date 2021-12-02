import os

import AoC_Companion
from AoC_Companion.AoC import AoC

print(f"Using AoC-Companion version {AoC_Companion.__version__}")
aoc = AoC(year=2021, source_folder=os.path.dirname(__file__))
