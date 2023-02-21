from datetime import datetime
from django.db import connection
from security import encrypt_password, check_encrypted_password

import sys, os
sys.path.append(os.path.abspath("../survivor/survivor_app"))
from constants import *

################################################ Start of General Queries #############################################################

def set_schema():
    query = 'SET SEARCH_PATH to survivor, public;'
    cursor = connection.cursor()
    cursor.execute(query)

def query_check_username_exists(username):
    set_schema()

    query = "SELECT password " 
    query += "FROM Account "
    query += "WHERE username='" + username + "';"

    cursor = connection.cursor()
    cursor.execute(query)
    login_response = cursor.fetchone()
    return login_response

def query_auth_username_password(username, password, hashed_password):
    set_schema()

    if check_encrypted_password(password, hashed_password) == True:
        query = "SELECT id " 
        query += "FROM Account "
        query += "WHERE username='" + username + "' AND password='" + hashed_password + "';"

        cursor = connection.cursor()
        cursor.execute(query)
        login_response = cursor.fetchone()
        return login_response
    else:
        # should return None
        query = "SELECT id " 
        query += "FROM Account "
        query += "WHERE username='" + username + "' AND password='" + hashed_password + "';"

        cursor = connection.cursor()
        cursor.execute(query)
        login_response = cursor.fetchone()
        return

def query_create_account(username, password, name, discord, avatar, bio):
    set_schema()

    query = "INSERT INTO Account " 
    query += "VALUES ("
    query += "DEFAULT" + ", "
    query += "'" + username + "', "
    query += "'" + password + "', "
    query += "'" + name + "', "
    query += "'" + discord + "', "
    query += "'" + avatar + "', "
    query += "'" + bio + "');"
    cursor = connection.cursor()
    cursor.execute(query)

    return

def query_get_account_info(username):
    set_schema()

    query = "SELECT username, name, bio, discord_name, avatar " 
    query += "FROM Account "
    query += "WHERE username='" + username + "';"

    cursor = connection.cursor()
    cursor.execute(query)
    login_response = cursor.fetchone()

    return login_response

def query_get_challenge(id):
    set_schema()
    query = "SELECT * FROM Challenge WHERE id=" + str(id) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    query_response = cursor.fetchone()
    
    # returns a tuple or None
    return query_response

def query_get_challenge_by_round_type(round_type):
    set_schema()
    query = "SELECT id, name, type, description, means, icon FROM Challenge WHERE type=" + str(round_type) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    query_response = cursor.fetchall()
    
    # returns a tuple or None
    return query_response

def query_get_account_id_from_name(username):
    set_schema()
    query = "SELECT id " 
    query += "FROM Account "
    query += "WHERE username='" + username + "';"

    cursor = connection.cursor()
    cursor.execute(query)
    response = cursor.fetchone()

    return response

def query_get_challenge_name_by_id(challenge_id):
    set_schema()

    query = "SELECT name FROM Challenge WHERE id = " + str(challenge_id) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    response = cursor.fetchone()
    return response

def query_get_account_name_by_player_id(player_id):
    set_schema()

    query = "SELECT name FROM Player LEFT JOIN Account ON Player.account_id = Account.id WHERE Player.id = " + str(player_id) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    response = cursor.fetchone()
    return response

def query_get_tribe_colour_by_id(tribe_id):
    set_schema()

    query = "SELECT colour FROM Tribe WHERE id = "+ str(tribe_id) +  ";"

    cursor = connection.cursor()
    cursor.execute(query)
    response = cursor.fetchone()
    return response

def query_set_players_tribe_id(players_list, tribe_id):
    set_schema()

    query = "UPDATE Player SET tribe_id = "+ str(tribe_id) +  " WHERE ("

    # Take list of player_ids and update all Players to have tribe_id
    for i in range(len(players_list)):
        query += "id = " + str(players_list[i])
        if i != len(players_list) - 1:
            query += " OR "
    
    query += ") AND is_still_playing = TRUE;"

    cursor = connection.cursor()
    cursor.execute(query)
    return True

def query_check_player_still_playing(game_id, username):
    set_schema()

    query = "SELECT is_still_playing, is_admin " 
    query += "FROM AccountPlayerGame "
    query += "WHERE game_id=" + str(game_id) + " AND username='" + username + "';"

    cursor = connection.cursor()
    cursor.execute(query)
    response = cursor.fetchone()

    return response[0], response[1]

