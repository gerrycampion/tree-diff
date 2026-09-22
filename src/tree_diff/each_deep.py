from collections.abc import Callable, Iterable, Mapping
from typing import Any

BeforeAfter = Callable[[list[Any], str, str], None]


def _each_deep(
    context: list[Any],
    before: BeforeAfter = lambda c, p, ip: None,
    after: BeforeAfter = lambda c, p, ip: None,
    path: str = "",
    indexed_path: str = "",
) -> None:
    node = context[-1]
    before(context, path, indexed_path)
    if isinstance(node, Mapping):
        for key, value in node.items():
            _each_deep(
                context=context + [value],
                before=before,
                after=after,
                path=path + "/" + str(key),
                indexed_path=indexed_path + "/" + str(key),
            )
    elif isinstance(node, Iterable) and not isinstance(node, str):
        for key, value in enumerate(node):
            _each_deep(
                context=context + [value],
                before=before,
                after=after,
                path=path,
                indexed_path=indexed_path + "/" + str(key),
            )
    after(context, path, indexed_path)


def each_deep(
    node: Any,
    before: BeforeAfter = lambda c, p, ip: None,
    after: BeforeAfter = lambda c, p, ip: None,
) -> Any:
    _each_deep(context=[node], before=before, after=after)
    return node
