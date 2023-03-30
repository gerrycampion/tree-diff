from json import dumps
from base_list_matcher import BaseListMatcher


def diff_value(
    list_matcher: BaseListMatcher, base, compare, base_pointer, compare_pointer
):
    scalars = {str, int, float, bool}
    objects = {dict}
    arrays = {list, tuple}
    if (
        base is None
        or compare is None
        or type(base) in scalars
        or type(compare) in scalars
        or type(base) != type(compare)
    ):
        return diff_scalar(base, compare, base_pointer, compare_pointer)
    if type(base) in objects and type(compare) in objects:
        return diff_obj(list_matcher, base, compare, base_pointer, compare_pointer)
    if type(base) in arrays and type(compare) in arrays:
        return diff_array(list_matcher, base, compare, base_pointer, compare_pointer)


def diff_scalar(base, compare, base_pointer, compare_pointer):
    if base != compare:
        return [
            {
                "op": "test",
                "path_base": base_pointer,
                "path_compare": compare_pointer,
                "value": base,
            },
            {
                "op": "replace",
                "path_base": base_pointer,
                "path_compare": compare_pointer,
                "value": compare,
            },
            *(
                []
                if base_pointer == compare_pointer
                else [{"op": "move", "from": base_pointer, "path": compare_pointer}]
            ),
        ]
    return []


def diff_obj(
    list_matcher: BaseListMatcher,
    base: dict,
    compare: dict,
    base_pointer="",
    compare_pointer="",
):
    deletions = [
        patch
        for k in set(base.keys()) - set(compare.keys())
        for patch in (
            {
                "op": "test",
                "path_base": f"{base_pointer}/{k}",
                "path_compare": f"{compare_pointer}/{k}",
                "value": base[k],
            },
            {
                "op": "remove",
                "path_base": f"{base_pointer}/{k}",
                "path_compare": f"{compare_pointer}/{k}",
            },
        )
    ]
    additions = [
        {
            "op": "add",
            "path_base": f"{base_pointer}/{k}",
            "path_compare": f"{compare_pointer}/{k}",
            "value": compare[k],
        }
        for k in set(compare.keys()) - set(base.keys())
    ]
    updates = []
    for k in set(base.keys()) & set(compare.keys()):
        updates.extend(
            diff_value(
                list_matcher,
                base[k],
                compare[k],
                f"{base_pointer}/{k}",
                f"{compare_pointer}/{k}",
            )
        )
    return deletions + additions + updates


def diff_array(
    list_matcher: BaseListMatcher, base, compare, base_pointer, compare_pointer
):
    json_to_base = _stringify(base)
    json_to_compare = _stringify(compare)
    json_base = set(json_to_base.keys())
    json_compare = set(json_to_compare.keys())
    pairs = list_matcher.match_lists(json_base, json_compare)
    deletions = [
        patch
        for item in json_base
        for patch in (
            {
                "op": "test",
                "path_base": f"{base_pointer}/{json_to_base[item][0]}",
                "path_compare": f"{compare_pointer}",
                "value": json_to_base[item][1],
            },
            {
                "op": "remove",
                "path_base": f"{base_pointer}/{json_to_base[item][0]}",
                "path_compare": f"{compare_pointer}",
            },
        )
    ]
    additions = [
        {
            "op": "add",
            "path_base": f"{base_pointer}",
            "path_compare": f"{compare_pointer}/{json_to_compare[item][0]}",
            "value": json_to_compare[item][1],
        }
        for item in json_compare
    ]
    updates = []
    for base, comp in pairs:
        updates.extend(
            diff_value(
                list_matcher,
                json_to_base[base][1],
                json_to_compare[comp][1],
                f"{base_pointer}/{json_to_base[base][0]}",
                f"{compare_pointer}/{json_to_compare[comp][0]}",
            )
        )
    return deletions + additions + updates


def _stringify(json_list):
    return {
        dumps(item, sort_keys=True, separators=(",", ":")): (index, item)
        for (index, item) in enumerate(json_list)
    }
