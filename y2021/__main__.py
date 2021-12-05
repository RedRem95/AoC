import argparse

from AoC_Companion.Day import TaskResult

from . import aoc

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-a', "--all", action="store_true", dest="all", help="Decision if you want to run all days")
    args = parser.parse_args()

    if args.all:
        results = aoc.run()
    else:
        results = aoc.run_latest()
    print(TaskResult.format(*results, show_log=True))
