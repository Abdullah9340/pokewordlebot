"""
    Authors: Mahfuzur Rahman (m236rahm@uwaterloo.ca), Abdullah Abdullah (a55abdul@uwaterloo.ca)
    Date: June 2022
    Description: This is the file that contains the main game functions
    for the Pokewordle bot. 
"""


from embedTemplates import *
import psycopg2
import os
import random
import requests
import json
from dotenv import load_dotenv
from typing import List

load_dotenv()
URL = os.environ.get('URL')

db = psycopg2.connect(URL)
myCursor = db.cursor()

generationEnds = {
    0: 0,
    1: 151,
    2: 251,
    3: 386,
    4: 493,
    5: 649,
    6: 721,
    7: 809,
    8: 898,
}


def game_started(userId: int) -> bool:
    """ Check to see if a user has an ongoing game

    This function fetches a user's row from the database
    to check if they have any ongoing games.

    Args:
        userId (int) : The user's id

    Returns:
        boolean value to indicate if the game has started

    """

    myCursor.execute(
        "SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    if len(rows) == 0:
        return False
    return rows[0][2] != ""


def get_stats(userId: int, name: str) -> Embed:
    """ Fetches the user's stats from the database

    This function fetches the user's stats from the database and 
    returns them if they exist

    Args:
        userId (int) : The user's id
        name (str) : The user's name

    Returns:
        An embedded discord message object holding information
        about the user's stats

    """

    myCursor.execute(
        "SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    if len(rows) == 0:
        return [0, 0, 0, 0, 0, 0]
    stats = rows[0][5]
    embed = stats_embed(name, stats)
    return embed


def game_won_poke_info(userId: int):
    """ Creates a discord embedded game won message

    This function fetches information about the game that is won and
    returns an embedded message object

    Args:
        userId (int) : The user's id

    Returns:
        An embedded discord message object holding information
        about the game
    """

    myCursor.execute(
        "SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    currentPokemon = rows[0][2]
    lives = rows[0][4]
    actual = requests.get(
        f'https://pokeapi.co/api/v2/pokemon/{currentPokemon}')
    actualImage = json.loads(actual.text)['sprites']['front_default']
    res = game_won(currentPokemon, actualImage, lives)
    return res


def game_over_poke_info(userId: int):
    """ Creates a discord embedded game over message

    This function fetches information about the game and
    returns an embedded message object

    Args:
        userId (int) : The user's id

    Returns:
        An embedded discord message object holding information
        about the lost game
    """

    myCursor.execute(
        "SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    currentPokemon = rows[0][2]
    actual = requests.get(
        f'https://pokeapi.co/api/v2/pokemon/{currentPokemon}')
    actualImage = json.loads(actual.text)['sprites']['front_default']
    res = game_over(currentPokemon, actualImage)
    return res


def reset(stats: List[int], userId: int) -> None:
    """ Resets information used during a game

    This function resets information like guesses left and the current word
    to prepare for creating a new game.

    Args:
        stats (List[int]) : The user's stats
        userId (int) : The user's id

    Returns:
        Updates the database 
    """

    query = "UPDATE pokewordle SET currentword = %s, guesses = %s, lives = %s, stats = %s WHERE userId = %s"
    myCursor.execute(query, ("", [], 5, stats, str(userId)))
    db.commit()


def view_rows(userId: int) -> str:
    """ A debugging function to view rows of a user

    This function returns a string consisting of all the info in a 
    user's row for debugging purposes

    Args:
        userId (int) : The user's id

    Returns:
        A string with all the data in a user's row in the database
    """

    a = ""
    myCursor.execute(
        "SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    for row in rows:
        a += str(row) + "\n"
    return a


def compare_pokemon(userId: int, guess: str) -> Embed:
    """ Compares the user's guess with the actual pokemon

    This function returns an embedded message object on the similarities / differences
    between the user's guessed pokemon and the actual pokemon

    Args:
        userId (int) : The user's id
        guess (str) : The user's guess

    Returns:
        A string with all the data in a user's row in the database
    """

    myCursor.execute(
        "SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    currentPokemon = rows[0][2]
    livesLeft = rows[0][4]

    # Fetch the guessed pokemon from the pokeapi
    guessed = requests.get(f'https://pokeapi.co/api/v2/pokemon/{guess}')
    guessed2 = requests.get(
        f'https://pokeapi.co/api/v2/pokemon-species/{guess}')
    if guessed.status_code == 404 or guessed2.status_code == 404:
        return "Pokemon not found"

    guessedInfo = json.loads(guessed.text)
    guessedGenInfo = json.loads(guessed2.text)
    guessedTypes = guessedInfo['types']
    guessedTypeNames = [type['type']['name'] for type in guessedTypes]
    guessedWeight, guessedHeight, guessedImage = guessedInfo[
        'weight'], guessedInfo['height'], guessedInfo['sprites']['front_default']
    guessedGeneration = guessedGenInfo['generation']['url']

    guessed = requests.get(
        f'https://pokeapi.co/api/v2/pokemon/{currentPokemon}')
    guessed2 = requests.get(
        f'https://pokeapi.co/api/v2/pokemon-species/{currentPokemon}')
    if guessed.status_code == 404 or guessed2.status_code == 404:
        return "Pokemon not found"

    actualInfo = json.loads(guessed.text)
    actualGenInfo = json.loads(guessed2.text)
    actualTypes = actualInfo['types']
    actualTypeNames = [type['type']['name'] for type in actualTypes]
    actualWeight, actualHeight, actualImage = actualInfo[
        'weight'], actualInfo['height'], actualInfo['sprites']['front_default']
    actualGeneration = actualGenInfo['generation']['url']

    res = "**"
    res += f"For Guessed Pokemon {guess}:\n"
    matchingTypes = [
        type for type in guessedTypeNames if type in actualTypeNames]
    res += f"Matching Types {matchingTypes}\n"
    if actualGeneration[37:38] < guessedGeneration[37:38]:
        res += f"Generation: Pokemon is in an Earlier Generation\n"
    elif actualGeneration[37:38] > guessedGeneration[37:38]:
        res += f"Generation: Pokemon is in a Later Generation\n"
    else:
        res += f"Generation: They are from the Same Generation\n"

    if actualWeight == guessedWeight:
        res += "Weight: They have the same weight\n"
    elif abs(int(guessedWeight) - int(actualWeight)) < 100:
        res += "Weight: They have similar weights\n"
    elif guessedWeight < actualWeight:
        res += "Weight: The Pokemon you guessed is too light\n"
    else:
        res += "Weight: The Pokemon you guessed is too heavy\n"

    if actualHeight == guessedHeight:
        res += "Height: They have the same Height\n"
    elif abs(int(guessedHeight) - int(actualHeight)) < 7:
        res += "Height: They have similar heights\n"
    elif guessedHeight < actualHeight:
        res += "Height: The Pokemon you guessed is too short\n"
    else:
        res += "Height: The Pokemon you guessed is too tall\n"
    res += "\n\nLives Left: " + str(livesLeft) + "**"
    res += "\n Previous Guesses: " + str(rows[0][3])
    embed = guessed_answer(guess, guessedImage, res)
    return embed


def make_guess(userId: int, guess: str) -> List[int]:
    """ Makes a guess for the user's current pokemon
        
    This function returns an array specifying what happened with the user's guess
    and what events to call afterwards.
    

    Args:
        userId (int) : The user's id
        guess (str) : The user's guess
    
    Returns:
        An array specifying what happened with the user's guess
    """
    
    guessed = requests.get(f'https://pokeapi.co/api/v2/pokemon/{guess}')
    if guessed.status_code == 404:
        return ["Pokemon not found", []]
    myCursor.execute(
        "SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    # If not in database
    if len(rows) == 0:
        return ["Game not started", []]

    entry = rows[0]
    currentPokemon = entry[2]
    if currentPokemon == '':
        return ["Game not started", []]
    # Check if guess is correct
    if guess.lower() == currentPokemon:
        # Win
        index = 5 - entry[4]
        stats = entry[5]
        stats[index] += 1
        return ["Game won", stats]

    # Wrong guess
    guessArr = entry[3]
    guessArr.append(guess)
    lives = entry[4]-1
    if lives == 0:
        stats = entry[5]
        stats[5] += 1
        return ["Game lost", stats]
    query = "UPDATE pokewordle SET guesses = %s, lives = %s WHERE userId = %s"
    myCursor.execute(query, (guessArr, lives, str(userId)))
    return ["Wrong Guess", []]


def store_current_pokemon(userId: int, start: int, end: int) -> None:
    """ Stores the current game in the database

    This function stores the current game in the database. It also stores the
    user's id, the current pokemon, the number of lives left, and the guesses
    made.

    Args:
        userId (int) : The user's id
        start (int) : Starting pokemon generation
        end (int) : Ending pokemon generation
    
    Returns:
        None
    """

    pokemonId = get_random_pokemon(start, end)
    pokemonName = get_pokemon_name(pokemonId)
    # Check to see if Row exists
    myCursor.execute(
        "SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    if len(rows) == 0:
        # Insert Row
        query = "INSERT INTO pokewordle (userId, currentword,guesses,lives,stats) VALUES (%s, %s, %s, %s, %s)"
        arr = [0, 0, 0, 0, 0, 0]
        myCursor.execute(query, (str(userId), pokemonName, [], 5, arr))
        db.commit()
    else:
        # Update Row currentword and lives and guesses
        query = "UPDATE pokewordle SET currentword = %s, guesses = %s, lives = %s WHERE userId = %s"
        myCursor.execute(query, (pokemonName, [], 5, str(userId)))
        db.commit()


def get_pokemon_name(id: int) -> str:
    """ Gets the name of the pokemon from the API
    
    This function gets the name of the pokemon from the API using the provided
    pokemon ID.
    
    Args:
        id (int) : The pokemon's ID

    Returns:
        The name of the pokemon
    """
    res = requests.get(f'https://pokeapi.co/api/v2/pokemon/{id}')
    response = json.loads(res.text)
    return response['species']['name']


def get_random_pokemon(start: int, end:int) -> int:
    """ Gets a random pokemon from the API
    
        This function gets a random pokemon from the API using the provided
        start and end generations.
        
        Args:
            start (int) : Starting generation
            end (int) : Ending generation
            
        Returns:
            The ID of the pokemon
    """
    id = random.randint(generationEnds[start], generationEnds[end])
    return id
