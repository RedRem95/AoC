from .Day01 import *
from .Day02 import *
from .Day03 import *
from .Day04 import *
from .Day05 import *


from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022)
def preproc_0(data: str):
    return data.split("\n")
