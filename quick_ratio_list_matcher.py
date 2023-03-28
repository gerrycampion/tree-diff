from each_deep import each_deep
from itertools import product
from difflib import SequenceMatcher
from collections import defaultdict
from base_list_matcher import BaseListMatcher


def _post_order_list(tree):
    lst = []
    each_deep(
        node=tree,
        after=lambda context, path, indexed_path: lst.append(
            {"node": context[-1], "path": path, "indexed_path": indexed_path}
        ),
    )
    return lst


def _append_if_str(context, lst):
    if isinstance(context[-1], str):
        lst.append(context[-1])


def _all_values(tree):
    lst = []
    each_deep(
        node=tree,
        after=lambda context, path, indexed_path: _append_if_str(context, lst),
    )
    return lst


def _diff_score(base_node, compare_node):
    base = base_node["node"]
    compare = compare_node["node"]
    if isinstance(base, str) and isinstance(compare, str):
        return _diff_str(base, compare)
    return 0.0


def _diff_scores(base, compare):
    base_nodes = _post_order_list(base)
    compare_nodes = _post_order_list(compare)
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
                    "score": _diff_score(base_node, compare_node),
                }
            )
    for level in node_levels.values():
        for node in level["base_nodes"] + level["compare_nodes"]:
            del node["node"]
    return scores


def _diff_str(base_node: str, compare_node: str):
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


class QRListMatcher(BaseListMatcher):
    def match_lists(base, compare):
        scores = []
        for base_node, compare_node in product(base, compare):
            score = _diff_str(base_node, compare_node)
            scores.append({"score": score, "base": base_node, "comp": compare_node})
        pairs = []
        for score in sorted(scores, key=lambda score: score["score"], reverse=True):
            if score["base"] in base and score["comp"] in compare:
                pairs.append((score["base"], score["comp"]))
                base.remove(score["base"])
                compare.remove(score["comp"])
        return pairs
