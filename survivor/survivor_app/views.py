from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view
import json
from flask import jsonify

# import psql_queries file
import sys, os
sys.path.append(os.path.abspath("../survivor/survivor_app"))
from psql_queries import *
from security import encrypt_password
from helpers import *

# Create your views here.
# Views are functions that process HTTP requests and call PSQL Queries

# An API function used for testing
@api_view(['GET'])
def test(request):
    return JsonResponse({ 'testestest': request.GET.get('var', '') })

# An API function to verify a login attempt's credentials
@api_view(['GET'])
def login(request):
    # check if user exists
    try:
        query_return = query_check_username_exists(request.GET.get('username', ''))
        if(query_return == None):
            login_successful = False
            message = "Account with that username does not exist."
        else:
            # authenticate username password combination
            query_return2 = query_auth_username_password(request.GET.get('username', ''), request.GET.get('password', ''), query_return[0])
            if(query_return2 != None):
                login_successful = True
                message = "authentication successful"
            else:
                login_successful = False
                message = "Incorrect password."
    except:
        login_successful = False
        message = "Incorrect password."

    # return
    return JsonResponse({ 'login_successful': login_successful, 'message': message })

# An API function to create an account
@api_view(['POST'])
def create_account(request):

    # CHANGE TO SEND ALL THE DATA VIA BODY
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    # check if user exists
    query_return = query_check_username_exists(body['username'])
    if(query_return != None):
        account_created = False
        message = "Account with that username already exists."
    else:
        # create account in the database

        encrypted_password = encrypt_password(body['password'])

        query_return = query_create_account(
            body['username'],
            encrypted_password,
            body['name'],
            body['discord'],
            body['avatar'],
            body['bio']
        )
        account_created = True
        message = "Account created."

    # return
    return JsonResponse({ 'account_created': account_created, 'message': message })

# An API function to fetch account information (but not password)
@api_view(['GET'])
def account(request):
    # check if user exists
    query_return = query_check_username_exists(request.GET.get('username', ''))
    if(query_return == None):
        message = "Account with that username does not exist."
    else:
        # get account information
        query_return = query_get_account_info(request.GET.get('username', ''))
        if(query_return != None):
            message = "Account information successfully retrieved."

            # return
            return JsonResponse({
                'username': query_return[0],
                'name': query_return[1],
                'bio': query_return[2],
                'discord': query_return[3],
                'avatar': query_return[4],
                'message': message
            })
        else:
            message = "Incorrect password."

            # return
            return JsonResponse({ 'message': message })

# An API function to fetch game information
@api_view(['GET'])
def game(request):
    # get game information
    query_return = query_get_game_info(request.GET.get('game_id', ''))
    if(query_return != None):
        message = "Game information successfully retrieved."
        # return
        return JsonResponse({
            'name': query_return[1],
            'password': query_return[2],
            'discord_link': query_return[3],
            'num_rounds_played': query_return[4],
            'game_stage': query_return[5],
            'is_active': query_return[6],
            'joinable': query_return[7],
            'num_players': query_return[8],
            'num_players_left': query_return[9],

            'message': message
        })
    else:
        message = "Game not found."

        # return
        return JsonResponse({ 'message': message })

# An API function to create a game
@api_view(['POST'])
def game_create(request):
    # CHANGE TO SEND ALL THE DATA VIA BODY
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    # get account id from name
    query_return = query_get_account_id_from_name(body['username'])
    account_id = query_return[0]
    if(query_return != None):
        # check if game with name already exists
        query_return = query_check_game_exists(body['name'])
        if(query_return == None):
            # create game
            query_return = query_create_game(
                body['name'],
                encrypt_password(body['password']),
                body['discord']
            )
            # get game id
            query_return = query_get_game_id_from_name(body['name'])
            game_id = query_return[0]
            # create admin player
            message = "Success."
            query_return = query_create_player(account_id, game_id, True)
            # return
            return JsonResponse({ 'successful': True, 'message': message, 'game_id': game_id, 'player_id': query_return[0] })
        else:
            message = "Game with that name already exists."
            # return
            return JsonResponse({ 'successful': False, 'message': message, 'game_id': 0, 'player_id': 0 })
    else:
        message = "User not found."
        # return
        return JsonResponse({ 'successful': False, 'message': message, 'game_id': 0, 'player_id': 0 })

