import re

def get_misspellings(word):
    return {word[i] + word[i+1] + word[i+2] for i in range(len(word)-2)}

def interactive_misspelling_picker(word, start_number=1):
    misspellings = get_misspellings(word)
    print(f"Misspellings for '{word}':")
    for i, misspelling in enumerate(misspellings, start=start_number):
        print(f"{i}. {misspelling}")

    while True:
        try:
            choice = int(input("Enter the number of the misspelling you want to correct, or 0 to exit: "))
            if choice == 0:
                break
            elif 1 <= choice <= len(misspellings):
                print(f"You chose to correct the misspelling '{list(misspellings)[choice-1]}'.")
                break
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    word = input("Enter a word: ")
    start_number = int(input("Enter the start number for misspelling selection (default is 1): ") or 1)
    interactive_misspelling_picker(word, start_number)

if __name__ == "__main__":
    main()
