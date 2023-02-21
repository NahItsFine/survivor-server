from datetime import datetime
import random
from re import A

import sys, os
sys.path.append(os.path.abspath("../survivor/survivor_app"))
from socket_models import *
from helpers import *
from psql_queries import *
from constants import *
import copy

# determine the message to send to the FE in the payload
def determine_message(payload_type):
    if(payload_type == PAYLOAD_INFO):
        return "Payload contains round information."
    elif(payload_type == PAYLOAD_VOTE):    
        return "Payload contains votable players."
    elif(payload_type == PAYLOAD_VOTE_RECEIVED):    
        return "Payload verifies that user's vote has been counted."
    elif(payload_type == PAYLOAD_VOTES_LEFT):    
        return "Payload contains number of votes left to be casted."
    elif(payload_type == PAYLOAD_VOTE_IDOLS):    
        return "Payload contains idol counts for players."
    elif(payload_type == PAYLOAD_NOT_PLAYING):
        return "User has been eliminated from this game."
    elif(payload_type == PAYLOAD_IDOL_USED):
        return "A Player has used an idol."
    elif(payload_type == PAYLOAD_ALL_VOTES):
        return "Payload contains voting results."
    elif(payload_type == PAYLOAD_VOTE_ELIMINATED):
        return "A Player has been eliminated."
    elif(payload_type == PAYLOAD_VOTE_TIE):
        return "There has been a tie."
    elif(payload_type == PAYLOAD_VOTE_TIE_AGAIN):
        return "There has been a second tie."  
    elif(payload_type == PAYLOAD_CHALLENGE):
        return "A challenge has been determined." 
    elif(payload_type == PAYLOAD_CHALLENGE_WINNER):
        return "A player has won the challenge."
    elif(payload_type == PAYLOAD_IDOL_PREDICTION_RECEIVED):
        return "Your idol prediction has been received."
    elif(payload_type == PAYLOAD_IDOL_PREDICTIONS_LEFT):
        return "Payload contains idol predictions left to be casted."
    elif(payload_type == PAYLOAD_IDOL_REVEAL):
        return "Payload contains idol roll result."
         

# initiate a dict to keep track of players and their voting
# Vote Tracker Format:
# {
#   "votes_against": 0,
#   "idol_played": 0,
#   "has_voted": false
# }
def initialize_vote_tracker(player_list, existing_idols = False, vote_tracker = None):
    ret = dict()

    for player in player_list:
        idol_played = COUNCIL_NOT_IMMUNE if not existing_idols else vote_tracker[player[1]]['idol_played']
        player_dict = {
            "votes_against": 0,
            "idol_played": idol_played,
            "has_voted": False
        }
        ret[player[1]] = player_dict

    return ret

# initiate dict to keep track of players' idol predicitons
def initialize_idol_tracker(game_id):
    ret = dict()

    active_players = query_get_players_from_game(game_id)   # [ [username, acct_name], [username, acct_name], ... ]
    for player in active_players:
        player_dict = {
            "idol_prediction": None,
            "has_predicted": False
        }
        ret[player[0]] = player_dict

    return ret

# return list of players that can be voted out
def get_votable_players(game_id, round_type, vote_tracker = None, includeImmunePlayers = False):
    votable_players = query_get_votable_players(game_id)

    print(f"Votable Players Before Extend:{votable_players}")

    if(includeImmunePlayers):
        votable_players.extend(query_get_immune_players(game_id))

    print(f"Votable Players After Extend:{votable_players}")

    if((round_type == ROUND_TYPE_INDIVIDUAL or round_type == ROUND_TYPE_FINAL_3) and vote_tracker is not None):
        immune_players = query_get_immune_players(game_id)
        for player in immune_players:
            vote_tracker[player[1]]['idol_played'] = COUNCIL_IMMUNE
            votable_players.append(player)

    votable_players_json = votable_players_to_JSON(votable_players)

    return votable_players, votable_players_json

# return list of all players to vote
def get_all_players_for_final_vote(game_id, vote_tracker = None):
    votable_players = query_get_all_players(game_id)

    for index in range(len(votable_players)):
        if(votable_players[index][6]): continue # if player still playing, skip
        [a, b, c, d, e, f, g] = votable_players[index]
        destructured_player = [a, b, c, d, e, f, g]
        destructured_player[5] = True # is_immune = True
        votable_players[index] = destructured_player

    print(f'117: {votable_players}')
    votable_players_json = votable_players_to_JSON(votable_players)

    return votable_players, votable_players_json