# An API function to join a game
@api_view(['GET'])
def game_join(request):
    # get account id from name
    query_return = query_get_account_id_from_name(request.GET.get('username', ''))
    account_id = query_return[0]
    if(query_return != None):
        # check game exists, return hashed password if it does
        query_return = query_check_game_exists(request.GET.get('name', ''))
        if(query_return != None):
            # authenticate username password combination, return game id
            try:
                query_return = query_auth_game(request.GET.get('name', ''), request.GET.get('password', ''), query_return[0])
                if(query_return != None):
                    game_id = query_return[0]
                    joinable = query_return[1]
                    query_return = query_get_game_num_players(game_id)
                    num_players = query_return[0]
                    # check if there is still space in the game
                    if(num_players < 20):
                        # check if user already in game
                        query_return = query_check_account_in_game(account_id, game_id)
                        if(query_return == None):
                            if(joinable):
                                # create non-admin player
                                query_return = query_create_player(account_id, game_id, False)
                                message = "Success."
                                # return
                                return JsonResponse({ 'successful': True, 'message': message, 'game_id': game_id, 'player_id': query_return[0] })
                            else:
                                message = "Cannot join this Game. It has either already started or is has already ended."
                                # return
                                return JsonResponse({ 'successful': False, 'message': message, 'game_id': 0, 'player_id': 0 })
                        else:
                            message = "This Account has already joined this Game."
                            # return
                            return JsonResponse({ 'successful': False, 'message': message, 'game_id': 0, 'player_id': 0 })
                    else:
                        message = "This Game has reached the maximum amount of players (20)."
                        # return
                        return JsonResponse({ 'successful': False, 'message': message, 'game_id': 0, 'player_id': 0 })
                else:
                    message = "Incorrect Game password."
                    # return
                    return JsonResponse({ 'successful': False, 'message': message, 'game_id': 0, 'player_id': 0 })
            except:
                message = "Incorrect Game password."
                # return
                return JsonResponse({ 'successful': False, 'message': message, 'game_id': 0, 'player_id': 0 })
        else:
            message = "Game not found."
            # return
            return JsonResponse({ 'successful': False, 'message': message, 'game_id': 0, 'player_id': 0 })
    else:
        message = "User not found."
        # return
        return JsonResponse({ 'successful': False, 'message': message, 'game_id': 0, 'player_id': 0 })

# An API function to fetch rounds for current game
@api_view(['GET'])
def game_rounds(request):
    # get game information
    query_return = query_get_game_rounds(request.GET.get('game_id', ''))
    if(query_return != None):
        message = "Round information successfully retrieved."
        # return
        return JsonResponse({'rounds': rounds_to_JSON(query_return)})
    else:
        message = "Game not found."

        # return
        return JsonResponse({ 'message': message })

# An API function to fetch latest round for current game
@api_view(['GET'])
def get_latest_round(request):
    # get game information
    query_return = query_get_latest_round(request.GET.get('game_id', ''))
    if(query_return != None):
        message = "Round information successfully retrieved."
        # return
        return JsonResponse(round_info_to_dict(query_return))
    else:
        message = "Game not found."

        # return
        return JsonResponse({ 'message': message })

# An API function to fetch rounds for current game
@api_view(['GET'])
def current_player(request):
    # get game information
    query_return = query_get_game_current_player(request.GET.get('game_id', ''), request.GET.get('username', ''))
    if(query_return != None):
        # return
        return JsonResponse({
            'player_id': query_return[7],
            'name': query_return[0],
            'discord_name': query_return[1],
            'avatar': query_return[2],
            'idol_count': query_return[3],
            'is_still_playing': query_return[4],
            'is_admin': query_return[5],
            'tribe_id': query_return[6],
            'tribe_colour': query_return[8]
            })
    else:
        message = "Player not found."
        # return
        return JsonResponse({ 'message': message })

