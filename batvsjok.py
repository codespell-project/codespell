import random

# Create a class to represent Batman
class Batman:
    def __init__(self):
        self.health = 100
        self.gadgets = ["batarang", "grappling hook", "utility belt"]

    def fight(self, enemy):
        # Randomly choose a gadget to use
        gadget = random.choice(self.gadgets)

        # Use the gadget
        if gadget == "batarang":
            enemy.health -= 10
        elif gadget == "grappling hook":
            # Disarm the enemy
            enemy.weapon = None
        elif gadget == "utility belt":
            # Heal Batman
            self.health += 20

    def is_alive(self):
        return self.health > 0

# Create a class to represent an enemy
class Enemy:
    def __init__(self, name, weapon, health):
        self.name = name
        self.weapon = weapon
        self.health = health

    def attack(self, hero):
        hero.health -= 10

    def is_alive(self):
        return self.health > 0

# Create a Batman object
batman = Batman()

# Create an enemy object
joker = Enemy("Joker", "knife", 50)

# Start the fight
while batman.is_alive() and joker.is_alive():
    batman.fight(joker)
    joker.attack(batman)

# Check who won the fight
if batman.is_alive():
    print("Batman wins!")
else:
    print("The Joker wins!")
