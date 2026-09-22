from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from difflib import SequenceMatcher
from itertools import product
from typing import Any

from tree_diff.base_list_matcher import BaseListMatcher
from tree_diff.each_deep import each_deep


def _post_order_list(tree: Any) -> list[dict[str, Any]]:
    lst: list[dict[str, Any]] = []
    each_deep(
        node=tree,
        after=lambda context, path, indexed_path: lst.append(
            {"node": context[-1], "path": path, "indexed_path": indexed_path}
        ),
    )
    return lst


def _append_if_str(context: list[Any], lst: list[str]) -> None:
    if isinstance(context[-1], str):
        lst.append(context[-1])


def _all_values(tree: Any) -> list[str]:
    lst: list[str] = []
    each_deep(
        node=tree,
        after=lambda context, path, indexed_path: _append_if_str(context, lst),
    )
    return lst


def _diff_score(base_node: dict[str, Any], compare_node: dict[str, Any]) -> float:
    base = base_node["node"]
    compare = compare_node["node"]
    if isinstance(base, str) and isinstance(compare, str):
        return _diff_str(base, compare)
    return 0.0


def _diff_scores(base: Any, compare: Any) -> dict[str, list[dict[str, Any]]]:
    base_nodes = _post_order_list(base)
    compare_nodes = _post_order_list(compare)
    node_levels: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: {"base_nodes": [], "compare_nodes": []}
    )
    for base_node in base_nodes:
        node_levels[base_node["path"]]["base_nodes"].append(base_node)
    for compare_node in compare_nodes:
        node_levels[compare_node["path"]]["compare_nodes"].append(compare_node)
    scores: dict[str, list[dict[str, Any]]] = defaultdict(list)
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


def _diff_str(base_node: str, compare_node: str) -> float:
    return SequenceMatcher(
        None,
        base_node,
        compare_node,
        False,
    ).quick_ratio()


class QRListMatcher(BaseListMatcher[str]):
    @staticmethod
    def match_lists(
        base: Iterable[str], compare: Iterable[str]
    ) -> list[tuple[str, str]]:
        base_list = list(base)
        compare_list = list(compare)
        scores: list[dict[str, Any]] = []
        for base_node, compare_node in product(base_list, compare_list):
            score = _diff_str(base_node, compare_node)
            scores.append({"score": score, "base": base_node, "comp": compare_node})
        pairs: list[tuple[str, str]] = []
        for score in sorted(scores, key=lambda score: score["score"], reverse=True):
            if score["base"] in base_list and score["comp"] in compare_list:
                pairs.append((score["base"], score["comp"]))
                base_list.remove(score["base"])
                compare_list.remove(score["comp"])
        return pairs
