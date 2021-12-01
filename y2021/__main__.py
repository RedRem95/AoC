from . import aoc
from AoC_Companion.Day import TaskResult

if __name__ == "__main__":
    results = aoc.run(1)
    print(TaskResult.format(results=results))
