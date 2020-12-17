from typing import List

from .back import Layout


def filter_layout(layout: Layout, include: List[str]) -> Layout:
    new_layout: Layout = {**layout}  # type: ignore
    new_actions = [a for a in layout['boss_actions'] if a['name'] in include]
    new_layout['boss_actions'] = new_actions
    return new_layout
