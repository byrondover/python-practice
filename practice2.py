## This is the text editor interface.
## Anything you type or change here will be seen by the other person in real time.


# suit
# number



class Card:
    def __init__(self, suit, name, value):
        self.suit = suit
        self.name = name
        self.value = value

        # enum("hearts", "spades", "diamonds", "clubs")
        # enum(1, 13)


class CardsCollection:
    cards = []

    def __init__(self):
        return cards

    def addCard(self, card):
        # add card to cards array

    def removeCard(self, card):
        # remove the card from the cards array


class Deck(CardsCollection):
    cards = [
      Card("heart", "Ace of Hearts", 1),
      ...
    ]

    def __init__(self):
        return cards

    def shuffle(self):
        # randomly reorders cards.

    def dealCard(self, card):
        # remove the card from the cards array
        self.removeCard(card)


class Hand(CardsCollection):
    cards = []
    value = 0

    def __init__(self):
        return

    def addCard(self, card):
        # add card to cards array

    def playCard(self, card):
        # remove the card from the cards array
        self.removeCard(card)

    def getValue(self):
        # for card in cards


class BlackjackHand(Hand):
    def getValue(self):
        hand_value = 0

        for card in cards:
            if card.value == 1:
                card.value == 13

        hand_value += card.value

        if hand_value > 21 and card.value == 13:
            hand_value -= 12

        return hand_value


#class BackjackDeck(Deck):
#
