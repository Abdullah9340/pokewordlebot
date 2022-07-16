from embedTemplates import *
import psycopg2
import os
import random 
import requests
import json
from dotenv import load_dotenv

load_dotenv()
password = os.environ.get('password')

URL = f'postgresql://abdullah:{password}@free-tier4.aws-us-west-2.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&options=--cluster%3Drunny-tiger-2222&sslrootcert=root.crt'
db = psycopg2.connect(URL)
myCursor = db.cursor()

generationEnds = {
    0 : 0,
    1 : 151,
    2 : 251,
    3 : 386,
    4 : 493,
    5 : 649,
    6 : 721,
    7 : 809,
    8 : 898,
}

def game_started(userId):
    myCursor.execute("SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    if len(rows) == 0:
        return False
    return rows[0][2] != ""


def get_stats(userId, name):
    myCursor.execute("SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    if len(rows) == 0:
        return [0,0,0,0,0,0]
    stats = rows[0][5]
    embed = stats_embed(name, stats)
    return embed

def game_won_poke_info(userId):
    myCursor.execute("SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    currentPokemon = rows[0][2]
    lives = rows[0][4]
    actual = requests.get(f'https://pokeapi.co/api/v2/pokemon/{currentPokemon}')
    actualImage = json.loads(actual.text)['sprites']['front_default']
    res = game_won(currentPokemon, actualImage, lives)
    return res

def game_over_poke_info(userId):
    myCursor.execute("SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    currentPokemon = rows[0][2]
    actual = requests.get(f'https://pokeapi.co/api/v2/pokemon/{currentPokemon}')
    actualImage = json.loads(actual.text)['sprites']['front_default']
    res = game_over(currentPokemon, actualImage)
    return res


def reset(stats,userId):
    query = "UPDATE pokewordle SET currentword = %s, guesses = %s, lives = %s, stats = %s WHERE userId = %s"
    myCursor.execute(query, ("", [], 5, stats, str(userId)))
    db.commit()

def view_rows(userId):
    a = ""
    myCursor.execute("SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    for row in rows:
        a += str(row) + "\n"
    return a


def compare_pokemon(userId, guess):
    myCursor.execute("SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    currentPokemon = rows[0][2]
    livesLeft = rows[0][4]
    
    guessed = requests.get(f'https://pokeapi.co/api/v2/pokemon/{guess}')
    guessed2 = requests.get(f'https://pokeapi.co/api/v2/pokemon-species/{guess}')
    if guessed.status_code == 404 or guessed2.status_code == 404:
        return "Pokemon not found"
        
    guessedInfo = json.loads(guessed.text)
    guessedGenInfo = json.loads(guessed2.text)
    guessedTypes = guessedInfo['types']
    guessedTypeNames = [type['type']['name'] for type in guessedTypes]
    guessedWeight = guessedInfo['weight']
    guessedHeight = guessedInfo['height']
    guessedImage = guessedInfo['sprites']['front_default']
    guessedGeneration = guessedGenInfo['generation']['url']
    
    guessed = requests.get(f'https://pokeapi.co/api/v2/pokemon/{currentPokemon}')
    guessed2 = requests.get(f'https://pokeapi.co/api/v2/pokemon-species/{currentPokemon}')
    if guessed.status_code == 404 or guessed2.status_code == 404:

        return "Pokemon not found"
        
    actualInfo = json.loads(guessed.text)
    actualGenInfo = json.loads(guessed2.text)
    actualTypes = actualInfo['types']
    actualTypeNames = [type['type']['name'] for type in actualTypes]
    actualWeight = actualInfo['weight']
    actualHeight = actualInfo['height']
    actualImage = actualInfo['sprites']['front_default']
    actualGeneration = actualGenInfo['generation']['url']

    res = "**"
    res += f"For Guessed Pokemon {guess}:\n"
    matchingTypes = [type for type in guessedTypeNames if type in actualTypeNames]
    res += f"Matching Types {matchingTypes}\n"
    if actualGeneration[37:38] < guessedGeneration[37:38]:
        res+= f"Generation: Pokemon is in an Earlier Generation\n"
    elif actualGeneration[37:38] > guessedGeneration[37:38]:
        res+= f"Generation: Pokemon is in a Later Generation\n"
    else:
        res+= f"Generation: They are from the Same Generation\n"

    if actualWeight == guessedWeight:
        res += "Weight: They have the same weight\n"
    elif abs(int(guessedWeight) - int(actualWeight)) < 100:
        res+= "Weight: They have similar weights\n"
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
# -1 need to start game
# 1 guessed correctly
# 0 Out of lives
# 2 Wrong guess

def make_guess(userId, guess):
    guessed = requests.get(f'https://pokeapi.co/api/v2/pokemon/{guess}')
    if guessed.status_code == 404:
        return [3,[]]
    myCursor.execute("SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    # If not in database
    if len(rows) == 0:
        return [-1,[]]

    entry = rows[0]
    currentPokemon = entry[2]
    if currentPokemon == '':
        return [-1,[]]
    # Check if guess is correct
    if guess.lower() == currentPokemon:
        # Win
        index = 5 - entry[4]
        stats = entry[5]
        stats[index] += 1
        return [1,stats]

    # Wrong guess   
    guessArr = entry[3]
    guessArr.append(guess)
    lives = entry[4]-1
    if lives == 0:
        stats = entry[5]
        stats[5] += 1 
        return [0,stats]
    query = "UPDATE pokewordle SET guesses = %s, lives = %s WHERE userId = %s"
    myCursor.execute(query, (guessArr, lives, str(userId)))
    return [2,[]]

def store_current_pokemon(userId, start , end):
    pokemonId = get_random_pokemon(start, end)
    pokemonName = get_pokemon_name(pokemonId)
    # Check to see if Row exists
    myCursor.execute("SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    if len(rows) == 0:
        # Insert Row
        query = "INSERT INTO pokewordle (userId, currentword,guesses,lives,stats) VALUES (%s, %s, %s, %s, %s)"
        arr = [0,0,0,0,0,0]
        myCursor.execute(query, (str(userId), pokemonName, [], 5, arr))
        db.commit()
    else:
        # Update Row currentword and lives and guesses
        query = "UPDATE pokewordle SET currentword = %s, guesses = %s, lives = %s WHERE userId = %s"
        myCursor.execute(query, (pokemonName, [], 5, str(userId)))
        db.commit()

    
def get_pokemon_name(id):
    res =  requests.get(f'https://pokeapi.co/api/v2/pokemon/{id}')
    response = json.loads(res.text)
    return response['species']['name']
    
def get_random_pokemon(start,end):
    id = random.randint(generationEnds[start],generationEnds[end])
    return id
