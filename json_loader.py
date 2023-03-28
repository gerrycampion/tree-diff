from json import load, dump


def load_from_file(filename):
    with open(filename) as fp:
        return load(fp)


def save_to_file(obj, filename):
    with open(filename, "w") as fp:
        dump(
            obj=obj,
            fp=fp,
            indent=3,
            sort_keys=True,
        )
