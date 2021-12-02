from . import aoc
from AoC_Companion.Day import TaskResult

if __name__ == "__main__":
    results = aoc.run_latest()
    print(TaskResult.format(*results, show_log=True))
