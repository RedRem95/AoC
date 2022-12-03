from .Day01 import *
from .Day02 import *
from .Day03 import *


from AoC_Companion.Preprocess import Preprocessor

@Preprocessor(year=2021)
def preproc_0(data: str):
    return data.split("\n")
