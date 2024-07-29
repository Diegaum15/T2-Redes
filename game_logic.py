import random

class CircularIterator:
    def __init__(self, items):
        self.items = items
        self.index = 0

    def next(self):
        item = self.items[self.index]
        self.index = (self.index + 1) % len(self.items)
        return item

    def current(self):
        return self.items[self.index]

    def previous(self):
        self.index = (self.index - 1) % len(self.items)
        return self.items[self.index]

class Game:
    def __init__(self, players):
        self.players = CircularIterator(players)
        self.deck = self.create_deck()
        self.round = 1
        self.hands = {player: [] for player in players}
        self.bids = {player: 0 for player in players}
        self.scores = {player: 0 for player in players}

    def create_deck(self):
        ranks = ['3', '2', 'A', 'K', 'J', 'Q', '7', '6', '5', '4']
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        return [f"{rank} of {suit}" for rank in ranks for suit in suits]

    def shuffle_and_deal(self):
        random.shuffle(self.deck)
        num_cards = 13 - (self.round - 1)
        for player in self.hands:
            self.hands[player] = self.deck[:num_cards]
            self.deck = self.deck[num_cards:]

    def collect_bids(self):
        for player in self.hands:
            # Solicitar apostas dos jogadores
            pass

    def play_round(self):
        for player in self.hands:
            # Lógica de jogo de cartas
            pass

    def calculate_scores(self):
        # Calcular pontuações dos jogadores
        pass

    def next_round(self):
        self.round += 1
        self.players.next()

    def get_current_dealer(self):
        return self.players.current()
