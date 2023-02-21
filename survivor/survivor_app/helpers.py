# HELPERS FILE: place all random utility functions here
import random 
import json
from datetime import datetime

import sys, os
sys.path.append(os.path.abspath("../survivor/survivor_app"))
from socket_models import *

def challenge_to_dict(challenge):
    ret = {
        "id": challenge[0],
        "name": challenge[1],
        "type": challenge[2],
        "description": challenge[3],
        "means": challenge[4],
        "icon": challenge[5]
    }
    return ret
    
def rounds_to_JSON(query_return):
    return_list = []
    for i in range(len(query_return)):
        return_json = {}
        return_json['round_num'] = query_return[i][1]
        return_json['day'] = query_return[i][3]
        return_json['phase'] = query_return[i][4]
        return_json['type'] = query_return[i][5]
        return_json['winning_player'] = query_return[i][6]
        return_json['winning_tribe'] = query_return[i][7]
        return_json['eliminated_player'] = query_return[i][8]
        return_json['idol_roll'] = query_return[i][9]
        return_json['challenge_id'] = query_return[i][10]
        return_list.append(return_json)

    return return_list

def players_to_JSON(query_return):
    return_list = []
    for i in range(len(query_return)):
        return_json = {}
        return_json['username'] = query_return[i][7]
        return_json['player_id'] = query_return[i][0]
        return_json['name'] = query_return[i][1]
        return_json['discord_name'] = query_return[i][2]
        return_json['avatar'] = query_return[i][3]
        return_json['bio'] = query_return[i][4]
        return_json['is_still_playing'] = query_return[i][5]
        return_json['tribe_id'] = query_return[i][6]
        return_json['is_admin'] = query_return[i][8]
        return_json['tribe_colour'] = query_return[i][9]
        return_list.append(return_json)

    return return_list

def votable_players_to_JSON(query_return):
    return_list = []

    for player in query_return:
        return_json = {}
        return_json['player_id'] = player[0]
        return_json['username'] = player[1]     
        return_json['account_name'] = player[2]
        return_json['discord_name'] = player[3]
        return_json['avatar'] = player[4]
        return_json['is_immune'] = player[5]
        return_list.append(return_json)

    return return_list

def get_player_ids(query_return_of_players):
    return_list = []
    # Append player_ids to list and return
    for i in range(len(query_return_of_players)):
        return_list.append(query_return_of_players[i][0])

    return return_list
    
def randomize_player_order(player_list):
    random.shuffle(player_list)
    return player_list

def socket_payload_to_JSON(payload: SocketPayload):
    return json.dumps({
        'type': payload.type,
        'message': payload.message,
        'round_info': round_info_to_dict(payload.round_info),
        # 'round_vote': payload.round_vote,
        # 'round_challenge': payload.round_challenge,
        # 'round_idol': payload.round_idol,
        'votable_players': payload.votable_players,
        'vote_received': payload.vote_received,
        'votes_left': payload.votes_left,
        'player_idols': payload.player_idols,
        'idol_played_by': payload.idol_played_by,
        'all_votes': payload.all_votes,
        'eliminated_player': payload.eliminated_player,
        'challenge': payload.challenge,
        'challenge_tribes': payload.challenge_tribes,
        'challenge_players': payload.challenge_players,
        'challenge_winner': payload.challenge_winner,
        'idol_predictions_left': payload.idol_predictions_left,
        'idol_result': payload.idol_result
    })

def game_info_to_dict(game):
    game_dict = {
        'game_id': game[0],
        'name': game[1], 
        'password': game[2], 
        'discord_link': game[3], 
        'num_rounds_played': game[4],
        'game_stage': game[5],
        'is_active': game[6],
        'joinable': game[7],
        'num_players': game[8],
        'num_players_left': game[9],
    }

    return game_dict

def round_info_to_dict(round):
    ret = {}
    ret['id'] = round[0]
    ret['round_num'] = round[1]
    ret['game_id'] = round[2]
    ret['day'] =  datetime.strftime(round[3], '%m/%d/%Y')
    ret['phase'] = round[4]
    ret['type'] = round[5]
    ret['winning_player'] = round[6]
    ret['winning_tribe'] = round[7]
    ret['eliminated_player'] = round[8]
    ret['idol_roll'] = round[9]
    ret['challenge_id'] = round[10]

    return ret

def player_idols_to_dict(players):
    ret = dict()
    for player in players:
        ret[player[0]] = player[1]

    return ret