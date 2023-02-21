import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

# import socket models file
import sys, os
sys.path.append(os.path.abspath("../survivor/survivor_app"))
from socket_models import *
from helpers import *
from psql_queries import *
from round_helpers import *
from round_models import *
from constants import *

# dict of all sessions (key = game_id-round_num, value = [player_vote_tracker, idol_tracker, tie_occured])
all_sessions = dict() 

# define web socket consumer for survivor game
class SurvivorConsumer(WebsocketConsumer):

    # accept all connection requests
    def connect(self):
        # Accept socket connection
        self.accept()
        
        # get query url data
        game_id = self.scope['url_route']['kwargs']['game_id']
        round_num = self.scope['url_route']['kwargs']['round_num']
        session_key = str(game_id) + "-" + str(round_num)
        username = self.scope['url_route']['kwargs']['username']
        round_info = query_get_round_info(game_id, round_num)
        round_type = round_info[5]
        round_challenge = round_info[10]
        round_idol = round_info[9]

        # check if user is still in the game
        user_still_playing, is_admin = query_check_player_still_playing(game_id, username)
        if(not user_still_playing):
            self.send_payload(PAYLOAD_NOT_PLAYING, game_id, round_num, to_client = True, to_group = False)
            if(not is_admin and round_type != ROUND_TYPE_FINAL_3):
                return

        # get round info 
        round_phase = query_get_round_info(game_id, round_num)[4]

        # Join Django Channel room group
        self.room_name = 'gameid' + game_id + '-roundnum' + round_num
        self.room_group_name = 'group_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        # Send a return appropriate payload back to the client
        if(round_phase == ROUND_PHASE_INIT):
            self.send_payload(PAYLOAD_INFO, game_id, round_num, to_client = True, to_group = False)
        elif(round_phase == ROUND_PHASE_COUNCIL_START):
            # return list players who can be voted out in tribal council 
            while(session_key not in all_sessions):
                pass
            votable_players, votable_players_json = get_votable_players(game_id, round_type, all_sessions[session_key][INDEX_VOTE_TRACKER])
            # send payload to client
            self.send_payload(PAYLOAD_VOTE, game_id, round_num, to_client = True, to_group = False, votable_players = votable_players_json)
        elif(round_phase == ROUND_PHASE_COUNCIL_IDOLS):
            # determine number of idols for each player and return
            player_idols = query_get_all_player_idols(game_id)
            player_idols_dict = player_idols_to_dict(player_idols)
            self.send_payload(PAYLOAD_VOTE_IDOLS, game_id, round_num, to_client = True, to_group = False, player_idols = player_idols_dict)
        # elif(round_phase == ROUND_PHASE_COUNCIL_REVEAL):
            # dont need to
        elif(round_phase == ROUND_PHASE_CHALLENGE_START):
            # populate council tab
            if(round_type != ROUND_TYPE_FINAL_3): # Final 3 does not have eliminated player
                player_username = query_get_eliminated_player(game_id, round_num)[0]
                self.send_payload(PAYLOAD_VOTE_ELIMINATED, game_id, round_num, to_client = True, to_group = False, eliminated_player = player_username)
            else:
                self.send_payload(PAYLOAD_EVENT, game_id, round_num, to_client = True, to_group = False, event_message = determine_event_message(EVENT_PRECOUNCIL_FINAL))

            self.send_payload(PAYLOAD_INFO, game_id, round_num, to_client = True, to_group = False)
        elif(round_phase == ROUND_PHASE_CHALLENGE_REVEAL):
            # populate council tab
            if(round_type != ROUND_TYPE_FINAL_3): # Final 3 does not have eliminated player
                player_username = query_get_eliminated_player(game_id, round_num)[0]
                self.send_payload(PAYLOAD_VOTE_ELIMINATED, game_id, round_num, to_client = True, to_group = False, eliminated_player = player_username)
            else:
                self.send_payload(PAYLOAD_EVENT, game_id, round_num, to_client = True, to_group = False, event_message = determine_event_message(EVENT_PRECOUNCIL_FINAL_CHALLENGE))
            self.send_payload(PAYLOAD_INFO, game_id, round_num, to_client = True, to_group = False)

            #populate challenge tab
            challenge = challenge_to_dict(query_get_challenge(round_challenge))

            if(round_type == ROUND_TYPE_TRIBE):
                tribes = query_get_tribes_from_game(game_id)
                self.send_payload(PAYLOAD_CHALLENGE, game_id, round_num, to_client = True, to_group = False, challenge=challenge, challenge_tribes=tribes)
            # round type == INDIVIDUAL, FINAL 4, FINAL 3
            else:
                players = query_get_players_from_game(game_id)
                self.send_payload(PAYLOAD_CHALLENGE, game_id, round_num, to_client = True, to_group = False, challenge=challenge, challenge_players=players)
        elif(round_phase == ROUND_PHASE_IDOL_START):
            # populate council tab
            player_username = query_get_eliminated_player(game_id, round_num)[0]
            self.send_payload(PAYLOAD_VOTE_ELIMINATED, game_id, round_num, to_client = True, to_group = False, eliminated_player = player_username)
            self.send_payload(PAYLOAD_INFO, game_id, round_num, to_client = True, to_group = False)

            #populate challenge tab
            challenge = challenge_to_dict(query_get_challenge(round_challenge))
            self.send_payload(PAYLOAD_CHALLENGE, game_id, round_num, to_client = True, to_group = False, challenge=challenge)

            if(round_type == ROUND_TYPE_INDIVIDUAL):
                eliminated_player_id = round_info[6]
                name = query_get_account_name_by_player_id(eliminated_player_id)[0]
                self.send_payload(PAYLOAD_CHALLENGE_WINNER, game_id, round_num, to_client = True, to_group = False, challenge_winner = name)
            else:
                winning_tribe_id = round_info[7]
                tribe_name = query_get_tribe_colour_by_id(winning_tribe_id)[0]
                tribe_name_str = 'Orange Tribe' if (tribe_name == TRIBE_ORANGE) else 'Purple Tribe'
                self.send_payload(PAYLOAD_CHALLENGE_WINNER, game_id, round_num, to_client = True, to_group = False, challenge_winner = tribe_name_str)
        elif(round_phase == ROUND_PHASE_COMPLETE):
            # populate council tab
            player_username = query_get_eliminated_player(game_id, round_num)[0]
            self.send_payload(PAYLOAD_VOTE_ELIMINATED, game_id, round_num, to_client = True, to_group = False, eliminated_player = player_username)
            self.send_payload(PAYLOAD_INFO, game_id, round_num, to_client = True, to_group = False)

            #populate challenge tab
            challenge = challenge_to_dict(query_get_challenge(round_challenge))
            self.send_payload(PAYLOAD_CHALLENGE, game_id, round_num, to_client = True, to_group = False, challenge=challenge)

            if(round_type == ROUND_TYPE_TRIBE):
                winning_tribe_id = round_info[7]
                tribe_name = query_get_tribe_colour_by_id(winning_tribe_id)[0]
                tribe_name_str = 'Orange Tribe' if (tribe_name == TRIBE_ORANGE) else 'Purple Tribe'
                self.send_payload(PAYLOAD_CHALLENGE_WINNER, game_id, round_num, to_client = True, to_group = False, challenge_winner = tribe_name_str)
            # round type == INDIVIDUAL, FINAL 4, FINAL 3
            else:
                eliminated_player_id = round_info[6]
                name = query_get_account_name_by_player_id(eliminated_player_id)[0]
                self.send_payload(PAYLOAD_CHALLENGE_WINNER, game_id, round_num, to_client = True, to_group = False, challenge_winner = name)
            
            # final 4 and final 3 tab don't have idol page
            if(round_type != ROUND_TYPE_FINAL_4 and round_type != ROUND_TYPE_FINAL_3):
                # populate idol tab
                self.send_payload(PAYLOAD_IDOL_REVEAL, game_id, round_num, to_client = False, to_group = True, idol_result = round_idol)
        elif(round_phase == ROUND_PHASE_FINAL_COUNCIL):
            # populate challenge tab
            challenge = challenge_to_dict(query_get_challenge(round_challenge))
            self.send_payload(PAYLOAD_CHALLENGE, game_id, round_num, to_client = True, to_group = False, challenge=challenge)
            eliminated_player_id = round_info[8]
            name = query_get_account_name_by_player_id(eliminated_player_id)[0]
            self.send_payload(PAYLOAD_CHALLENGE_WINNER, game_id, round_num, to_client = True, to_group = False, eliminated_player = name)

            # send voting payload
            # return list players who can be voted to win the game
            while(session_key not in all_sessions):
                pass
            if (all_sessions[session_key][INDEX_VOTE_TRACKER]):
                votable_players, votable_players_json = get_all_players_for_final_vote(game_id)
                # send payload to client
                self.send_payload(PAYLOAD_VOTE, game_id, round_num, to_client = True, to_group = False, votable_players = votable_players_json)
        else: 
            self.send_payload(PAYLOAD_INFO, game_id, round_num, to_client = True, to_group = False)

        return

    # disconnect when requested
    def disconnect(self, code):
        # Disconnect room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        return
        
    # receive data from clients and perform action based on type
    def receive(self, text_data):
        data_json = json.loads(text_data)
        game_id = data_json['game_id']
        round_num = data_json['round_num']
        username = data_json['username']
        session_key = str(game_id) + "-" + str(round_num)
        round_info = query_get_round_info(game_id, round_num)
        round_type = round_info[5]
        round_challenge = round_info[10]

        # determine received message TYPE
        if(data_json['type'] == MESSAGE_START_ROUND):
            event_occured = self.check_events_precouncil(game_id, round_info)
            # pre-council event = skip council/voting
            if(not event_occured):
                query_advance_round(game_id, round_num, ROUND_PHASE_COUNCIL_START)
                # return list players who can be voted out in tribal council 
                votable_players, votable_players_json = get_votable_players(game_id, round_type, None, round_type != ROUND_TYPE_TRIBE)
                # these are the players that will be casting votes as well, so keep track of them
                # check if session exists, since it will contain the current round's player_vote_tracker
                if (session_key not in all_sessions):
                    all_sessions[session_key] = [initialize_vote_tracker(votable_players), None, False]

                # add immune players outside of get_votable_players for individual rounds
                votable_players, votable_players_json = attach_immunity_to_players(game_id, round_type, votable_players, all_sessions[session_key][INDEX_VOTE_TRACKER])
                # send payload to client
                self.send_payload(PAYLOAD_VOTE, game_id, round_num, to_client = False, to_group = True, votable_players = votable_players_json)
            # event occured
            else:
                if (session_key not in all_sessions):
                    all_sessions[session_key] = [None, None, False]
                # return to FE
                self.send_payload(PAYLOAD_VOTE_ELIMINATED, game_id, round_num, to_client = False, to_group = True, eliminated_player = "No One")
                self.send_payload(PAYLOAD_INFO, game_id, round_num, to_client = False, to_group = True)

        elif(data_json['type'] == MESSAGE_VOTE_SENT):
            # update voted player
            if(all_sessions[session_key][INDEX_VOTE_TRACKER][username]['has_voted'] == False):
                voted_player_username = data_json['message']
                all_sessions[session_key][INDEX_VOTE_TRACKER][voted_player_username]['votes_against'] += 1
                # mark voting player as complete
                all_sessions[session_key][INDEX_VOTE_TRACKER][username]['has_voted'] = True
            # send status back to client as vote received
            self.send_payload(PAYLOAD_VOTE_RECEIVED, game_id, round_num, to_client = True, to_group = False)
            # send status to group about current number of votes left
            votes_left = get_votes_left(all_sessions[session_key][INDEX_VOTE_TRACKER])
            self.send_payload(PAYLOAD_VOTES_LEFT, game_id, round_num, to_client = False, to_group = True, votes_left = votes_left)

        elif(data_json['type'] == MESSAGE_VOTE_IDOL):
            query_advance_round(game_id, round_num, ROUND_PHASE_COUNCIL_IDOLS)
            # determine number of idols for each player and return
            player_idols = query_get_all_player_idols(game_id)
            player_idols_dict = player_idols_to_dict(player_idols)
            self.send_payload(PAYLOAD_VOTE_IDOLS, game_id, round_num, to_client = False, to_group = True, player_idols = player_idols_dict)

        elif(data_json['type'] == MESSAGE_VOTE_USE_IDOL):
            query_decrement_idol(game_id, username)
            if(all_sessions[session_key][INDEX_VOTE_TRACKER][username]['idol_played'] == COUNCIL_NOT_IMMUNE):
                all_sessions[session_key][INDEX_VOTE_TRACKER][username]['idol_played'] = COUNCIL_IMMUNE
            self.send_payload(PAYLOAD_IDOL_USED, game_id, round_num, to_client = False, to_group = True, idol_played_by = username)

        elif(data_json['type'] == MESSAGE_VOTE_REVEAL):
            # send back vote tracker to be displayed by FE
            self.send_payload(PAYLOAD_ALL_VOTES, game_id, round_num, to_client = False, to_group = True, vote_tracker = all_sessions[session_key][INDEX_VOTE_TRACKER])
            # determine player(s) with most votes, take into account idols played
            most_votes = get_persons_with_most_votes(all_sessions[session_key][INDEX_VOTE_TRACKER])
             
             # if one person voted out
            if(len(most_votes) == 1):
                # someone was voted out
                if(round_type != ROUND_TYPE_FINAL_3):
                    # set player as eliminated in db
                    query_eliminate_player(game_id, round_num, most_votes[0])
                    player_username = query_get_account_info(most_votes[0])[1]
                    
                    # return to FE
                    self.send_elimination_payload(game_id, round_num, round_info, player_username)
                
                # game is over, we have a winner
                else:
                    # set game winner
                    query_update_round_individual_winner(game_id, round_num, query_get_player_id_by_username(game_id, most_votes[0])[0])
                    # set round in db to be completed
                    query_advance_round(game_id, round_num, ROUND_PHASE_COMPLETE)
                    # set game in db to be over
                    query_conclude_game(game_id)
                    # return to FE new payload type to display winner
                    player_username = query_get_account_info(most_votes[0])[1]
                    self.send_payload(PAYLOAD_VOTE_ELIMINATED, game_id, round_num, to_client = False, to_group = True, eliminated_player = player_username)
                    
            # if tie
            else:
                # if first tie, revote amongst tied UNLESS ROUND_TYPE_FINAL_3, where continually vote until winner
                if(all_sessions[session_key][INDEX_TIE_COUNT] == False):
                    self.send_payload(PAYLOAD_VOTE_TIE, game_id, round_num, to_client = False, to_group = True)
                    # reset round phase in db
                    # record that tie has occured if NOT final 3
                    if(round_type == ROUND_TYPE_FINAL_3):
                        query_advance_round(game_id, round_num, ROUND_PHASE_FINAL_COUNCIL)
                        votable_players, votable_players_json = get_all_players_for_final_vote(game_id)
                    else:
                        all_sessions[session_key][INDEX_TIE_COUNT] = True
                        query_advance_round(game_id, round_num, ROUND_PHASE_COUNCIL_START)
                        # get new list of votable players and remove those not involved in the tie
                        votable_players, votable_players_json = get_votable_players(game_id, round_type, all_sessions[session_key][INDEX_VOTE_TRACKER])
                    votable_players, votable_players_json = immunize_non_tied_players(most_votes, votable_players, all_sessions[session_key][INDEX_VOTE_TRACKER])
                    # create new vote tracker
                    all_sessions[session_key][0] = initialize_vote_tracker(votable_players, existing_idols=True, vote_tracker=all_sessions[session_key][INDEX_VOTE_TRACKER])
                    # send to clients
                    self.send_payload(PAYLOAD_VOTE, game_id, round_num, to_client = False, to_group = True, votable_players = votable_players_json)
                # if second tie, unanimous OR random
                else:
                    # reset round phase in db
                    query_advance_round(game_id, round_num, ROUND_PHASE_COUNCIL_START)
                    # get new list of votable players and remove those who were involved in the first tie
                    votable_players, votable_players_json = get_votable_players(game_id, round_type, all_sessions[session_key][INDEX_VOTE_TRACKER])
                    votable_players, votable_players_json = remove_non_tied_players(most_votes, votable_players)
                    # send to group (admin and players see diff things)
                    self.send_payload(PAYLOAD_VOTE_TIE_AGAIN, game_id, round_num, to_client = False, to_group = True, votable_players = votable_players_json)
            
        elif(data_json['type'] == MESSAGE_UNANIMOUS_ELIMINATION):
            elim_player = data_json['message']
            query_eliminate_player(game_id, round_num, elim_player)
            self.send_elimination_payload(game_id, round_num, round_info, elim_player)

        elif(data_json['type'] == MESSAGE_RANDOM_ELIMINATION):
            players_list = remove_tied_idoled_players(all_sessions[session_key][INDEX_VOTE_TRACKER])
            elim_player = choose_random_player(players_list)
            query_eliminate_player(game_id, round_num,  elim_player)
            player_username = query_get_account_info(elim_player)[1]
            self.send_elimination_payload(game_id, round_num, round_info, player_username)

        elif(data_json['type'] == MESSAGE_RANDOMIZE_CHALLENGE):
            query_advance_round(game_id, round_num, ROUND_PHASE_CHALLENGE_REVEAL)
            # get challenges based on round type
            possible_challenges = query_get_challenge_by_round_type(round_type)
            # shuffle and get random challenge from list
            challenge = challenge_to_dict(choose_random_player(possible_challenges))
            challenge_id = challenge['id']
            # put challenge in Round table in db
            query_add_challenge_to_round(game_id, round_num, challenge_id)

            # get list of tribes or players active
            if(round_type == ROUND_TYPE_TRIBE):
                tribes = query_get_tribes_from_game(game_id)
                self.send_payload(PAYLOAD_CHALLENGE, game_id, round_num, to_client = False, to_group = True, challenge=challenge, challenge_tribes=tribes)
            else:
                players = query_get_players_from_game(game_id)
                self.send_payload(PAYLOAD_CHALLENGE, game_id, round_num, to_client = False, to_group = True, challenge=challenge, challenge_players=players)

        elif(data_json['type'] == MESSAGE_CHALLENGE_WINNER):         
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # if this is the 1v1 challenge, LOSER player username will be sent in the message and payload, NOT WINNER

            if(round_type == ROUND_TYPE_INDIVIDUAL):
                query_advance_round(game_id, round_num, ROUND_PHASE_IDOL_START)
                player_id = query_get_player_id_by_username(game_id, data_json['message'])[0]
                query_update_round_individual_winner(game_id, round_num, player_id)
                query_update_individual_immunity(game_id, player_id)
                name = query_get_account_name_by_player_id(player_id)[0]
                self.send_payload(PAYLOAD_CHALLENGE_WINNER, game_id, round_num, to_client = False, to_group = True, challenge_winner = name)
            elif(round_type == ROUND_TYPE_TRIBE):
                query_advance_round(game_id, round_num, ROUND_PHASE_IDOL_START)
                query_update_round_tribe_winner(game_id, round_num, data_json['message'])
                query_update_tribe_immunity(game_id, data_json['message'])
                tribe_name = query_get_tribe_colour_by_id(data_json['message'])[0]
                tribe_name_str = 'Orange Tribe' if (tribe_name == TRIBE_ORANGE) else 'Purple Tribe'
                self.send_payload(PAYLOAD_CHALLENGE_WINNER, game_id, round_num, to_client = False, to_group = True, challenge_winner = tribe_name_str)
            elif(round_type == ROUND_TYPE_FINAL_4):
                player_id = query_get_player_id_by_username(game_id, data_json['message'])[0]
                query_update_round_individual_winner(game_id, round_num, player_id)
                name = query_get_account_name_by_player_id(player_id)[0]
                self.send_payload(PAYLOAD_CHALLENGE_WINNER, game_id, round_num, to_client = False, to_group = True, challenge_winner = name)
                # conclude the round
                query_advance_round(game_id, round_num, ROUND_PHASE_COMPLETE)
            elif(round_type == ROUND_TYPE_FINAL_3):
                query_advance_round(game_id, round_num, ROUND_PHASE_FINAL_COUNCIL)
                loser_username = data_json['message']
                query_eliminate_player(game_id, round_num, loser_username)
                self.send_payload(PAYLOAD_CHALLENGE_WINNER, game_id, round_num, to_client = False, to_group = True, eliminated_player = loser_username)

        elif(data_json['type'] == MESSAGE_IDOL_PREDICTION):
            # create idol tracker if one does not exist
            if(all_sessions[session_key][INDEX_IDOL_TRACKER] == None):
                all_sessions[session_key][INDEX_IDOL_TRACKER] = initialize_idol_tracker(game_id)

            # update idol_tracker
            if(all_sessions[session_key][INDEX_IDOL_TRACKER][username]['has_predicted'] == False):
                all_sessions[session_key][INDEX_IDOL_TRACKER][username]['has_predicted'] = True
                idol_prediction = data_json['message']
                all_sessions[session_key][INDEX_IDOL_TRACKER][username]['idol_prediction'] = idol_prediction

            # client payload = vote received
            self.send_payload(PAYLOAD_IDOL_PREDICTION_RECEIVED, game_id, round_num, to_client = True, to_group = False)

            # group payload = counter
            idol_predictions_left = get_idol_predictions_left(all_sessions[session_key][INDEX_IDOL_TRACKER])
            self.send_payload(PAYLOAD_IDOL_PREDICTIONS_LEFT, game_id, round_num, to_client = False, to_group = True, idol_predictions_left = idol_predictions_left)
        
        elif(data_json['type'] == MESSAGE_IDOL_RANDOMIZE):
            # randomize number 1-12
            idol_num = choose_random_number(1,12)
            # update idol counts in db using idol tracker
            if(all_sessions[session_key][INDEX_IDOL_TRACKER] != None):
                update_idol_count(game_id, all_sessions[session_key][INDEX_IDOL_TRACKER], idol_num)
            query_set_round_idol(game_id, round_num, idol_num)
            # group payload = result
            self.send_payload(PAYLOAD_IDOL_REVEAL, game_id, round_num, to_client = False, to_group = True, idol_result = idol_num)
            # conclude the round
            query_advance_round(game_id, round_num, ROUND_PHASE_COMPLETE)

        elif(data_json['type'] == MESSAGE_FINAL_COUNCIL_START):
            # prep vote tracker and get all votable players
            
            # return list players who can be voted out in tribal council 
            # votable_players, votable_players_json = get_votable_players(game_id, round_type, None, True)
            votable_players, votable_players_json = get_all_players_for_final_vote(game_id)

            print(f'Votable Players JSON: {votable_players}')

            # these are the players that will be casting votes as well, so keep track of them
            all_sessions[session_key] = [initialize_vote_tracker(votable_players), None, False]

            # add immune players outside of get_votable_players; TODOTESTING: check when testing if tab is correct
            votable_players, votable_players_json = attach_immunity_for_final_3(votable_players, all_sessions[session_key][INDEX_VOTE_TRACKER])
            # print('Had to initialize vote tracker')

            print(f'Before Payload')
            # send payload to client
            self.send_payload(PAYLOAD_VOTE, game_id, round_num, to_client = False, to_group = True, votable_players = votable_players_json)

        elif(data_json['type'] == MESSAGE_DISCONNECT):
            self.disconnect(1001)

        return

    def send_elimination_payload(self, game_id, round_num, round_info, player_username):
        self.check_events_prechallenge(game_id, round_info)
        query_advance_round(game_id, round_num, ROUND_PHASE_CHALLENGE_START)
                    # Sending PAYLOAD INFO twice because the first one updates UI before elimination.
        self.send_payload(PAYLOAD_INFO, game_id, round_num, to_client = False, to_group = True)
        self.send_payload(PAYLOAD_VOTE_ELIMINATED, game_id, round_num, to_client = False, to_group = True, eliminated_player = player_username)
        self.send_payload(PAYLOAD_INFO, game_id, round_num, to_client = False, to_group = True)

    # send payload back to FE client
    def send_payload(
        self, 
        type, 
        game_id, round_num, 
        to_client, to_group, 
        votable_players = None, 
        votes_left = None, 
        player_idols = None, 
        idol_played_by = None, 
        vote_tracker = None,
        eliminated_player = None,
        challenge = None,
        challenge_tribes = None,
        challenge_players = None,
        challenge_winner = None,
        idol_predictions_left = None,
        idol_result = None,
        event_message = None
    ):

        round_info = query_get_round_info(game_id, round_num)
        payload_message = determine_message(type)
        payload = SocketPayload(type = type, message = payload_message)
        payload.round_info = round_info
        session_key = str(game_id) + "-" + str(round_num)

        # specific client payload data
        if(to_client):
            payload = self.append_payload_data(type, payload, votable_players, votes_left, player_idols, idol_played_by, vote_tracker, eliminated_player, challenge, challenge_tribes, challenge_players, challenge_winner, idol_predictions_left, idol_result, event_message)
            client_payload_json = socket_payload_to_JSON(payload)
            self.send(text_data = client_payload_json)
        
        # specific group payload data, so need to revert any client-specific payload data
        if(to_group):
            payload = self.append_payload_data(type, payload, votable_players, votes_left, player_idols, idol_played_by, vote_tracker, eliminated_player, challenge, challenge_tribes, challenge_players, challenge_winner, idol_predictions_left, idol_result, event_message)
            group_payload_json = socket_payload_to_JSON(payload)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'send_group_payload',
                    'message': group_payload_json
                }
            )

        return

    # send payload to all clients in group
    def send_group_payload(self, event):
        payload_json = event['message']

        # send message to WebSockets clients in group
        self.send(text_data = payload_json)

        return

    # append payload-type specific payload data
    def append_payload_data(self, type, payload, votable_players, votes_left, player_idols, idol_played_by, vote_tracker, eliminated_player, challenge, challenge_tribes, challenge_players, challenge_winner, idol_predictions_left, idol_result, event_message):
        if(type == PAYLOAD_VOTE_RECEIVED):
            payload.vote_received = True
        elif(type == PAYLOAD_VOTE):
            payload.votable_players = votable_players
        elif(type == PAYLOAD_VOTES_LEFT):
            payload.votes_left = votes_left
        elif(type == PAYLOAD_VOTE_IDOLS):
            payload.player_idols = player_idols
        elif(type == PAYLOAD_IDOL_USED):
            payload.idol_played_by = idol_played_by
        elif(type == PAYLOAD_ALL_VOTES):
            payload.all_votes = vote_tracker
        elif(type == PAYLOAD_VOTE_ELIMINATED):
            payload.eliminated_player = eliminated_player
        elif(type == PAYLOAD_VOTE_TIE_AGAIN):
            payload.votable_players = votable_players
        elif(type == PAYLOAD_CHALLENGE):
            payload.challenge = challenge
            payload.challenge_tribes = challenge_tribes
            payload.challenge_players = challenge_players
        elif(type == PAYLOAD_CHALLENGE_WINNER):
            payload.challenge_winner = challenge_winner
            payload.eliminated_player = eliminated_player
        elif(type == PAYLOAD_IDOL_PREDICTIONS_LEFT):
            payload.idol_predictions_left = idol_predictions_left
        elif(type == PAYLOAD_IDOL_REVEAL):
            payload.idol_result = idol_result
        elif(type == PAYLOAD_EVENT):
            payload.message = event_message

        return payload

    # EVENT CHECK - precouncil
    def check_events_precouncil(self, game_id, round_info):
        game_info = query_get_game_info(game_id)

        # things we need from round_info
        round_num = round_info[1]
        round_type = round_info[5]
        # things we need from game_info
        num_players = game_info[8]
        num_players_left = game_info[9]

        # Check for the event
        event_code = EVENT_NONE
        if(round_num == 0):
            event_code = EVENT_PRECOUNCIL_ROUND_0
        elif(num_players_left == 4):
            event_code = EVENT_PRECOUNCIL_FINAL

        if(event_code != EVENT_NONE):
            message = execute_event(event_code, game_id, round_num)
            self.send_payload(PAYLOAD_EVENT, game_id, round_num, to_client = False, to_group = True, event_message = message)
            return True
        return False 

    # EVENT CHECK - prechallenge
    def check_events_prechallenge(self, game_id, round_info):
        game_info = query_get_game_info(game_id)

        print(f'Game Info: {game_info}')
        print(f'Round Info: {round_info}')

        # things we need from round_info
        round_num = round_info[1]
        round_type = round_info[5]
        # things we need from game_info
        num_players = game_info[8]
        num_players_left = game_info[9]

        # Check for the event
        event_code = EVENT_NONE
        if(num_players_left == 4):      # FINAL 4 ROUND
            event_code = EVENT_PRECHALLENGE_FINAL_4
            print("Final 4 PreChallenge")
        elif(num_players >= 18 and round_type == ROUND_TYPE_TRIBE and num_players_left == 15):        # TWO TRIBE SWAPS
            event_code = EVENT_PRECHALLENGE_SWAP
            print("PreChallenge Swap")
        elif(num_players >= 14 and round_type == ROUND_TYPE_TRIBE and num_players_left == 12):        # ONE TRIBE SWAP
            event_code = EVENT_PRECHALLENGE_SWAP
            print("PreChallenge Single Swap")
        elif(round_type == ROUND_TYPE_TRIBE and query_get_min_tribe_count(game_id) == 4):
            event_code = EVENT_PRECHALLENGE_MERGE
            print("PreChallenge Merge")
            
        if(event_code != EVENT_NONE):
            message = execute_event(event_code, game_id, round_num)
            self.send_payload(PAYLOAD_EVENT, game_id, round_num, to_client = False, to_group = True, event_message = message)
            return True

        return False 