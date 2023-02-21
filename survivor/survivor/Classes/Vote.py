class Vote:
    def __init__(self):
        self.eligible_players = {}
        """ Use a dictionary to count votes """

    def add_eligible_player(self, Player):
        self.eligible_players[Player] = 0

    def remove_eligible_player(self, Player):
        self.eligible_players.pop(Player)

    def vote_player(self, Player_voted):
        self.eligible_players[Player_voted] += 1

    def decide_majority(self):
        """ Gets player(s) with max number of votes. If more than one, only keep them as eligible players """
        pass