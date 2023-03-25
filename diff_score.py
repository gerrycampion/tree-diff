from each_deep import each_deep
from collections import defaultdict, Counter
from itertools import product
from difflib import SequenceMatcher
from json import dumps


def post_order_list(tree):
    lst = []
    each_deep(
        node=tree,
        after=lambda context, path, indexed_path: lst.append(
            {"node": context[-1], "path": path, "indexed_path": indexed_path}
        ),
    )
    return lst


def append_if_str(context, lst):
    if isinstance(context[-1], str):
        lst.append(context[-1])


def all_values(tree):
    lst = []
    each_deep(
        node=tree,
        after=lambda context, path, indexed_path: append_if_str(context, lst),
    )
    return lst


def diff_str(base_node: str, compare_node: str):
    # return 100 if base_node == compare_node else 0
    """
    Where T is the total number of elements in both sequences,
    and M is the number of matches,
    this is 2.0*M / T.
    Note that this is 1.0 if the sequences are identical,
    and 0.0 if they have nothing in common.
    """
    return SequenceMatcher(
        None,
        base_node,
        compare_node,
        False,
    ).quick_ratio()


def diff_score(base_node, compare_node):
    base = base_node["node"]
    compare = compare_node["node"]
    if isinstance(base, str) and isinstance(compare, str):
        return diff_str(base, compare)
    return 0.0


def ngrams(text, n):
    return (
        Counter({text: 1})
        if n == 0
        else Counter([text[i : i + n] for i in range(0, len(text) - n + 1)])
    )


def add_ngrams(arr, ngram_len, ngram_to_string, string_to_ngram):
    for val in arr:
        if isinstance(val, str):
            counts = string_to_ngram.setdefault(
                val,
                {"ngrams": ngrams(val, ngram_len), "i_match": set(), "match_me": set()},
            )["ngrams"]
            for ngram, count in counts.items():
                ngram_to_string[ngram].update({val: count})


def find_closest_matches(text, base_ngram_to_string, string_to_ngram):
    compare_counts = string_to_ngram[text]["ngrams"]
    scores = Counter()
    for compare_ngram, compare_count in compare_counts.items():
        for base_string, base_count in base_ngram_to_string[compare_ngram].items():
            scores.update({base_string: min(compare_count, base_count)})
    if len(scores) > 0:
        top = scores.most_common()
        top = [t for t, count in top if count == top[0][1]]
        top = sorted(top, key=len)
        top = [t for t in top if len(t) == len(top[0])]
        string_to_ngram[text]["i_match"].update(top)
        for t in top:
            string_to_ngram[t]["match_me"].add(text)


def remove(lst, string_to_ngram, item):
    lst.remove(item)
    for match_me in string_to_ngram.get(item, {}).get("match_me", set()):
        string_to_ngram.get(match_me, {}).get("i_match", set()).discard(item)
    string_to_ngram.pop(item, None)


def intersections(string_to_ngram, base, compare, pairs, ngram_len):
    for base_item in list(base):
        compare_items = string_to_ngram[base_item]["i_match"]
        if len(compare_items) > 0:
            compare_items_that_have_base = []
            compare_item_only_has_base = False
            for compare_item in compare_items:
                base_items = string_to_ngram[compare_item]["i_match"]
                if base_item in base_items:
                    compare_items_that_have_base.append(compare_item)
                    if len(base_items) == 1:
                        compare_item_only_has_base = True
            if compare_item_only_has_base and len(compare_items_that_have_base) == 1:
                compare_item = compare_items_that_have_base[0]
                pairs.append(
                    (
                        base_item,
                        compare_item,
                        #  "ngram_len": ngram_len
                    )
                )
                remove(base, string_to_ngram, base_item)
                remove(compare, string_to_ngram, compare_item)


def _pair_arrays(base, compare, pairs, ngram_len, steps):
    print(f"==========={steps}============")
    print(f"Ngram, Base, Compare, Pairs")
    print("Start")
    print(f"{ngram_len}, {len(base)}, {len(compare)}, {len(pairs)}")
    string_to_ngram = {}
    base_ngram_to_string = defaultdict(lambda: Counter())
    compare_ngram_to_string = defaultdict(lambda: Counter())
    add_ngrams(base, ngram_len, base_ngram_to_string, string_to_ngram)
    add_ngrams(compare, ngram_len, compare_ngram_to_string, string_to_ngram)
    for c in compare:
        find_closest_matches(c, base_ngram_to_string, string_to_ngram)
    for b in base:
        find_closest_matches(b, compare_ngram_to_string, string_to_ngram)
    intersections(string_to_ngram, base, compare, pairs, ngram_len)
    intersections(string_to_ngram, compare, base, pairs, ngram_len)
    print("End")
    print(f"{ngram_len}, {len(base)}, {len(compare)}, {len(pairs)}")


