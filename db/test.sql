-- load sample data into the database
SET SEARCH_PATH TO survivor, public;

INSERT INTO Game
VALUES (DEFAULT, 'Test Game 1', 'test', 'https://discord.gg/5Q9z93sN', 0, 0, false, true);

do $$
begin
   for i in 1..12 loop
        INSERT INTO Account
        VALUES (DEFAULT, i, '$pbkdf2-sha256$30000$.b9XSimFcA6BsNaaM4bQmg$8cE.h/xB.3gNdAXqZMx46W77kgTCYUwOqIKXW5JnKUw', i, i, i, i);
        INSERT INTO Player
        VALUES (DEFAULT, 1, i, false, true, 0, false, NULL);
   end loop;
end; 
$$;

-- Make Tribes
INSERT INTO Tribe (game_id, colour)
VALUES
(1, 0), (1, 1);

-- Put players in tribe
do $$
begin
   for i in 1..12 loop
        UPDATE Player
        SET tribe_id = (i % 2) + 1
        WHERE id = i;
   end loop;
end; 
$$;

-- Set One Player to Admin
UPDATE Player
SET is_admin = TRUE
WHERE id = 1;

-- Start Game
UPDATE GAME 
SET is_active = true,
joinable = false,
num_rounds_played = 1;

-- CREATE AND FINISH ROUND 0
INSERT INTO Round
(day, round_num, game_id, phase, type, winning_tribe, idol_roll, challenge_id)
VALUES
(CURRENT_DATE, 0, 1, 8, 0, 1, 1, 4);

--Set Player immunity
UPDATE Player SET is_immune=TRUE WHERE game_id=1 AND tribe_id=1;

-- --Eliminate player 11
-- UPDATE Player SET is_still_playing=FALSE and is_immune = false WHERE game_id=1 AND id=11;

-- CREATE AND FINISH ROUND 1
-- INSERT INTO Round
-- (day, round_num, game_id, phase, type)
-- VALUES
-- (CURRENT_DATE, 1, 1, 1, 0);
-- --Set Player immunity
-- UPDATE Player SET is_immune=TRUE WHERE game_id=1 AND tribe_id=1;

-- --Eliminate player 11
-- UPDATE Player SET is_still_playing=FALSE and is_immune = false WHERE game_id=1 AND id=9;