def query_get_player_idol_count(game_id, username):
    set_schema()

    query = "SELECT idol_count " 
    query += "FROM Player, Account "
    query += "WHERE Account.id = Player.account_id AND Account.username = '" + username + "' AND game_id = "+ str(game_id) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    response = cursor.fetchone()

    return response[0]

def query_increment_idol(game_id, username):
    set_schema()

    query = "UPDATE Player " 
    query += "SET idol_count = idol_count + 1 "
    query += "FROM Account "
    query += "WHERE Account.id = Player.account_id AND Account.username = '" + username + "' AND game_id = "+ str(game_id) + ";"

    cursor = connection.cursor()
    cursor.execute(query)

    return True

def query_decrement_idol(game_id, username):
    set_schema()

    query = "UPDATE Player " 
    query += "SET idol_count = idol_count - 1 "
    query += "FROM Account "
    query += "WHERE Account.id = Player.account_id AND Account.username = '" + username + "' AND game_id = "+ str(game_id) + ";"

    cursor = connection.cursor()
    cursor.execute(query)

    return True

def query_get_player_id_by_username(game_id, username):
    set_schema()

    query = "SELECT player_id FROM AccountPlayerGame WHERE username = '" + username + "' AND game_id = "+ str(game_id) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    response = cursor.fetchone()

    return response

################################################ End of General Queries #############################################################

################################################ Start of Game Queries #############################################################

def query_get_game_info(game_id):
    set_schema()

    query = "SELECT  id, name, password, discord_link, num_rounds_played, game_stage, is_active, joinable, num_players, num_players_left FROM Game LEFT JOIN GameNumberPlayers ON Game.id = GameNumberPlayers.game_id LEFT JOIN GameNumberPlayersLeft ON Game.id = GameNumberPlayersLeft.game_id WHERE Game.id = "+ str(game_id) +  ";"

    cursor = connection.cursor()
    cursor.execute(query)
    login_response = cursor.fetchone()

    return login_response

def query_get_game_current_player(game_id, username):
    set_schema()

    # query = "SELECT * From Player WHERE game_id = "+ str(game_id) +  " AND account_id = " + account_id + ";"
    query = "SELECT name,discord_name,avatar,idol_count,is_still_playing,is_admin,tribe_id,Player.id AS player_id, (SELECT colour from Tribe WHERE id = tribe_id) FROM Player LEFT JOIN Account ON account.id = player.account_id WHERE game_id = "+ str(game_id) +  " AND Account.username = \'" + username + "\';"

    cursor = connection.cursor()
    cursor.execute(query)
    login_response = cursor.fetchone()

    return login_response

def query_get_game_players(game_id):
    set_schema()

    query = "SELECT player.id AS player_id, name, discord_name, avatar, bio, is_still_playing, tribe_id, username, is_admin, (SELECT colour from Tribe WHERE id = tribe_id) FROM Player LEFT JOIN Account ON player.account_id = account.id WHERE game_id = "+ str(game_id) +  " ORDER BY is_still_playing DESC, tribe_id, name;"

    cursor = connection.cursor()
    cursor.execute(query)
    response = cursor.fetchall()

    return response

def query_get_game_player(username, game_id):
    set_schema()

    query = "SELECT player.id AS player_id, name, discord_name, avatar, bio, is_still_playing, tribe_id, username, is_admin, (SELECT colour from Tribe WHERE id = tribe_id) FROM Player LEFT JOIN Account ON player.account_id = account.id WHERE username = \'" + username + "\' AND game_id = "+ str(game_id) +  ";"

    cursor = connection.cursor()
    cursor.execute(query)
    response = cursor.fetchall()

    return response

def query_get_active_game_players(game_id):
    set_schema()

    query = "SELECT player.id AS player_id, name, discord_name, avatar, bio, is_still_playing, tribe_id, username, is_admin, (SELECT colour from Tribe WHERE id = tribe_id) FROM Player LEFT JOIN Account ON player.account_id = account.id WHERE game_id = "+ str(game_id) +  " AND is_still_playing = TRUE;"

    cursor = connection.cursor()
    cursor.execute(query)
    login_response = cursor.fetchall()

    return login_response

def query_get_current_games(username):
    set_schema()

    query = "SELECT * " 
    query += "FROM AccountPlayerGame "
    query += " WHERE username='" + str(username) + "'"
    query += " AND ((is_active=TRUE) OR (is_active=FALSE AND joinable=TRUE))"
    query += ";"

    cursor = connection.cursor()
    cursor.execute(query)
    query_response = cursor.fetchall()
    
    return query_response
    
