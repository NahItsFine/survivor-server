class Round:
    def __init__(self, date, type):
        self.date = date
        self.type = type
        self.eligible_players = []

    def set_winner(self, winner):
        """ Winner is either Player or Team object """
        self.winner = winner

    def get_eliminated(self):
        pass