def max_len(base, compare):
    return max(len(text) for text in [*base, *compare]) if base or compare else 0


def decrement(num):
    return int(num / 2) if num > 16 else num - 1


def pair_arrays(base, compare):
    pairs = []
    steps = 1
    _pair_arrays(base, compare, pairs, 0, steps)
    ngram_length = decrement(max_len(base, compare))
    while ngram_length > 0 and base and compare:
        steps += 1
        pairs_length = len(pairs)
        _pair_arrays(base, compare, pairs, ngram_length, steps)
        if pairs_length == len(pairs):
            ngram_length = decrement(min(ngram_length, max_len(base, compare)))
    return pairs


def pair_arrays_quick_ratio(base, compare):
    for base_node, compare_node in product(base, compare):
        if isinstance(base_node, str) and isinstance(compare_node, str):
            diff_str(base_node, compare_node)
    return ""


def diff_scores(base, compare):
    base_nodes = post_order_list(base)
    compare_nodes = post_order_list(compare)
    node_levels = defaultdict(lambda: {"base_nodes": [], "compare_nodes": []})
    for base_node in base_nodes:
        node_levels[base_node["path"]]["base_nodes"].append(base_node)
    for compare_node in compare_nodes:
        node_levels[compare_node["path"]]["compare_nodes"].append(compare_node)
    scores = defaultdict(lambda: [])
    for path, level in node_levels.items():
        for base_node, compare_node in product(
            level["base_nodes"], level["compare_nodes"]
        ):
            scores[path].append(
                {
                    "base_node": base_node,
                    "compare_node": compare_node,
                    "score": diff_score(base_node, compare_node),
                }
            )
    for level in node_levels.values():
        for node in level["base_nodes"] + level["compare_nodes"]:
            del node["node"]
    return scores


def diff_scalar(base, compare, base_pointer, compare_pointer):
    if base != compare:
        return [
            {
                "base_pointer": base_pointer,
                "compare_pointer": compare_pointer,
                "op": "replace",
                "base": base,
                "value": compare,
            },
            *(
                []
                if base_pointer == compare_pointer
                else [{"from": base_pointer, "path": compare_pointer, "op": "move"}]
            ),
        ]
    return []


def stringify(json_list):
    return {
        dumps(item, sort_keys=True, separators=(",", ":")): (index, item)
        for (index, item) in enumerate(json_list)
    }


def diff_array(base, compare, base_pointer, compare_pointer):
    json_to_base = stringify(base)
    json_to_compare = stringify(compare)
    json_base = set(json_to_base.keys())
    json_compare = set(json_to_compare.keys())
    pairs = pair_arrays(json_base, json_compare)
    deletions = [
        {
            "base_pointer": f"{base_pointer}/{json_to_base[item][0]}",
            "compare_pointer": f"{compare_pointer}",
            "op": "remove",
        }
        for item in json_base
    ]
    additions = [
        {
            "base_pointer": f"{base_pointer}",
            "compare_pointer": f"{compare_pointer}/{json_to_compare[item][0]}",
            "op": "add",
        }
        for item in json_compare
    ]
    updates = []
    for base, comp in pairs:
        updates.extend(
            diff_value(
                json_to_base[base][1],
                json_to_compare[comp][1],
                f"{base_pointer}/{json_to_base[base][0]}",
                f"{compare_pointer}/{json_to_compare[comp][0]}",
            )
        )
    return deletions + additions + updates


def diff_value(base, compare, base_pointer, compare_pointer):
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
        return diff_obj(base, compare, base_pointer, compare_pointer)
    if type(base) in arrays and type(compare) in arrays:
        return diff_array(base, compare, base_pointer, compare_pointer)


def diff_obj(base, compare, base_pointer="", compare_pointer=""):
    deletions = [
        {
            "base_pointer": f"{base_pointer}/{k}",
            "compare_pointer": f"{compare_pointer}/{k}",
            "op": "remove",
        }
        for k in set(base.keys()) - set(compare.keys())
    ]
    additions = [
        {
            "base_pointer": f"{base_pointer}/{k}",
            "compare_pointer": f"{compare_pointer}/{k}",
            "op": "add",
        }
        for k in set(compare.keys()) - set(base.keys())
    ]
    updates = []
    for k in set(base.keys()) & set(compare.keys()):
        updates.extend(
            diff_value(
                base[k],
                compare[k],
                f"{base_pointer}/{k}",
                f"{compare_pointer}/{k}",
            )
        )
    return deletions + additions + updates
