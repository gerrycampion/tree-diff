import os
from os.path import join
from json import dumps
from typing import Any

from tree_diff.diff_json import DiffNode, diff_obj
from tree_diff.json_loader import load_from_file, save_to_file
from tree_diff.ngram_list_matcher import NgramListMatcher

base_filename: str = os.environ.get("BASE_FILENAME", "")
compare_filename: str = os.environ.get("COMPARE_FILENAME", "")
output_directory: str = os.environ.get("OUTPUT_DIRECTORY", "")

if not base_filename or not compare_filename or not output_directory:
    raise ValueError(
        "Set BASE_FILENAME, COMPARE_FILENAME, and OUTPUT_DIRECTORY in .env or the environment."
    )

base: Any = load_from_file(base_filename)
compare: Any = load_from_file(compare_filename)

diffs: list[dict[str, Any]] = sorted(
    diff_obj(NgramListMatcher, DiffNode(base, compare)),
    key=lambda diff: dumps(diff, sort_keys=True, separators=(",", ":")),
)


save_to_file(
    diffs,
    join(output_directory, "diff_paths.json"),
    keep=["diffs", "op", "path_base", "path_compare"],
)
save_to_file(
    diffs,
    join(output_directory, "diff_summary.json"),
    keep=["diffs", "op", "path_base", "path_compare"],
)
save_to_file(
    diffs,
    join(output_directory, "diff_detailed.json"),
    keep=["diffs", "op", "path_base", "path_compare", "value_base", "value_compare"],
)


# base_values = set(all_values(base))
# compare_values = set(all_values(compare))
# pairs = pair_arrays(base_values, compare_values)

# save_to_file(
#     {
#         "pairs": sorted(
#             [pair for pair in pairs if pair[0] != pair[1]],
#             key=lambda pair: pair[0],
#         ),
#         "base": sorted([*base_values]),
#         "comp": sorted([*compare_values]),
#     },
#     f"{out_dir}pairs_halves.json",
# )


# 3055, 61-3072, 68-3081, 63-3081, 59-3112

# scores = diff_scores(base, compare)
# save_to_file(scores, f"{out_dir}out.json")


# pair_arrays_quick_ratio(base_values, compare_values)
