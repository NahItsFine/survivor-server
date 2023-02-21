-- Survivor Schema.
-- To only be run to reset the database back to factory settings (empty tables)

DROP SCHEMA IF EXISTS survivor CASCADE;
CREATE SCHEMA survivor;
SET SEARCH_PATH to survivor, public;

SET TIME ZONE 'EST';

-- ENTITY: A virtual survivor account
CREATE TABLE Account (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  password VARCHAR(500) NOT NULL,
  name VARCHAR(50) NOT NULL,
  discord_name VARCHAR(50) NOT NULL,
  avatar VARCHAR NOT NULL,
  bio VARCHAR(500) NOT NULL,
  -- login must be unique
  UNIQUE (username)
);

-- ENTITY: A survivor game.
CREATE TABLE Game (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) UNIQUE,
  password VARCHAR(500) NOT NULL,
  discord_link VARCHAR(50) NOT NULL,
  num_rounds_played INT NOT NULL,
  game_stage INT NOT NULL,
  is_active BOOLEAN NOT NULL, -- represents if game started yet / is not over
  joinable BOOLEAN NOT NULL -- represents if game can be joined (not started yet and still space remaining)
);

-- ENTITY: Account in a game = Player
CREATE TABLE Player (
  id SERIAL PRIMARY KEY,
  game_id INT NOT NULL REFERENCES Game(id),
  account_id INT NOT NULL REFERENCES Account(id),
  is_admin BOOLEAN NOT NULL,
  is_still_playing BOOLEAN NOT NULL,
  idol_count INT NOT NULL,
  is_immune BOOLEAN NOT NULL,
  -- id for tribe, can be NULL for individual stage
  tribe_id INT DEFAULT NULL,
  -- each account can only enter a game once
  UNIQUE (game_id, account_id)
);

-- ENTITY: A survivor tribe.
CREATE TABLE Tribe (
  id SERIAL PRIMARY KEY,
  game_id INT NOT NULL REFERENCES Game(id),
  -- name VARCHAR(50) NOT NULL,
  -- 0 for the first tribe, 1 for the second.
  colour INT NOT NULL
  -- colour VARCHAR(50) NOT NULL,
  -- tribe names must be unique
  -- UNIQUE (name)
);

-- RELATION: in a game, players belong to tribes
-- CREATE TABLE TribePlayers (
--   game_id INT NOT NULL REFERENCES Game(id),
--   tribe_id INT NOT NULL REFERENCES Tribe(id),
--   player_id INT NOT NULL REFERENCES Player(id),
--   -- each player (player id) can be in a tribe once (game id, tribe id)
--   PRIMARY KEY (game_id, tribe_id, player_id)
-- );

-- ENTITY: rounds have a challenge (except for last)
CREATE TABLE Challenge (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  -- 0 = tribe, 1 = individual, 2 = final 4, 3 = tower
  type INT NOT NULL,
  description VARCHAR(500),
  -- i.e a link to a website to play the challenge
  means VARCHAR(500),
  icon VARCHAR(20),
  -- challenge names must be unique
  UNIQUE (name)
);

-- ENTITY: A game round; games consist of rounds
CREATE TABLE Round (
  id SERIAL PRIMARY KEY,
  round_num INT NOT NULL,
  UNIQUE(game_id, round_num),
  game_id INT NOT NULL REFERENCES Game(id),
  day DATE NOT NULL,
  -- definitions are in constants.py
  phase INT NOT NULL,
  -- definitions are in constants.py
  type INT NOT NULL,
  -- winner can be either a player or a tribe
  winning_player INT,
  winning_tribe INT,
  -- not all rounds (i.e first one) will have an elimination
  eliminated_player INT,
  -- not all rounds (i.e last one) will have an idol roll
  idol_roll INT,
  -- not all rounds (i.e last one) will have a challenge
  challenge_id INT REFERENCES Challenge(id)
);

-- VIEW: Number of players in each Game
CREATE VIEW GameNumberPlayers AS 
SELECT 
  g.id AS "game_id", COUNT(p.id) AS "num_players"
FROM Account a, PLAYER p, Game g
WHERE p.account_id = a.id AND p.game_id = g.id
GROUP BY g.id
ORDER BY g.id;

-- VIEW: Number of players LEFT in each Game
CREATE VIEW GameNumberPlayersLeft AS 
SELECT 
  g.id AS "game_id", COUNT(p.id) AS "num_players_left"
FROM Account a, PLAYER p, Game g
WHERE p.account_id = a.id AND p.game_id = g.id AND p.is_still_playing = TRUE
GROUP BY g.id
ORDER BY g.id;

-- VIEW: Account Player Game information in one table
CREATE VIEW AccountPlayerGame AS
SELECT 
  g.id AS "game_id", g.name AS "game_name", g.password AS "game_password", g.discord_link, g.num_rounds_played, g.game_stage, g.is_active, g.joinable, 
  gnp.num_players AS "num_players",
  gnpl.num_players_left AS "num_players_left",
  a.id AS "account_id", a.username, a.name AS "account_name", a.discord_name, a.avatar,
  p.id AS "player_id", p.is_admin, p.is_still_playing, p.idol_count, p.is_immune, p.tribe_id
