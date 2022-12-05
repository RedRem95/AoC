from .Day01 import *
from .Day02 import *
from .Day03 import *
from .Day04 import *
from .Day05 import *
from .Day06 import *
from .Day07 import *
from .Day08 import *
from .Day09 import *
from .Day10 import *
from .Day11 import *
from .Day12 import *
from .Day13 import *
from .Day14 import *
from .Day15 import *
from .Day16 import *
from .Day17 import *
from .Day18 import *
from .Day19 import *
from .Day20 import *
from .Day21 import *
from .Day22 import *
from .Day23 import *
from .Day24 import *

from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2021)
def preproc_0(data: str):
    return data.split("\n")
