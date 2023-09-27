import re

# Define your multiline text
multiline_text = """
This is some text.
Here is another line.
And yet another line.
"""

# Define the multiline regex pattern
multiline_pattern = r"^Here is another line\.\n"

# Use re.MULTILINE flag to search for the pattern in multiline text
match = re.search(multiline_pattern, multiline_text, re.MULTILINE)

if match:
    print("Pattern found in multiline text.")
else:
    print("Pattern not found in multiline text.")
