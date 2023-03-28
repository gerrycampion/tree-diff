from json_loader import load_from_file, save_to_file
from ngram_list_matcher import NgramListMatcher
from quick_ratio_list_matcher import QRListMatcher
from diff_json import (
    diff_obj,
)
from json import dumps

base_filename = "C:/Users/GerryCampion/Code/cdisc-library-src-files/cdisc-json/products/data-tabulation/sdtm-1-8.json"
compare_filename = "C:/Users/GerryCampion/Code/cdisc-library-src-files/cdisc-json/products/data-tabulation/sdtm-2-0.json"
out_dir = "./out/"

base = load_from_file(base_filename)
compare = load_from_file(compare_filename)

diffs = sorted(
    diff_obj(QRListMatcher, base, compare),
    key=lambda diff: dumps(diff, sort_keys=True, separators=(",", ":")),
)

save_to_file(
    {"diffs": diffs},
    f"{out_dir}diffs.json",
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
