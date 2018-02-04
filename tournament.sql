-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
---------------------------------------------------------------------

-- Do not throw an error if the database does not exist. 
-- A notice is issued in this case.
DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;

-- connects to the tournament database, drops connection to previous database
\c tournament;

CREATE TABLE players ( player_id SERIAL PRIMARY KEY,
					   name TEXT NOT NULL, -- the player's full name (need not be unique).
					   num_wins INTEGER DEFAULT 0 
					 );

CREATE TABLE matches ( match_id SERIAL, -- should this be made PRIMARY KEY?
					   round_num INTEGER DEFAULT 0, 
					   player1_id INTEGER REFERENCES players (player_id),
					   player2_id INTEGER REFERENCES players (player_id),
					   winner_id INTEGER REFERENCES players (player_id)
					 );

CREATE TABLE rounds ( curr_round INTEGER DEFAULT 0 );

INSERT INTO rounds VALUES (0);
