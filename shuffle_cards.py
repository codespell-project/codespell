# Import required modules
from random import shuffle


# Define a class to create
# all type of cards
class Cards:
	global suites, values
	suites = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
	values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

	def __init__(self):
		pass


# Define a class to categorize each card
class Deck(Cards):
	def __init__(self):
		Cards.__init__(self)
		self.mycardset = []
		for n in suites:
			for c in values:
				self.mycardset.append((c)+" "+"of"+" "+n)

	# Method to remove a card from the deck
	def popCard(self):
		if len(self.mycardset) == 0:
			return "NO CARDS CAN BE POPPED FURTHER"
		else:
			cardpopped = self.mycardset.pop()
			print("Card removed is", cardpopped)


# Define a class gto shuffle the deck of cards
class ShuffleCards(Deck):

	# Constructor
	def __init__(self):
		Deck.__init__(self)

	# Method to shuffle cards
	def shuffle(self):
		if len(self.mycardset) < 52:
			print("cannot shuffle the cards")
		else:
			shuffle(self.mycardset)
			return self.mycardset

	# Method to remove a card from the deck
	def popCard(self):
		if len(self.mycardset) == 0:
			return "NO CARDS CAN BE POPPED FURTHER"
		else:
			cardpopped = self.mycardset.pop()
			return (cardpopped)


# Driver Code
# Creating objects
objCards = Cards()
objDeck = Deck()

# Player 1
player1Cards = objDeck.mycardset
print('\n Player 1 Cards: \n', player1Cards)

# Creating object
objShuffleCards = ShuffleCards()

# Player 2
player2Cards = objShuffleCards.shuffle()
print('\n Player 2 Cards: \n', player2Cards)

# Remove some cards
print('\n Removing a card from the deck:', objShuffleCards.popCard())
print('\n Removing another card from the deck:', objShuffleCards.popCard())
