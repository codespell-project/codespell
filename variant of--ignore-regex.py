import re

def process_text(text, ignore_regex):
    # Compile the regex pattern with the MULTILINE flag
    pattern = re.compile(ignore_regex, re.MULTILINE)
    
    # Use the findall method to identify matches in the text
    matches = pattern.findall(text)
    
    # Process the matches as needed (e.g., ignore or replace)
    processed_text = pattern.sub("", text)  # Remove the matched portions
    
    return processed_text, matches

# Example usage
text = """Line 1: This is some text.
Line 2: This is another line.
Line 3: Here's more text.
"""

ignore_regex = r"Line \d+: This is another line\."

processed_text, matches = process_text(text, ignore_regex)

# Print the processed text and matched patterns
print("Processed Text:")
print(processed_text)

print("\nMatched Patterns:")
for match in matches:
    print(match)