def query_get_completed_games(username):
    set_schema()

    query = "SELECT * " 
    query += " FROM AccountPlayerGame "
    query += " WHERE username='" + str(username) + "'"
    query += " AND is_active=FALSE"
    query += " AND joinable=FALSE"
    query += ";"

    cursor = connection.cursor()
    cursor.execute(query)
    query_response = cursor.fetchall()
    
    return query_response

def query_get_game_id_from_name(name):
    set_schema()
    query = "SELECT id " 
    query += "FROM Game "
    query += "WHERE name='" + name + "';"

    cursor = connection.cursor()
    cursor.execute(query)
    response = cursor.fetchone()

    return response

def query_create_player(account_id, game_id, is_admin):
    set_schema()
    query = "INSERT INTO Player " 
    query += "VALUES ("
    query += "DEFAULT" + ", "
    query += "" + str(game_id) + ", "
    query += "" + str(account_id) + ", "
    query += "" + str(is_admin) + ", "
    query += "'" + str(True) + "', "
    query += "" + str(0) + ","
    query += "'" + str(False) + "', "
    query += "DEFAULT" + ");"

    cursor = connection.cursor()
    cursor.execute(query)

    # get player id
    query = "SELECT id " 
    query += "FROM Player "
    query += "WHERE game_id=" + str(game_id) + " AND account_id=" + str(account_id) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    response = cursor.fetchone()
    
    return response

def query_create_game(name, hashed_password, discord):
    set_schema()

    # create game
    query = "INSERT INTO Game " 
    query += "VALUES ("
    query += "DEFAULT" + ", "
    query += "'" + name + "', "
    query += "'" + hashed_password + "', "
    query += "'" + discord + "', "
    query += "" + str(0) + ", "
    query += "" + str(GAME_STAGE_TRIBE) + ", "
    query += "" + str(False) + ", "
    query += "" + str(True) + ");"
    cursor = connection.cursor()
    cursor.execute(query)

    return 

def query_check_game_exists(name):
    set_schema()

    query = "SELECT password " 
    query += "FROM Game "
    query += "WHERE name='" + name + "';"

    cursor = connection.cursor()
    cursor.execute(query)
    response = cursor.fetchone()
    return response

def query_auth_game(name, password, hashed_password):
    set_schema()

    if check_encrypted_password(password, hashed_password) == True:
        query = "SELECT id, joinable " 
        query += "FROM Game "
        query += "WHERE name='" + name + "';"

        cursor = connection.cursor()
        cursor.execute(query)
        login_response = cursor.fetchone()
        return login_response
    else:
        return None

def query_check_account_in_game(account_id, game_id):
    set_schema()

    query = "SELECT id " 
    query += "FROM Player "
    query += "WHERE game_id=" + str(game_id) + " AND account_id=" + str(account_id) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    login_response = cursor.fetchone()
    return login_response

def query_get_game_num_players(game_id):
    set_schema()

    query = "SELECT num_players " 
    query += "FROM AccountPlayerGame "
    query += "WHERE game_id=" + str(game_id) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    login_response = cursor.fetchone()
    return login_response

def query_start_game(game_id):
    set_schema()

    query = "UPDATE Game SET is_active=TRUE, joinable=FALSE WHERE id="+ str(game_id) +  ";"

    cursor = connection.cursor()
    cursor.execute(query)
    return True

def query_end_game(game_id):
    set_schema()

    query = "UPDATE Game SET is_active=FALSE, joinable=FALSE WHERE id="+ str(game_id) +  ";"

    cursor = connection.cursor()
    cursor.execute(query)
    return True

def query_create_game_tribe(game_id, colour):
    set_schema()

    query = "INSERT INTO Tribe "
    query += "VALUES (DEFAULT, "+ str(game_id) +  ", " + str(colour) +  ");"

    cursor = connection.cursor()
    cursor.execute(query)
    return True

def query_get_tribe_id_from_game(game_id, colour):
    set_schema()

    query = "SELECT id FROM Tribe WHERE game_id = "+ str(game_id) +  " AND colour = " + str(colour) +  ";"

    cursor = connection.cursor()
    cursor.execute(query)
    login_response = cursor.fetchone()
    return login_response[0]

