def are_anagrams(str1, str2):
    # Remove spaces and convert both strings to lowercase for case-insensitive matching
    str1 = str1.replace(" ", "").lower()
    str2 = str2.replace(" ", "").lower()

    # Check if the sorted characters of both strings match
    return sorted(str1) == sorted(str2)

# Example usage:
word1 = input("enter the first word: ")
word2 = input("enter the socond word: ")

if are_anagrams(word1, word2):
    print(f"{word1} and {word2} are anagrams.")
else:
    print(f"{word1} and {word2} are not anagrams.")
