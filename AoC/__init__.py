if __name__ == "__main__":
    import os
    from AoC_Companion.AoC import run, import_stuff, SpecialType
    from AoC_Companion.Day import Collection

    import_stuff(__file__)

    years = SpecialType.apply(elements=[SpecialType.latest], coll=Collection.available_years())
    if len(os.environ.get("AOC_ALL_DAYS", "")):
        days = []
    else:
        days = SpecialType.apply(elements=[SpecialType.latest], coll=Collection.available_days(years=years))

    run(years=years, days=days, tasks=[], log=True)

else:
    import os
    from importlib import import_module

    for k in os.listdir(os.path.dirname(__file__)):
        if not os.path.isdir(os.path.join(os.path.dirname(__file__), k)) or k.startswith("_"):
            continue
        import_module(f".{k}", __name__)
