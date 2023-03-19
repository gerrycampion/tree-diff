from json_loader import load_from_file, save_to_file
from diff_score import (
    diff_scores,
    ngrams,
    all_values,
    pair_arrays,
    pair_arrays_quick_ratio,
)

# fast fourier transforms?
# gale-shapely algo?

base_filename = "C:/Users/GerryCampion/Code/cdisc-library-src-files/cdisc-json/products/data-tabulation/sdtm-1-8.json"
compare_filename = "C:/Users/GerryCampion/Code/cdisc-library-src-files/cdisc-json/products/data-tabulation/sdtm-2-0.json"
out_dir = "./out/"

base = load_from_file(base_filename)
compare = load_from_file(compare_filename)

base_values = set(all_values(base))
compare_values = set(all_values(compare))
pairs = pair_arrays(base_values, compare_values)

# 3055, 61-3072, 68-3081, 63-3081

# scores = diff_scores(base, compare)
# save_to_file(scores, f"{out_dir}out.json")

save_to_file(
    {
        "pairs": sorted(
            [pair for pair in pairs if pair["base"] != pair["comp"]],
            key=lambda pair: pair["base"],
        ),
        "base": sorted([*base_values]),
        "comp": sorted([*compare_values]),
    },
    f"{out_dir}pairs_halves.json",
)

# pair_arrays_quick_ratio(base_values, compare_values)
