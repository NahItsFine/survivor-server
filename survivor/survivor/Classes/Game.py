class Game:
    def __init__(self, name, password):
        self.name = name
        self.password = password
        self.players = []
        self.tribes = []
        self.rounds_played = 0
        self.tribe_game_stage = True

    def set_tribe_rounds(self, num_tribe_rounds):
        self.num_tribe_rounds = num_tribe_rounds

    def set_tribe_swaps(self, num_tribe_swaps):
        self.num_tribe_swaps = num_tribe_swaps

    def add_tribe(self, Tribe):
        self.tribes.append(Tribe)

    def clear_tribes(self):
        self.tribes.clear()

    def decide_num_rounds(self):
        pass

    def increment_round(self):
        """ Increments rounds played. If number of rounds passes the number of tribe rounds, change game state. """
        self.rounds_played += 1

        if self.rounds_played >= self.num_tribe_rounds:
            self.tribe_game_stage = False

    