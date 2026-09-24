# tree-diff-py

Utilities for diffing nested JSON-like structures and matching list items.

## Installation

```bash
pip install tree-diff-py
```

## Development

```bash
python -m pip install -U pip
python -m pip install -e ".[dev]"
pre-commit install
```

## Example

```python
from diff_json import DiffNode, diff_obj
from ngram_list_matcher import NgramListMatcher

# compare nested structures using the matcher of your choice
# diffs = diff_obj(NgramListMatcher, DiffNode(base, compare))
```
