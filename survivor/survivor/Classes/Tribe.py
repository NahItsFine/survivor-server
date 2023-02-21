class Tribe:
    def __init__(self, name, colour):
        self.name = name
        self.colour = colour
        self.players = []
        self.immunity = False

    def add_player(self, Player):
        self.players.append(Player)

    def remove_player(self, Player):
        self.players.remove(Player)

    def set_immune(self):
        self.immunity = True

    def set_not_immune(self):
        self.immunity = False