# tree-diff-py

Utilities for diffing nested JSON-like structures and matching list items.

## Installation

```bash
pip install tree-diff-py
```

## Development

```bash
python -m pip install --upgrade pip
python -m pip install --editable ".[dev]"
pre-commit install
```

## How it works

The library takes a recursive approach to diffing JSON-like data structures.

### 1. Recursive value diffing

The main algorithm walks the base and compares values in parallel. It handles:

- scalar values like strings, numbers, booleans, and nulls
- object keys and nested object paths
- arrays and list items

When the values are the same type, it compares them recursively. If the type changes or the scalar value changes, it records a replace operation with the source and target paths.

For example:

```json
{
  "status": "draft"
}
```

versus

```json
{
  "status": "published"
}
```

produces:

```json
[
  {
    "op": "replace",
    "path_base": "/status",
    "path_compare": "/status",
    "value_base": "draft",
    "value_compare": "published"
  }
]
```

### 2. Object-level changes

Object diffs are produced by comparing keys. A key that exists only in the base is treated as a remove. A key that exists only in the compare is treated as an add. Shared keys keep descending into the nested values.

Example:

```json
{
  "owner": { "name": "Alex", "team": "platform" }
}
```

versus

```json
{
  "owner": { "name": "Alex", "team": "platform-ops" }
}
```

yields a replace on `/owner/team`.

### 3. Array matching with n-gram similarity

The key challenge is list comparison. Arrays are frequently reordered, and a naive diff would mark every item as removed and re-added. This project uses an n-gram based matcher to find the closest matching items even when list order changes.

The matcher:

- converts each item into a string representation
- builds n-grams from those strings
- compares n-gram overlap across base and compare lists
- picks the strongest candidate matches
- resolves one-to-one item pairing before generating move or replace operations

This makes it good at detecting changes like:

- reordered tags or teams
- similar feature entries with updated metadata
- same item moved to a different index with small changes

Example:

```json
[
  "urgent",
  "backend",
  "release",
  "api"
]
```

versus

```json
[
  "backend",
  "release",
  "urgent",
  "api",
  "security"
]
```

The diff records list moves and the added item `"security"` instead of treating the entire array as completely different.

### 4. Example from the sample data

The sample files in `samples/base.json` and `samples/compare.json` demonstrate several common cases:

- scalar change: `status` from `draft` to `published`
- nested field change: `owner.team` from `platform` to `platform-ops`
- moved list items: `tags` and `teams` are reordered
- matched object updates: `search` and `billing` entries are paired by similarity even when indices shift
- added item: `security` appears in the compare list
- removed item: a nested feature appears in the base but not in the compare

A typical output looks like:

```json
[
  {"op": "move", "path_base": "/tags/0", "path_compare": "/tags/2"},
  {"op": "move", "path_base": "/features/1", "path_compare": "/features/2"},
  {"op": "replace", "path_base": "/status", "path_compare": "/status"},
  {"op": "add", "path_base": "/tags", "path_compare": "/tags/4"}
]
```

## Example usage

```python
import json
from pathlib import Path

from tree_diff.diff_json import DiffNode, diff_value
from tree_diff.ngram_list_matcher import NgramListMatcher

base = json.loads(Path("samples/base.json").read_text())
compare = json.loads(Path("samples/compare.json").read_text())

diffs = diff_value(NgramListMatcher, DiffNode(base, compare))
print(diffs)
```

This will return a sequence of diff records describing the semantic changes between the two JSON structures.
