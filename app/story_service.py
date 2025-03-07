from pathlib import Path
from typing import Dict, List, Optional
from .models.story import StoryInput, Chapter, Scene, ChapterContent
from .models.context import StoryContext
import json
import time
import logging
import os
from dotenv import load_dotenv
from .models.exceptions import StoryServiceError, TemplateError, ModelError, ContentGenerationError
from google import genai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize Gemini model
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError('GEMINI_API_KEY environment variable is not set')
MODEL="gemini-2.0-flash"
client = genai.Client(api_key=api_key)
# model = genai.GenerativeModel('gemini-2.0-flash')
# nsfw_model = genai.GenerativeModel('gemini-2.0-flash')  # Configure with different safety settings


logger = logging.getLogger(__name__)
class StoryService:
    def __init__(self):
        try:
            self.template_dir = Path(__file__).parent / 'templates'
            self.output_dir = Path(__file__).parent / 'output'
            self.output_dir.mkdir(exist_ok=True)
            
            if not self.template_dir.exists():
                raise TemplateError(f"Template directory not found at {self.template_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize StoryService: {str(e)}")
            raise StoryServiceError(f"Service initialization failed: {str(e)}")

    def _load_template(self, template_name: str) -> str:
        try:
            template_path = self.template_dir / template_name
            if not template_path.exists():
                raise TemplateError(f"Template file not found: {template_name}")
            return template_path.read_text()
        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {str(e)}")
            raise TemplateError(f"Failed to load template {template_name}: {str(e)}")

    async def _generate_input(self, story_input: StoryInput) -> StoryInput:
        try:
            if not story_input:
                raise ValueError("Story input cannot be empty")
            template = self._load_template('generate_input_prompt.txt')
            story_details = {
                "Genre": story_input.genre,
                "Target Audience": story_input.target_audience,
                "Setting": story_input.setting,
                "Cover Art Description": story_input.cover_art_description,
                "Main Characters": [
                    {
                        "Name": char.name,
                        "Age": char.age,
                        "Gender": char.gender,
                        "Occupation": char.occupation,
                        "Brief Backstory": char.brief_backstory,
                        "Personality": char.personality,
                        "Internal Conflict/Flaw": char.internal_conflict_flaw,
                        "External Conflict/Goal": char.external_conflict_goal,
                        "POV Character": char.pov_character
                    } for char in story_input.main_characters
                ],
                "Relationship Structure": story_input.relationship_structure,
                "Supporting Characters": story_input.supporting_characters,
                "Plot Summary": story_input.plot_summary,
                "Themes": story_input.themes,
                "Tropes": story_input.tropes,
                "Conflict": story_input.conflict,
                "Heat Level": story_input.heat_level,
                "POV": story_input.pov,
                "Ending": story_input.ending,
                "Approximate Number of Chapters": story_input.approximate_chapters
            }
            
            try:
                formatted_details = json.dumps(story_details, indent=2)
                prompt = template.replace('{special_generation_info}', formatted_details)
                
                # Generate content using the model
                response = client.models.generate_content(model=MODEL, contents=prompt,config={
        'response_mime_type': 'application/json',
        'response_schema': StoryInput,
    })
                if not response or not response.text:
                    raise ModelError("Empty response from model")
                
                # Clean up the response text to ensure valid JSON
                return response.parsed 
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse model response: {str(e)}")
                raise ContentGenerationError(f"Invalid JSON in model response: {str(e)}")
            except ValueError as e:
                logger.error(f"Failed to create StoryInput from response: {str(e)}")
                raise ContentGenerationError(f"Failed to create StoryInput: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error in _generate_input: {str(e)}")
            raise ContentGenerationError(f"Failed to generate input: {str(e)}")

    async def _generate_chapter_overview(self, story_input: StoryInput, context: StoryContext,
                                batch_start: int, batch_size: int = 5) -> List[Chapter]:
        try:
            template = self._load_template('structure_prompt.txt')
            
            story_details = {
                "genre": story_input.genre,
                "target_audience": story_input.target_audience,
                "setting": story_input.setting,
                "main_characters": [
                    {
                        "name": char.name,
                        "age": char.age,
                        "gender": char.gender,
                        "occupation": char.occupation,
                        "personality": char.personality,
                        "internal_conflict": char.internal_conflict_flaw,
                        "external_goal": char.external_conflict_goal,
                        "pov_character": char.pov_character
                    } for char in story_input.main_characters
                ],
                "relationship_structure": story_input.relationship_structure,
                "plot_summary": story_input.plot_summary,
                "themes": story_input.themes,
                "tropes": story_input.tropes,
                "conflict": story_input.conflict,
                "heat_level": story_input.heat_level,
                "pov_type": story_input.pov,
                "ending_type": story_input.ending,
                "batch_context": {
                    "current_chapter": batch_start,
                    "batch_size": batch_size,
                    "active_arcs": context.active_arcs,
                    "key_plot_points": context.key_plot_points,
                    "character_states": context.character_states
                }
            }
            
            formatted_details = json.dumps(story_details, indent=2)
            formatted_prompt = template.replace('{story_details}', formatted_details)
            
            try:
                response = client.models.generate_content(model=MODEL, contents=formatted_prompt, config={
        'response_mime_type': 'application/json',
        'response_schema': list[Chapter],
    })
                if not response or not response.text:
                    raise ModelError("Empty response from model")
                
               
                chapters_data = response.parsed 
                if not isinstance(chapters_data, list):
                    raise ContentGenerationError("Expected JSON array for chapters data")
                
                return chapters_data 
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse chapters data: {str(e)}\nResponse: {response.text}")
                raise ContentGenerationError(f"Invalid JSON in model response: {str(e)}")
            except Exception as e:
                logger.error(f"Error processing chapters data: {str(e)}\nResponse: {response.text if 'response' in locals() else 'No response'}")
                raise ContentGenerationError(f"Failed to process chapter data: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in chapter overview generation: {str(e)}")
            raise ContentGenerationError(f"Failed to generate chapter overview: {str(e)}")

    async def _generate_chapter_content(self, chapter: Chapter, story_input: StoryInput,
                               context: StoryContext) -> ChapterContent:
        try:
            if not chapter or not chapter.scenes:
                raise ValueError("Chapter or scenes cannot be empty")
            
            template = self._load_template('chapter_prompt.txt')
            chapter_details = {
                "chapter_number": chapter.chapter_number,
                "chapter_title": chapter.title,
                "scenes": [
                    {
                        "scene_number": scene.scene_number,
    "setting": scene.setting,
    "characters_present": scene.characters_present,
    "action": scene.action,
    "emotional_cues": scene.emotional_cues,
    "pov_character": scene.pov_character,
    "plot_progression": scene.plot_progression,
    "character_development": scene.character_development,
    "desires_and_fears": scene.desires_and_fears,
    "nsfw": scene.nsfw
                    } for scene in chapter.scenes
                ],
                "story_context": {
                    "genre": story_input.genre,
                    "heat_level": story_input.heat_level,
                    "pov_type": story_input.pov,
                    "active_arcs": context.active_arcs,
                    "character_states": context.character_states
                }
            }
            
            formatted_details = json.dumps(chapter_details, indent=2)
            formatted_prompt = template.replace('{chapter_details}', formatted_details)
            
            try:
                response = client.models.generate_content(model=MODEL,contents=formatted_prompt,config={
        'response_mime_type': 'application/json',
        'response_schema': ChapterContent,
    },)
                if not response or not response.text:
                    raise ModelError("Empty response from model")
                
                return response.parsed
                
            except Exception as e:
                logger.error(f"Error generating chapter content: {str(e)}")
                raise ContentGenerationError(f"Failed to generate chapter content: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in chapter content generation: {str(e)}")
            raise ContentGenerationError(f"Failed to generate chapter content: {str(e)}")

    async def _handle_nsfw_scene(self, scene: Scene, story_input: StoryInput,
                         context: StoryContext) -> str:
        try:
            if not scene:
                raise ValueError("Invalid scene data: Scene is missing")

            nsfw_scene_details = {
                'setting': scene.setting,
                'characters': scene.characters_present,
                'emotional_state': scene.emotional_cues,
                'plot_context': scene.plot_progression,
                'character_development': scene.character_development,
                'desires_and_fears': scene.desires_and_fears,
                'heat_level': story_input.heat_level,
                'relationship_structure': story_input.relationship_structure,
                'character_states': {name: state for name, state in context.character_states.items()
                                   if name in scene.characters_present}
            }
            
            try:
                print("NSFW MODEL")
                response = "" 
                if not response or not response.text:
                    raise ModelError("Empty response from model for NSFW scene")
                return response
            except Exception as e:
                logger.error(f"Error generating NSFW content: {str(e)}")
                raise ModelError(f"Failed to generate NSFW content: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in NSFW scene generation: {str(e)}")
            raise ContentGenerationError(f"Failed to generate NSFW scene: {str(e)}")

    def _update_context(self, context: StoryContext, chapter_content: ChapterContent):
        try:
            if not context or not chapter_content:
                raise ValueError("Invalid input: Context or chapter content is missing")

            # Update character states based on character developments
            if chapter_content.character_developments:
                for char_dev in chapter_content.character_developments:
                    if char_dev.character_name in context.character_states:
                        context.character_states[char_dev.character_name]["mental_state"] = char_dev.emotional_state
                        
                        # Add character development to active arcs if significant
                        if char_dev.development:
                            arc = f"Character Arc: {char_dev.character_name} - {char_dev.development}"
                            if arc not in context.active_arcs:
                                context.active_arcs.append(arc)

            # Update plot points and story arcs
            if chapter_content.plot_progressions:
                context.key_plot_points.extend(chapter_content.plot_progressions)

            # Add new themes to active arcs
            if chapter_content.themes_explored:
                for theme in chapter_content.themes_explored:
                    if theme not in context.active_arcs:
                        context.active_arcs.append(theme)

            # Remove resolved plot threads from active arcs
            if chapter_content.resolved_threads:
                for resolved in chapter_content.resolved_threads:
                    if resolved in context.active_arcs:
                        context.active_arcs.remove(resolved)

            # Ensure unresolved threads are in active arcs
            if chapter_content.unresolved_threads:
                for unresolved in chapter_content.unresolved_threads:
                    if unresolved not in context.active_arcs:
                        context.active_arcs.append(unresolved)

            context.current_chapter += 1
            
        except Exception as e:
            logger.error(f"Error updating context: {str(e)}")
            raise StoryServiceError(f"Failed to update story context: {str(e)}")

    async def generate_story(self, story_input: StoryInput) -> str:
        try:
            # Generate initial story prompt and structure
            story_prompt = await self._generate_input(story_input)
            print("story_prompt") 
            # Initialize story context
            context = StoryContext(
                current_chapter=0,
                active_arcs=[],
                key_plot_points=[],
                total_chapters=story_prompt.approximate_chapters,
                character_states={char.name: {"mental_state": "neutral", "health": "100"} 
                                for char in story_input.main_characters}
            )
            
            # Generate initial story structure
            chapters = []
            batch_size = 5
            # chapter_length = story_prompt.approximate_chapters
            chapter_length = 5 
            for batch_start in range(0, chapter_length, batch_size):
                batch_chapters = await self._generate_chapter_overview(
                    story_prompt, context, batch_start, batch_size
                )
                chapters.extend(batch_chapters)
            
            # Generate full story content
            print(chapters)
            story_content = []
            for chapter in chapters:
                # Generate chapter content
                chapter_content = await self._generate_chapter_content(chapter, story_input, context)
                story_content.append(chapter_content.content)
                
                # Update story context
                self._update_context(context, chapter_content)
            
            # Save story to file
            timestamp = int(time.time())
            story_file_path = self.output_dir / f"story_{timestamp}.txt"
            story_text = "\n\n".join(story_content)
            story_file_path.write_text(story_text)
            
            return str(story_file_path)
            
        except Exception as e:
            logger.error(f"Error generating story: {str(e)}")
            raise ContentGenerationError(f"Failed to generate story: {str(e)}")