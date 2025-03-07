from typing import List, Dict
from pydantic import BaseModel

class StoryContext(BaseModel):
    active_arcs: List[str]
    key_plot_points: List[str]
    character_states: Dict[str, Dict[str, str]]
    current_chapter: int
    total_chapters: int