# An API function to fetch all players for current game
@api_view(['GET'])
def game_players(request):
    # get game information
    query_return = query_get_game_players(request.GET.get('game_id', ''))
    if(query_return != None):
        message = "Players information successfully retrieved."
        # return
        return JsonResponse({'players': players_to_JSON(query_return)})
    else:
        message = "Game not found."
        # return
        return JsonResponse({ 'message': message })

# An API function to fetch active players for current game
@api_view(['GET'])
def active_game_players(request):
    # get game information
    query_return = query_get_active_game_players(request.GET.get('game_id', ''))
    if(query_return != None):
        message = "Players information successfully retrieved."
        # return
        return JsonResponse({'players': players_to_JSON(query_return)})
    else:
        message = "Game not found."
        # return
        return JsonResponse({ 'message': message })

# An API function to fetch all challenges
@api_view(['GET'])
def challenges(request):

    # query get challenge by id
    # return each challenge as dict
    # final result is dict of list containing dicts

    # split challenges into lists: tribal, merge, final 4, tower
    tribal = list()
    individual = list()
    final_four = list()
    tower = list()

    id = 1
    query_return = query_get_challenge(id)
    while(query_return != None):
        if (query_return[2] == 0):
            tribal.append(challenge_to_dict(query_return))
        elif (query_return[2] == 1):
            individual.append(challenge_to_dict(query_return))
        elif (query_return[2] ==2):
            final_four.append(challenge_to_dict(query_return))
        elif (query_return[2] == 3):
            tower.append(challenge_to_dict(query_return))

        id += 1
        query_return = query_get_challenge(id)

    # return
    return JsonResponse({
        'tribal_challenges': tribal,
        'individual_challenges': individual,
        'final_four_challenges': final_four,
        'tower_challenge': tower
    })

# An API function to getch challenge name by id
@api_view(['GET'])
def challenge_name(request):
    query_return = query_get_challenge_name_by_id(request.GET.get('challenge_id', ''))

    # return
    return JsonResponse({'challenge_name': query_return[0]})

# An API function to get name by id
@api_view(['GET'])
def name_by_id(request):
    name = ''
    if request.GET.get('player_id',''):
        query_return = query_get_account_name_by_player_id(request.GET.get('player_id',''))
        if query_return != None: name = query_return[0]
    elif request.GET.get('tribe_id',''):
        query_return = query_get_tribe_colour_by_id(request.GET.get('tribe_id',''))
        if query_return != None: name = query_return[0]
    return JsonResponse({'name': name})
# An API function to start game
@api_view(['PATCH'])
def start_game(request):
    # games must have minimum 12 players
    query_return = query_get_game_num_players(request.GET.get('game_id',''))
    num_players = query_return[0]
    min_players = 1    # TODOTESTING: CHANGE TO 12 AFTER DONE TESTING
    if(num_players < min_players):   
        successful = False
        message = "Need at least 12 players to start a game. There are currently only " + str(num_players) + " player(s)."
        return JsonResponse({'successful': successful, 'message': message })

    query_return = query_start_game(request.GET.get('game_id',''))
    if(query_return == None):
        successful = False
        message = "Couldn't Find Game."
    else:
        successful = True
        message = "Game Started."

    # Create a new round, round #0
    query_create_round(request.GET.get('game_id',''), 0, ROUND_TYPE_TRIBE)

    # return
    return JsonResponse({'successful': successful, 'message': message })

