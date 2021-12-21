import os

from AoC_Companion.Day import StarTask

from y2021 import Day01, Day02, Day03, Day04, Day05


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


def test_day04():
    day = Day04.Day04(year=2021)
    with open(os.path.join(os.path.dirname(__file__), "test_resources", "day04.txt"), "rb") as fin:
        data = day.construct_data_package(data=fin.read().decode("utf-8"))

    expected = {
        StarTask.Task01: 4512,
        StarTask.Task02: 1924
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"


def test_day05():
    day = Day05.Day05(year=2021)
    with open(os.path.join(os.path.dirname(__file__), "test_resources", "day05.txt"), "rb") as fin:
        data = day.construct_data_package(data=fin.read().decode("utf-8"))

    expected = {
        StarTask.Task01: 5,
        StarTask.Task02: 12
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"


def test_day06():
    from y2021 import Day06
    day = Day06.Day06(year=2021, days={"1": 80, "2": 256}, graphs=False)
    data = day.construct_data_package(data="3,4,3,1,2")

    expected = {
        StarTask.Task01: 5934,
        StarTask.Task02: 26984457539
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"


def test_day07():
    from y2021 import Day07
    day = Day07.Day07(year=2021)
    data = day.construct_data_package(data="16,1,2,0,4,2,7,1,2,14")

    expected = {
        StarTask.Task01: 37,
        StarTask.Task02: 168
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"


def test_day08():
    from y2021 import Day08
    day = Day08.Day08(year=2021)
    with open(os.path.join(os.path.dirname(__file__), "test_resources", "day08.txt"), "rb") as fin:
        data = day.construct_data_package(data=fin.read().decode("utf-8"))

    expected = {
        StarTask.Task01: 26,
        StarTask.Task02: 61229
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"


def test_day09():
    from y2021 import Day09
    day = Day09.Day09(year=2021, create_img=False)
    with open(os.path.join(os.path.dirname(__file__), "test_resources", "day09.txt"), "rb") as fin:
        data = day.construct_data_package(data=fin.read().decode("utf-8"))

    expected = {
        StarTask.Task01: 15,
        StarTask.Task02: 1134
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"


def test_day10():
    from y2021 import Day10
    day = Day10.Day10(year=2021)
    with open(os.path.join(os.path.dirname(__file__), "test_resources", "day10.txt"), "rb") as fin:
        data = day.construct_data_package(data=fin.read().decode("utf-8"))

    expected = {
        StarTask.Task01: 26397,
        StarTask.Task02: 288957
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"


def test_day11():
    from y2021 import Day11
    day = Day11.Day11(year=2021)
    with open(os.path.join(os.path.dirname(__file__), "test_resources", "day11.txt"), "rb") as fin:
        data = day.construct_data_package(data=fin.read().decode("utf-8"))

    expected = {
        StarTask.Task01: 1656,
        StarTask.Task02: 195
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"


def test_day12():
    from y2021 import Day12
    day = Day12.Day12(year=2021)
    with open(os.path.join(os.path.dirname(__file__), "test_resources", "day12.txt"), "rb") as fin:
        data = day.construct_data_package(data=fin.read().decode("utf-8"))

    expected = {
        StarTask.Task01: 226,
        StarTask.Task02: 3509
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"


def test_day13():
    from y2021 import Day13
    day = Day13.Day13(year=2021)
    with open(os.path.join(os.path.dirname(__file__), "test_resources", "day13.txt"), "rb") as fin:
        data = day.construct_data_package(data=fin.read().decode("utf-8"))

    expected = {
        StarTask.Task01: 17,
        StarTask.Task02: "See below in log"
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"


def test_day14():
    from y2021 import Day14
    day = Day14.Day14(year=2021, sim_steps={"1": 10, "2": 40})
    with open(os.path.join(os.path.dirname(__file__), "test_resources", "day14.txt"), "rb") as fin:
        data = day.construct_data_package(data=fin.read().decode("utf-8"))

    expected = {
        StarTask.Task01: 1588,
        StarTask.Task02: 2188189693529
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"


def test_day15():
    from y2021 import Day15
    day = Day15.Day15(year=2021)
    with open(os.path.join(os.path.dirname(__file__), "test_resources", "day15.txt"), "rb") as fin:
        data = day.construct_data_package(data=fin.read().decode("utf-8"))

    expected = {
        StarTask.Task01: 40,
        StarTask.Task02: 315
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"


def test_day16():
    from y2021 import Day16
    day = Day16.Day16(year=2021, create_summary=False)

    expected = {
        StarTask.Task01: [("8A004A801A8002F478", 16),
                          ("620080001611562C8802118E34", 12),
                          ("C0015000016115A2E0802F182340", 23),
                          ("A0016C880162017C3686B18A3D4780", 31)],
        StarTask.Task02: [("C200B40A82", 3),
                          ("04005AC33890", 54),
                          ("880086C3E88112", 7),
                          ("CE00C43D881120", 9),
                          ("D8005AC2A8F0", 1),
                          ("F600BC2D8F", 0),
                          ("9C005AC2F8F0", 0),
                          ("9C0141080250320F1802104A08", 1)]
    }

    for task, expected_data_pairs in expected.items():
        for data, expected_data in expected_data_pairs:
            data_const = day.construct_data_package(data=data)
            res = day.run(task=task, data=data_const)
            if res is not None:
                res = res.get_result()
            assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} - {data} failed"


def test_day17():
    from y2021 import Day17
    day = Day17.Day17(year=2021)
    data = day.construct_data_package(data="target area: x=20..30, y=-10..-5")

    expected = {
        StarTask.Task01: 45,
        StarTask.Task02: 112
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"


def test_day18():
    from y2021 import Day18
    day = Day18.Day18(year=2021)
    with open(os.path.join(os.path.dirname(__file__), "test_resources", "day18.txt"), "rb") as fin:
        data = day.construct_data_package(data=fin.read().decode("utf-8"))

    expected = {
        StarTask.Task01: 4140,
        StarTask.Task02: 3993
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"


def test_day19():
    from y2021 import Day19
    day = Day19.Day19(year=2021)
    with open(os.path.join(os.path.dirname(__file__), "test_resources", "day19.txt"), "rb") as fin:
        data = day.construct_data_package(data=fin.read().decode("utf-8"))

    expected = {
        StarTask.Task01: 79,
        StarTask.Task02: 3621
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"


def test_day20():
    from y2021 import Day20
    day = Day20.Day20(year=2021, steps={"1": 2, "2": 50}, create_visual=False)
    with open(os.path.join(os.path.dirname(__file__), "test_resources", "day20.txt"), "rb") as fin:
        data = day.construct_data_package(data=fin.read().decode("utf-8"))

    expected = {
        StarTask.Task01: 35,
        StarTask.Task02: 3351
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"


def test_day21():
    from y2021 import Day21
    day = Day21.Day21(year=2021)
    with open(os.path.join(os.path.dirname(__file__), "test_resources", "day21.txt"), "rb") as fin:
        data = day.construct_data_package(data=fin.read().decode("utf-8"))

    expected = {
        StarTask.Task01: 739785,
        StarTask.Task02: 444356092776315
    }

    for task, expected_data in expected.items():
        res = day.run(task=task, data=data)
        if res is not None:
            res = res.get_result()
        assert res == expected_data, f"{day.get_year()} - {day.get_name()} - {task.name} failed"
