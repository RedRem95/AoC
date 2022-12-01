from .Day01 import *


from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2021)
def preproc_0(data: str):
    return data.split("\n")