def query_set_game_stage(game_id, stage):
    set_schema()

    query = "UPDATE Game SET game_stage=" + str(stage) + " WHERE id=" + str(game_id) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    return True

def query_remove_idols(game_id):
    set_schema()

    query = "UPDATE Player SET idol_count=0 WHERE game_id=" + str(game_id) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    return True

def query_conclude_game(game_id):
    query_set_game_stage(game_id, GAME_STAGE_COMPLETE)
    query_end_game(game_id)

################################################ End of Game Queries #############################################################

################################################ Start of Round Queries #############################################################

def query_get_game_rounds(game_id):
    set_schema()

    query = "SELECT * FROM Round WHERE game_id = "+ str(game_id) +  ";"

    cursor = connection.cursor()
    cursor.execute(query)
    login_response = cursor.fetchall()

    return login_response

def query_get_round_info(game_id, round_num):
    set_schema()

    query = "SELECT * FROM Round WHERE game_id = " + str(game_id) + "AND round_num = " + str(round_num) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    query_response = cursor.fetchone()

    return query_response

def query_get_latest_round(game_id):
    set_schema()

    query = "SELECT * FROM Round WHERE game_id = "+ str(game_id) +  "ORDER BY round_num DESC LIMIT 1;"

    cursor = connection.cursor()
    cursor.execute(query)
    query_response = cursor.fetchone()

    return query_response

def query_create_round(game_id, round_num, type):
    set_schema()

    query = "INSERT INTO Round (round_num, game_id, phase, type, day)"
    query += "VALUES ( " + str(round_num) + ", " + str(game_id) + ", 0, " + str(type) + ", now()::DATE AT time zone 'EST');"

    cursor = connection.cursor()
    cursor.execute(query)
    return True

def query_increment_rounds_played(game_id):
    set_schema()

    query = "UPDATE Game SET num_rounds_played = num_rounds_played + 1 WHERE id = "+ str(game_id) +  ";"

    cursor = connection.cursor()
    cursor.execute(query)

    return 

def query_advance_round(game_id, round_num, phase):
    set_schema()

    query = "UPDATE Round SET phase=" + str(phase) + " WHERE game_id=" + str(game_id) + "AND round_num=" + str(round_num) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    return True

def query_set_round_type(game_id, round_num, type):
    set_schema()

    query = "UPDATE Round SET type=" + str(type) + " WHERE game_id=" + str(game_id) + "AND round_num=" + str(round_num) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    return True

def query_set_round_idol(game_id, round_num, idol_num):
    set_schema()

    query = "UPDATE Round SET idol_roll=" + str(idol_num) + " WHERE game_id=" + str(game_id) + "AND round_num=" + str(round_num) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    return True

def query_get_votable_players(game_id):
    set_schema()

    query = "SELECT player_id, username, account_name, discord_name, avatar, is_immune "
    query += "FROM AccountPlayerGame "
    query += "WHERE game_id=" + str(game_id) + " AND is_still_playing = TRUE AND is_immune = FALSE"
    query += ";"

    cursor = connection.cursor()
    cursor.execute(query)
    login_response = cursor.fetchall()

    return login_response

def query_get_immune_players(game_id):
    set_schema()

    query = "SELECT player_id, username, account_name, discord_name, avatar, is_immune "
    query += "FROM AccountPlayerGame "
    query += "WHERE game_id=" + str(game_id) + " AND is_still_playing = TRUE AND is_immune = TRUE"
    query += ";"

    cursor = connection.cursor()
    cursor.execute(query)
    login_response = cursor.fetchall()

    return login_response

def query_get_all_players(game_id):
    set_schema()

    query = "SELECT player_id, username, account_name, discord_name, avatar, is_immune, is_still_playing "
    query += "FROM AccountPlayerGame "
    query += "WHERE game_id=" + str(game_id) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    response = cursor.fetchall()

    return response

def query_get_all_player_idols(game_id):
    set_schema()

    query = "SELECT username, idol_count "
    query += "FROM AccountPlayerGame "
    query += "WHERE game_id=" + str(game_id) + " AND is_still_playing = TRUE AND is_immune = FALSE"
    query += ";"

    cursor = connection.cursor()
    cursor.execute(query)
    response = cursor.fetchall()

    return response