FROM Account a, PLAYER p, Game g, GameNumberPlayers gnp, GameNumberPlayersLeft gnpl
WHERE p.account_id = a.id AND p.game_id = g.id AND g.id = gnp.game_id AND g.id = gnpl.game_id
ORDER BY g.id, a.id;

-- CHALLENGES
-- type: 0 = tribe, 1 = individual, 2 = final 4, 3 = tower
-- means: i.e a link to a website to play the challenge
INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Scavenger Hunt', 0, 'Winner is Tribe with most pictures of object AND player face in frame posted to a discord channel within 24 hours or first Tribe to finish the entire list.', 'To Be Determined by Game Admin', 'map');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Tribal Tron', 0, 'Rounds: 2v2s first to 3 wins; Winner is first Tribe to 3 Round wins.', 'https://xtremetron.com/', 'directions_bike');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Jeopardy', 0, 'Best 2 of 3, will randomize categories.', 'https://jeopardylabs.com/browse/', 'quiz');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Pokemon Showdown', 0, 'Best of n, where n = number of people on smallest tribe; gen 3 random singles.', 'https://play.pokemonshowdown.com/', 'catching_pokemon');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Typing Competition Relay', 0, '1v1s against opponent on opposite tribe. Best WPM after 1 minute of "sentences" mode wins the round. Best of 3 rounds wins point. Tribe with most points wins.', 'https://www.typingtest.com/', 'keyboard');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Codenames', 0, 'Best of 3.', 'http://codewordsgame.com', 'password');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Pictionary', 0, 'Winning Tribe is one with highest average score, best of 3 matches.', 'https://sketchful.io/', 'gesture');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Generals IO', 0, 'Last Tribe standing, 4v4s, best of 3.', 'http://generals.io/', 'military_tech');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Workout Circuit', 0, 'First Tribe to complete the following exercises in order (1 person per exercise): 50 pushups, 50 situps, 50 squats, 50 jumping jacks, 25 burpees.', 'Video Call', 'fitness_center');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Tribal Human Benchmark', 0, 'Choose random tests. First Tribe to 3 wins.', 'https://humanbenchmark.com/', 'accessibility_new');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Scattergories', 0, 'Best of 3, first Tribe to complete a list of 20 words.', 'https://swellgarfo.com/scattergories/', 'format_list_bulleted');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Arm Endurance', 1, 'Full body in view, standing, nothing to support arm, arm straight up. Last Player standing.', 'Video Call', 'emoji_people');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Ab Endurance', 1, 'Full body in view, side angle, front plank with good form. Last Player standing.', 'Video Call', 'mood_bad');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Poker', 1, 'Texas Hold Em. Last Player standing.', 'https://www.cardzmania.com/games/', 'style');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'President', 1, 'Last Player standing, last place each round is eliminated and winner of previous round goes first.', 'https://www.cardzmania.com/games/', 'style');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Connect 4 Tournament', 1, 'Best of 3 tournament', 'https://c4arena.com', 'blur_on');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Drawing Competition', 1, 'Draw a random object in 10 minutes, all drawings ranked anonymously by Players.', 'https://randomwordgenerator.com/', 'edit');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Jackbox Trivia', 1, 'Best combined placement out of 2 games, tie breaker #1 is best placement of the 2 games, tie breaker #2 is a third game between tied players.', 'Video Stream of Jackbox', 'contact_support');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Hoodie Hustle', 1, 'Most shirts (T-Shirts, Longsleeves, Hoodies, Jackets, etc.) worn on top of each other in 5 minutes. Females have +1 shirt advantage. Tie breaker is number of longsleeve clothing worn.', 'Video Recording', 'checkroom');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Unblock Game', 1, 'Most levels completed in 10 minutes.', 'https://www.xpgameplus.com/games/unblockme/index.html', 'view_comfy');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Tetris', 1, 'Best combined score after 2 games.', 'https://tetris.com/play-tetris', 'image_aspect_ratio');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Tron', 1, 'First to 3 wins.', 'https://xtremetron.com/', 'directions_bike');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Human Benchmark', 1, 'Choose random tests. First Player to 3 wins.', 'https://humanbenchmark.com/', 'accessibility_new');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Sleep Deprivation', 2, 'Longest to go without sleeping wins. Message the chat every 15 minutes as proof.', 'Discord Chat', 'nightlight');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'UNO', 2, 'Best combined placement out of 2 games, tie breaker #1 is best placement of the 2 games, tie breaker #2 is a third game between tied players.', 'https://play.unofreak.com/', 'style');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Bloxors', 2, 'First to 3 wins.', 'https://backyard.co/', 'dashboard');

INSERT INTO Challenge(id, name, type, description, means, icon)
VALUES (DEFAULT, 'Tower', 3, 'Best of 3, winner joins the Final 3.', 'https://www.gamesxl.com/skill/stack-tower', 'reorder');