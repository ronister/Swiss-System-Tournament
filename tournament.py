#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2, bleach


######### helper function #########

def planNextRound(standings):

    conn = connect()
    c = conn.cursor()

    # 1. increment round number
    c.execute("UPDATE rounds SET curr_round=curr_round+1;")

    # 2. insert matches into "matches" table
    for i in range(0, len(standings), 2):
        p1_id = standings[i][0]
        p2_id = standings[i+1][0]
        c.execute("INSERT INTO matches (round_num, player1_id, player2_id) VALUES ((SELECT curr_round FROM rounds), {}, {});".format(p1_id, p2_id)) 

    conn.commit()
    conn.close()

####################################

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database.
       Reset curr_round from "rounds" table.
       Reset num_wins from "players" table
    """
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM matches;")
    c.execute("UPDATE rounds SET curr_round=0;")
    c.execute("UPDATE players SET num_wins=0;")
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database. """
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM players;")
    #c.execute("UPDATE rounds SET curr_round=0;")
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM players;")
    count = c.fetchall()[0][0] # first column of first (and only) row
    # we can also use: count = c.fetchone()[0]
    conn.close()
    return int(count)


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO players (name) VALUES (%s);", (bleach.clean(name),))
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT p.player_id, p.name, p.num_wins, r.curr_round FROM players AS p, rounds AS r ORDER BY p.num_wins DESC;")
    results = c.fetchall()
    conn.close()

    # make sure we return even number of players, error otherwise.
    if len(results) % 2 != 0:
        raise ValueError("There must be an even number of players.")

    return results

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    c = conn.cursor()

    # 1. make sure "matches" table isn't empty before updating it.
    # if it is empty, planNextRound will insert all matches to it.
    c.execute("SELECT COUNT(*) FROM matches;")                
    count = c.fetchall()[0][0]
    if (int(count) == 0):
        planNextRound(playerStandings())

    # 2. now we are safe to update "matches" table
    # bug in old query - why doen't this work?
    #c.execute("UPDATE matches SET winner_id={} WHERE player1_id={} OR player2_id={};".format(winner, loser, loser))

    # the fixed query
    c.execute("UPDATE matches SET winner_id={winner} WHERE (round_num = (select curr_round from rounds)) AND ((player1_id={winner} AND player2_id={loser}) OR (player1_id={loser} AND player2_id={winner}));".format(winner=winner, loser=loser))

    # 3. update "players" table
    c.execute("UPDATE players SET num_wins=num_wins+1 WHERE player_id=%s;", (bleach.clean(str(winner)),))

    conn.commit()
    conn.close()
  
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    results = []

    standings = playerStandings()
    planNextRound(standings)

    for i in range(0, len(standings), 2):
        p1_id = standings[i][0]
        p1_name = standings[i][1]
        p2_id = standings[i+1][0]
        p2_name = standings[i+1][1]
        results.append((p1_id, p1_name, p2_id, p2_name))

    return results