# An API function to create a game
@api_view(['POST'])
def start_round(request):

    # Get Latest Round info
    query_return1 = query_get_latest_round(request.GET.get('game_id',''))
    latest_round_num = query_return1[1]
    latest_round_phase = query_return1[4]

    # Check latest round is complete then create round, else send warning
    if latest_round_phase == ROUND_PHASE_COMPLETE:
        query_return2 = query_create_round(request.GET.get('game_id',''), latest_round_num+1, query_return1[5])
        if query_return2:
            #increment rounds played in game
            query_increment_rounds_played(request.GET.get('game_id',''))
            successful = True
            message = "New Round Created"
            new_round_num = latest_round_num+1
        else:
            successful = False
            message = "Something went wrong in Round Creation"
            new_round_num = -1
    else:
        successful = False
        message = "Previous Round Not Concluded"
        new_round_num = -1
    
    return JsonResponse({'successful': successful, 'message': message, 'new_round_num': new_round_num })

# An API function to end game
@api_view(['PATCH'])
def end_game(request):

    query_return = query_end_game(request.GET.get('game_id',''))
    if(query_return == None):
        successful = False
        message = "Couldn't Find Game."
    else:
        successful = True
        message = "Game Ended."

    # return
    return JsonResponse({'successful': successful, 'message': message })

# Decrement current users idol, increment to another user
@api_view(['PATCH'])
def transfer_idol(request):
    if (query_get_player_idol_count(request.GET.get('game_id',''), request.GET.get('giver_username','')) > 0):
        giver_query_return = query_decrement_idol(request.GET.get('game_id',''), request.GET.get('giver_username',''))
        # If decrement didnt work
        if(giver_query_return == None):
            successful = False
            message = "Couldn't decrement current user's idols."
        else:
            taker_query_return = query_increment_idol(request.GET.get('game_id',''), request.GET.get('taker_username',''))
            # if increment didnt work
            if(taker_query_return == None):
                successful = False
                message = "Couldn't increment other user's idols."
            else:
                successful = True
                message = "Idol Transferred to "
    else:
        successful = False
        message = "You have no more idols to transfer."

    return JsonResponse({'successful': successful, 'message': message })

# An API function to create tribes
@api_view(['POST'])
def create_tribes(request):

    query_return1 = query_create_game_tribe(request.GET.get('game_id', ''), 0)
    query_return2 = query_create_game_tribe(request.GET.get('game_id', ''), 1)

    if(query_return1 and query_return2):
        message = "Game Tribes Created Successfully"
        successful = True
    else:
        message = "Something went wrong in tribe creation."
        successful = False

    return JsonResponse({'successful': successful, 'message': message })

# An API function to add players to a tribe
@api_view(['PATCH'])
def tribe_insert(request):

    query_return = query_get_game_players(request.GET.get('game_id', ''))
    if(query_return != None):
        message = "Players information successfully retrieved."
        # Get players, randomize order, split in half to get tribes
        query_return = randomize_player_order(get_player_ids(query_return))
        first_tribe_players = query_return[:len(query_return)//2]
        second_tribe_players = query_return[len(query_return)//2:]
        first_tribe_id = query_get_tribe_id_from_game(request.GET.get('game_id', ''),0)
        second_tribe_id = query_get_tribe_id_from_game(request.GET.get('game_id', ''),1)

        # Insert players into tribes by setting Player tribe_id property
        insert_success1 = query_set_players_tribe_id(first_tribe_players, first_tribe_id)
        insert_success2 = query_set_players_tribe_id(second_tribe_players, second_tribe_id)

        if (insert_success1 and insert_success2):
            message = "Error in setting player tribe ids."
            return JsonResponse({ 'message': message })

    else:
        message = "Game not found."
        return JsonResponse({ 'message': message })

# An API function to get games
@api_view(['GET'])
def get_games(request):

    username = request.GET.get('username', '')
    complete = request.GET.get('complete', '')

    games = list()
    if(complete == 'True'):
        query_return = query_get_completed_games(username)
    else:
        query_return = query_get_current_games(username)

    for game in query_return:
        games.append(game_info_to_dict(game))

    return JsonResponse(games, safe=False)

# An API function to get player data from a username
@api_view(['GET'])
def get_player_from_username(request):

    username = request.GET.get('username', '')
    game_id = request.GET.get('game_id', '')

    query_return = query_get_game_player(username, game_id)

    # return
    return JsonResponse(players_to_JSON(query_return), safe=False)