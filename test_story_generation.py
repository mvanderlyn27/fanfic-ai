from app.models.story import StoryInput, Character, RelationshipStructure, POVType, Ending
from app.story_service import StoryService
import asyncio

async def test_story_generation():
    # Create main characters
    main_characters = [
        Character(
            name="Emma Chen",
            age=28,
            gender="Female",
            occupation="Software Engineer",
            brief_backstory="Dedicated programmer who's been focused on her career, leaving little time for romance",
            personality="Analytical, introverted, but warmhearted",
            internal_conflict_flaw="Struggles with work-life balance and opening up to others",
            external_conflict_goal="Finding love while maintaining her career aspirations",
            pov_character=True
        ),
        Character(
            name="James Martinez",
            age=32,
            gender="Male",
            occupation="Coffee Shop Owner",
            brief_backstory="Former corporate worker who quit to pursue his passion for coffee and community",
            personality="Extroverted, compassionate, and creative",
            internal_conflict_flaw="Fear of failure and returning to corporate life",
            external_conflict_goal="Growing his business while nurturing a new relationship",
            pov_character=False
        )
    ]

    # Create story input
    story_input = StoryInput(
        genre="Contemporary Romance",
        target_audience="Young Adult",
        setting="Seattle, Washington - A bustling tech hub with a vibrant coffee culture",
        cover_art_description="A cozy coffee shop window on a rainy Seattle day, with two people's silhouettes visible inside",
        main_characters=main_characters,
        relationship_structure=RelationshipStructure.MONOGAMOUS,
        supporting_characters="Sarah (Emma's best friend and fellow developer), Mike (James's barista)",
        plot_summary="A workaholic software engineer finds unexpected love with a coffee shop owner who teaches her the importance of work-life balance",
        themes=["Work-Life Balance", "Taking Chances", "Finding Community"],
        tropes=["Meet Cute", "Opposites Attract", "Career vs. Love"],
        conflict="Internal struggles with work-life balance and fear of failure, while external pressures from career demands test their growing relationship",
        heat_level="Sweet",
        pov=POVType.THIRD_PERSON_LIMITED,
        ending=Ending.HEA,
        approximate_chapters=5,
        chapter_length_range=[2000, 3000]
    )

    # Initialize story service
    story_service = StoryService()

    # Generate story
    try:
        story_file_path = await story_service.generate_story(story_input)
        print(f"Story generated successfully! File path: {story_file_path}")
    except Exception as e:
        print(f"Error generating story: {str(e)}")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_story_generation())