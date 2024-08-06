import random

class CircularIterator:
    def __init__(self, items):
        self.items = items
        self.player = 0
        self.dealer = 0
        self.first_player = 0

    def next_index(self):
        return (self.player + 1) % len(self.items)
    
    def next_dealer(self):
        return (self.dealer + 1) % len(self.items)
    
    def previous_index(self):
        return (self.player - 1) % len(self.items)

    def current_string(self):
        return self.items[self.player]

    def next_string(self):
        return self.items[(self.player + 1) % len(self.items)]

    def previous_string(self):
        return self.items[(self.player - 1) % len(self.items)]

class Game:
    def __init__(self, players):
        self.players = CircularIterator(players)
        self.deck = self.create_deck()
        self.players_amt = len(players)
        self.round = 1
        self.num_cards = (42 // self.players_amt) if (42 // self.players_amt) < 13 else 13
        # self.num_cards = 3
        self.hands = {player: [] for player in players}
        self.bids = {player: 0 for player in players}
        self.lives = {player: self.num_cards for player in players}
    
    def create_deck(self):
        ranks = ['3', '2', 'A', 'K', 'J', 'Q', '7', '6', '5', '4']
        suits = ['paus', 'copas', 'espadas', 'ouros']
        deck = [f"{rank} de {suit}" for rank in ranks for suit in suits]
        deck.extend(["Coringa", "Coringa"])
        return deck

    def stronger_card(self, card1, card2):
        ranks = ['3', '2', 'A', 'K', 'J', 'Q', '7', '6', '5', '4']
        suits = ['paus', 'copas', 'espadas', 'ouros']
        if card1 == card2:
            return None
        if card1 == "Coringa":
            return card1
        if card2 == "Coringa":
            return card2
        rank1, suit1 = card1.split(" de ")
        rank2, suit2 = card2.split(" de ")
        #Primeira tem número mais forte
        if ranks.index(rank1) < ranks.index(rank2):
            return card1
        elif ranks.index(rank1) == ranks.index(rank2): #Mesmo número
            if suits.index(suit1) < suits.index(suit2): #checa naipe
                return card1
            else:
                return card2
        else:
            return card2

    def shuffle_and_deal(self):
        random.shuffle(self.deck)
        for player in self.hands:
            self.hands[player] = self.deck[:self.num_cards]
            self.deck = self.deck[self.num_cards:]