# return list of players than can vote but cannot be voted upon
def attach_immunity_to_players(game_id, round_type, votable_players, vote_tracker):
    if(round_type != ROUND_TYPE_TRIBE):
        immune_players = query_get_immune_players(game_id)
        for player in immune_players:
            vote_tracker[player[1]]['idol_played'] = COUNCIL_IMMUNE
            votable_players.append(player)

    for player in votable_players:
        if(vote_tracker[player[1]]['idol_played'] == COUNCIL_TEMP_IMMUNE):
            player = edit_votable_player(player, 5, True) #player[5] = is_immune

    votable_players_json = votable_players_to_JSON(votable_players)

    return votable_players, votable_players_json

def attach_immunity_for_final_3(votable_players, vote_tracker):
    for player in votable_players:
        # player[6] = is_still_playing
        if (player[6]): continue 
        vote_tracker[player[1]]['idol_played'] = COUNCIL_IMMUNE

    votable_players_json = votable_players_to_JSON(votable_players)

    return votable_players, votable_players_json

# return tuple of (num votes left to be cast, total num votes)
def get_votes_left(vote_tracker):
    votes_left = 0
    votes_total = 0
    for username in vote_tracker:
        if(vote_tracker[username]['has_voted'] == False):
            votes_left += 1
        votes_total += 1
    return (votes_left, votes_total)

# return tuple of (num idol predictions left to be made, total num predictions)
def get_idol_predictions_left(idol_tracker):
    idol_predictions_left = 0
    idol_predictions_total = 0
    for username in idol_tracker:
        if(idol_tracker[username]['has_predicted'] == False):
            idol_predictions_left += 1
        idol_predictions_total += 1
    return (idol_predictions_left, idol_predictions_total)

# Get list of username(s) of person(s) with most votes.
def get_persons_with_most_votes(vote_tracker):
    vote_count_list = list()

    # remove from vote tracker all players with idols played
    for player in vote_tracker:
        if(vote_tracker[player]['idol_played'] != COUNCIL_IMMUNE and vote_tracker[player]['idol_played'] != COUNCIL_TEMP_IMMUNE):
            vote_count_list.append(vote_tracker[player]['votes_against'])
        else:
            vote_count_list.append(0)

    
    # Puts usernames/keys into list
    username_list = list(vote_tracker.keys())
    # Put vote count in a list and see if there are repeats of max
    max_vote_number = max(vote_count_list)

    # Return username if there is only one max number
    if (vote_count_list.count(max_vote_number) <= 1):
        return [username_list[vote_count_list.index(max(vote_count_list))]]
    else:
        list_of_usernames = []
        for i in range(len(vote_count_list)):
            if vote_count_list[i] == max_vote_number:
                list_of_usernames.append(username_list[i])
        return list_of_usernames

# players not involved in tie are granted them temporary immunity
def immunize_non_tied_players(tied_players, votable_players, vote_tracker):
    for index in range(len(votable_players)):
        if(votable_players[index][1] not in tied_players): #player[1] = username
            vote_tracker[votable_players[index][1]]['idol_played'] = COUNCIL_TEMP_IMMUNE
            votable_players[index] = edit_votable_player(votable_players[index], 5, True) #player[5] = is_immune
    
    votable_players_json = votable_players_to_JSON(votable_players)
    return votable_players, votable_players_json

def edit_votable_player(player, index_to_edit, value):
    if(len(player) == 6):
        [a, b, c, d, e, f] = player
        destructured_player = [a, b, c, d, e, f]
    elif (len(player) == 7):
        [a, b, c, d, e, f, g] = player
        destructured_player = [a, b, c, d, e, f, g]
    destructured_player[index_to_edit] = value
    return tuple(destructured_player)

# remove players not involved in tie
def remove_non_tied_players(tied_players, votable_players):
    votable_players_copy = copy.copy(votable_players)
    for player in votable_players:
        if(player[1] not in tied_players):
            votable_players_copy.remove(player)
    
    votable_players_json = votable_players_to_JSON(votable_players_copy)
    return votable_players_copy, votable_players_json

# remove players involved in the tie and players who played idols
def remove_tied_idoled_players(vote_tracker):
    votable_players = list()

    for player in vote_tracker:
        # temp bc those are the non-tied, non-idoled players
        if((player in vote_tracker) and ((vote_tracker[player]['idol_played']) == COUNCIL_TEMP_IMMUNE)):
            # player[5] = False
            votable_players.append(player)

    # if there are no non-tied, non-idoled players, just do tied players
    if(len(votable_players) == 0):
        for player in vote_tracker:
            if((player in vote_tracker) and ((vote_tracker[player]['idol_played']) == COUNCIL_NOT_IMMUNE)):
                # player[5] = False
                votable_players.append(player)

    return votable_players

# update idol count in the db if players predicted correctly
def update_idol_count(game_id, idol_tracker, idol_num):
    for player in idol_tracker:
        if(idol_tracker[player]['idol_prediction'] == str(idol_num)):
            query_increment_idol(game_id, player)
    
    return

# selects random player from list
def choose_random_player(player_list):
    random.shuffle(player_list)
    return player_list[0]

