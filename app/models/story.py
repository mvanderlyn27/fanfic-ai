from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from .enums import Gender, POVType, RelationshipStructure, Ending

class Character(BaseModel):
    name: str
    age: int
    gender: Gender
    occupation: str
    brief_backstory: str
    personality: str
    internal_conflict_flaw: str
    external_conflict_goal: str
    pov_character: bool

class Scene(BaseModel):
    scene_number: int
    setting: str
    characters_present: List[str]
    action: str
    emotional_cues: str
    pov_character: str
    plot_progression: str
    character_development: str
    desires_and_fears: str
    nsfw: bool

class Chapter(BaseModel):
    chapter_number: int
    title: str
    pov_character: str
    summary: str
    scenes: List[Scene]
    themes_explored: List[str]
    foreshadowing: str
    symbolism: str
    cliffhanger: str

class StoryInput(BaseModel):
    genre: str
    target_audience: str
    setting: str
    cover_art_description: str
    main_characters: List[Character]
    relationship_structure: RelationshipStructure
    supporting_characters: str
    plot_summary: str
    themes: List[str]
    tropes: List[str]
    conflict: str
    heat_level: str
    pov: POVType
    ending: Ending
    approximate_chapters: int
    chapter_length_range: List[int] = Field(..., min_items=2, max_items=2)
    special_requests: Optional[str] = None
class CharacterDevelopment(BaseModel):
    character_name: str
    emotional_state: str
    development: str

class ChapterContent(BaseModel):
    content: str
    themes_explored: List[str]
    character_developments: List[CharacterDevelopment]
    plot_progressions: List[str]
    unresolved_threads: List[str]
    resolved_threads: List[str]
    chapter_number: int