def query_eliminate_player(game_id, round_num, username):
    set_schema()

    player_id = query_get_player_id_by_username(game_id, username)[0]

    # Eliminates Player by id
    query = "UPDATE Player " 
    query += "SET is_still_playing=FALSE "
    query += f"WHERE id = {player_id}"
    cursor = connection.cursor()
    cursor.execute(query)

    # Set eliminated player in round
    query = "UPDATE Round " 
    query += "SET eliminated_player= " + str(player_id) + " "
    query += f"WHERE round_num = {round_num} and game_id = {game_id};"
    cursor = connection.cursor()
    cursor.execute(query)

    return True

def query_get_eliminated_player(game_id, round_num):
    if(int(round_num) == 0):
        return ["No One"]

    set_schema()

    query = "SELECT AccountPlayerGame.account_name "
    query += "FROM Round, AccountPlayerGame "
    query += "WHERE Round.game_id=" + str(game_id) + " AND Round.round_num = " + str(round_num) + " AND Round.game_id=AccountPlayerGame.game_id" + " AND eliminated_player=player_id" 
    query += ";"
    cursor = connection.cursor()
    cursor.execute(query)
    response = cursor.fetchone()

    return response

def query_add_challenge_to_round(game_id, round_num, challenge_id):
    set_schema()

    query = "UPDATE Round SET challenge_id=" + str(challenge_id) + " WHERE game_id=" + str(game_id) + "AND round_num=" + str(round_num) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    return

def query_get_tribes_from_game(game_id):
    set_schema()

    query = "SELECT id, colour FROM Tribe WHERE game_id = " + str(game_id) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    login_response = cursor.fetchall()
    return login_response

def query_get_players_from_game(game_id):
    set_schema()

    query = "SELECT username, account_name "
    query += "FROM AccountPlayerGame "
    query += "WHERE game_id=" + str(game_id) + " AND is_still_playing = TRUE"
    query += ";"

    cursor = connection.cursor()
    cursor.execute(query)
    login_response = cursor.fetchall()

    return login_response

def query_update_round_individual_winner(game_id, round_num, player_id):
    set_schema()

    query = "UPDATE Round SET winning_player=" + str(player_id) + " WHERE game_id=" + str(game_id) + "AND round_num=" + str(round_num) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    return

def query_update_round_tribe_winner(game_id, round_num, tribe_id):
    set_schema()

    query = "UPDATE Round SET winning_tribe=" + str(tribe_id) + " WHERE game_id=" + str(game_id) + "AND round_num=" + str(round_num) + ";"

    cursor = connection.cursor()
    cursor.execute(query)
    return

def query_update_individual_immunity(game_id, player_id):
    set_schema()

    query = "UPDATE Player SET is_immune=TRUE WHERE game_id=" + str(game_id) + "AND id=" + str(player_id) + ";"
    cursor = connection.cursor()
    cursor.execute(query)

    query = "UPDATE Player SET is_immune=FALSE WHERE game_id=" + str(game_id) + "AND id!=" + str(player_id) + ";"
    cursor = connection.cursor()
    cursor.execute(query)

    return

def query_update_tribe_immunity(game_id, tribe_id):
    set_schema()

    query = "UPDATE Player SET is_immune=TRUE WHERE game_id=" + str(game_id) + "AND tribe_id=" + str(tribe_id) + ";"
    cursor = connection.cursor()
    cursor.execute(query)

    query = "UPDATE Player SET is_immune=FALSE WHERE game_id=" + str(game_id) + "AND tribe_id!=" + str(tribe_id) + ";"
    cursor = connection.cursor()
    cursor.execute(query)

    return

def query_get_min_tribe_count(game_id):
    set_schema()

    query = "SELECT count(tribe_id) "
    query += "FROM AccountPlayerGame "
    query += "WHERE game_id=" + str(game_id) + " AND is_still_playing = TRUE "
    query += "GROUP BY tribe_id "
    query += "ORDER BY count "
    query += ";"
    cursor = connection.cursor()
    cursor.execute(query)
    return cursor.fetchone()[0]

def query_prep_players_final_council(game_id):
    set_schema()

    # make final 3 not immune 
    query = "UPDATE Player SET is_immune=FALSE WHERE game_id=" + str(game_id) + ";"
    cursor = connection.cursor()
    cursor.execute(query)

    # resurrect all players and make them immune
    query = "UPDATE Player SET is_immune=TRUE AND is_still_playing=TRUE WHERE game_id=" + str(game_id) + "AND is_still_playing=FALSE;"
    cursor = connection.cursor()
    cursor.execute(query)

    return

################################################ End of Round Queries #############################################################