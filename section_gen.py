import json

scene_fpath = "./media/videos/main/1080p60/sections"
# Load the JSON file exported from Manim
with open(scene_fpath + "/Q2.json") as f:
    sections = json.load(f)

# Template for each slide section
slide_template = """
<section data-background-video="{video}" data-autoplay data-preload data-background-color="black"></section>
"""

# Generate the section tags
sections_html = ""
for sec in sections:
    sections_html += slide_template.format(
        video=scene_fpath + "/" + sec["video"]
    )

# Save the output
with open("slides_sections.txt", "w") as f:
    f.write(sections_html)

print("Generated slides_sections.html with only <section> tags.")
