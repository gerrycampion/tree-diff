import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tree_diff.diff_json import DiffNode, diff_value
from tree_diff.ngram_list_matcher import NgramListMatcher

SAMPLES_DIR = Path(__file__).resolve().parents[1] / "samples"


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sorted_diffs(diffs):
    return sorted(
        diffs,
        key=lambda diff: json.dumps(diff, sort_keys=True, separators=(",", ":")),
    )


def test_generated_diff_matches_sample_output_files():
    base = _load_json(SAMPLES_DIR / "base.json")
    compare = _load_json(SAMPLES_DIR / "compare.json")

    generated = _sorted_diffs(
        diff_value(NgramListMatcher, DiffNode(base, compare)),
    )

    expected_paths = _load_json(SAMPLES_DIR / "diff_paths.json")
    expected_summary = _load_json(SAMPLES_DIR / "diff_summary.json")
    expected_detailed = _load_json(SAMPLES_DIR / "diff_detailed.json")

    path_only = [
        {key: diff[key] for key in ("op", "path_base", "path_compare")}
        for diff in generated
    ]

    assert path_only == expected_paths
    assert path_only == expected_summary
    assert generated == expected_detailed
