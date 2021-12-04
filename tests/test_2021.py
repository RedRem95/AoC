import os

import pytest

from AoC_Companion.Day import StarTask
from y2021 import Day01, Day02, Day03


def test_day01():
    day = Day01.Day01(year=2021)
    data = day.construct_data_package(data="199\n200\n208\n210\n200\n207\n240\n269\n260\n263")

    expected = {
        StarTask.Task01: "7",
        StarTask.Task02: "5"
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"


def test_day02():
    day = Day02.Day02(year=2021)
    data = day.construct_data_package(data="forward 5\ndown 5\nforward 8\nup 3\ndown 8\nforward 2")

    expected = {
        StarTask.Task01: "150",
        StarTask.Task02: "900"
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"


def test_day03():
    day = Day03.Day03(year=2021)
    with open(os.path.join(os.path.dirname(__file__), "test_resources", "day03.txt"), "rb") as fin:
        data = day.construct_data_package(data=fin.read().decode("utf-8"))

    expected = {
        StarTask.Task01: "198",
        StarTask.Task02: "230"
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"