# select random number between range (inclusive)
def choose_random_number(min, max):
    return random.randint(min,max)

# Execute a series of queries and services for a given event
def execute_event(event_code, game_id, round_num):
    if(event_code == EVENT_PRECOUNCIL_ROUND_0):
        # create tribes
        create_tribes(game_id)
        # shuffle players into tribes
        shuffle_players_to_tribes(game_id)
        # set round phase to challenge_start (skip council)
        query_advance_round(game_id, round_num, ROUND_PHASE_CHALLENGE_START)
        # query_get_eliminated_player will display "No One" as the eliminated player in the FE
    elif(event_code == EVENT_PRECOUNCIL_FINAL):
        # set game and round in db to be finale stage/type
        query_set_game_stage(game_id, GAME_STAGE_FINAL_3)
        query_set_round_type(game_id, round_num, ROUND_TYPE_FINAL_3)
        # set round phase to challenge_start (skip council)
        query_advance_round(game_id, round_num, ROUND_PHASE_CHALLENGE_START)
        # voting after challenge (manipulating round phase, done by frontend and round_type)
        # resurrect, make immune so not in votable players, make remaining players NOT immune
        query_prep_players_final_council(game_id)
    elif(event_code == EVENT_PRECHALLENGE_SWAP):
        # shuffle players into tribes
        shuffle_players_to_tribes(game_id)
    elif(event_code == EVENT_PRECHALLENGE_MERGE):
        # remove tribe associations from players
        remove_tribes(game_id)
        # set game in db to be individual stage
        query_set_game_stage(game_id, GAME_STAGE_INDIVIDUAL)
        query_set_round_type(game_id, round_num, ROUND_TYPE_INDIVIDUAL)
    elif(event_code == EVENT_PRECHALLENGE_FINAL_4):
        # set game in db to be final 4 stage/type
        query_set_game_stage(game_id, GAME_STAGE_FINAL_4)
        query_set_round_type(game_id, round_num, ROUND_TYPE_FINAL_4)
        # add logic to not allow idols (set everyone to 0)
        query_remove_idols(game_id)

    # return event-specific message for FE snackbar
    return determine_event_message(event_code)

# determine the event specific message to send to the FE in the payload
def determine_event_message(event_code):
    if(event_code == EVENT_PRECOUNCIL_ROUND_0):
        return "The Game has begun! All players have been randomly split into two tribes and you can go to the Game page to see the tribes. There will be no Tribal Council this round."
    elif(event_code == EVENT_PRECOUNCIL_FINAL):    
        return "Welcome to the Finale! Two players will battle for the final spot amongst the Final 3. Then, the finalists will make their bid on why they deserve to be the Ultimate Virtual Survivor."
    elif(event_code == EVENT_PRECOUNCIL_FINAL_CHALLENGE):    
        return "The Winner of the Final 4 Challenge will pick two people among the Final 4 to join the Final 3. The other two players will compete in this Challenge to determine who will join the previous two players."
    elif(event_code == EVENT_PRECHALLENGE_SWAP):    
        return "Tribe Swap! Tribes have been shuffled and players may have been assigned new tribes. You can go to the Game page to see the new tribes."
    elif(event_code == EVENT_PRECHALLENGE_MERGE):    
        return "Tribe Merge! All players have been joined into one singular tribe, and will play as individuals for the remainder of the game."
    elif(event_code == EVENT_PRECHALLENGE_FINAL_4):    
        return "Final 4! This round's challenge will be drawn from a special pool of challenges. See the Rules ('How To Play') for more information. Idols can no longer be played for the remainder of the game."

# execute_event helper functions
def create_tribes(game_id):
    query_create_game_tribe(game_id, TRIBE_ORANGE)
    query_create_game_tribe(game_id, TRIBE_PURPLE)

def shuffle_players_to_tribes(game_id):
    all_players = query_get_active_game_players(game_id)
    if(all_players != None):
        # Get players, randomize order, split in half to get tribes
        all_players_ids = get_player_ids(all_players)
        random.shuffle(all_players_ids)
        first_tribe_players = all_players_ids[:len(all_players_ids)//2]
        second_tribe_players = all_players_ids[len(all_players_ids)//2:]
        first_tribe_id = query_get_tribe_id_from_game(game_id,TRIBE_ORANGE)
        second_tribe_id = query_get_tribe_id_from_game(game_id,TRIBE_PURPLE)

        # Insert players into tribes by setting Player tribe_id property
        query_set_players_tribe_id(first_tribe_players, first_tribe_id)
        query_set_players_tribe_id(second_tribe_players, second_tribe_id)

def remove_tribes(game_id):
    all_players = query_get_active_game_players(game_id)
    if(all_players != None):
        all_players_ids = get_player_ids(all_players)
        query_set_players_tribe_id(all_players_ids, "NULL")
