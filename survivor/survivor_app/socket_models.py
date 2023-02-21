# define socket return class structure
class SocketPayload():
    
    def __init__(self, type, message):
        self.type = type
        self.message = message
        self.round_info = None
        self.votable_players = None
        self.vote_received = None
        self.votes_left = (0,0)
        self.player_idols = None
        self.idol_played_by = None
        self.all_votes = None
        self.eliminated_player = None
        self.challenge = None
        self.challenge_tribes = None
        self.challenge_players = None
        self.challenge_winner = None
        self.idol_predictions_left = None
        self.idol_result = None
class RoundInfo ():
    id: int
    round_num: int
    game_id: int
    day: str
    phase: int
    type: int 
    eliminated_player: int
    winning_tribe: int
    winning_player: int
    idol_roll: int
    challenge_id: int