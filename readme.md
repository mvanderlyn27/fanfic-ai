# Goal

- Create an api that takes in a json containing
  - Genre (e.g., Contemporary Romance, Historical Romance, Paranormal Romance)
  - Target Audience (detailed description of target demographic)
  - Setting (time period and location with sensory details)
  - Cover Art Description
  - Story characters
    - Main Characters (2-3 characters)
      - Name
      - Age
      - Gender
      - Occupation
      - Brief Backstory
      - Personality
      - Internal Conflict/Flaw
      - External Conflict/Goal
      - POV Character (True/False)
  - Relationship Structure (Monogamous, Polyamorous, Open Relationship)
  - Supporting Characters (list of important supporting characters and their roles)
  - Plot Summary (2-3 compelling sentences)
  - Themes (major themes explored)
  - Tropes (romance tropes used)
  - Conflict (main sources of conflict)
  - Heat Level (level of sexual content)
  - POV (1st person, 3rd person limited, 3rd person omniscient)
  - Ending (HEA or HFN)
  - Approximate Number of Chapters
  - Story length
  - Chapter length range [num1, num2] 
  - Special Requests (optional)

- This info will be passed into the template generate_input_prompt.txt, and then used as a prompt with gemini 2.0 flash
- We'll get the response from gemini 2.0 flash as a json, and parse it into a data structure.
- We'll extract the number of chapters from the response, and then use that to determine the number of batches we need to generate chapter overviews (default to 5 chapters at a time).
- We'll then do a batch run of gemini 2.0 flash to generate chapter overviews using the structure_prompt.txt, with added batch context info from previous runs to ensure continuity.
  - We'll need to keep a datastructure which keeps track of important story details and context between batches including active arcs, key plot points, main character health, mental state, and other important details.
- After we have a list of all the chapters, with all the scenes/ other relevant info, we'll pass in the story info generated from the first step, with the chapter info to generate the story. chapter by chapter. 
  - We'll need to keep a datastructure which keeps track of important story details and context between chapters including active arcs, key plot points, main character health, mental state, and other important details. This info should be passed back into the next chapter so we can ensure continuity.
  - If a chapter has nsfw scenes, then pass the nsfw scene to a different model that is unfiltered, We still need to ensure that the two chapters have continuity. 
- We want to store all chapter info in a txt file with proper formatting, and make this available to the user. The api call should return the path to the txt file after completion.
- For all data structures you can look at the prompt files to see what we need generated. Ensure that the data is properly formatted everytime we get a response from gemini 2.0 flash.