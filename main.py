import discord
import psycopg2
import os
import random 
import requests
import json
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get('TOKEN')
password = os.environ.get('password')

client = discord.Client()
URL = f'postgresql://abdullah:{password}@free-tier4.aws-us-west-2.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&options=--cluster%3Drunny-tiger-2222&sslrootcert=root.crt'

db = psycopg2.connect(URL)

myCursor = db.cursor()


# Commands
# $pokewordle create
# This will randomly choose a pokemon and store it in the 

def reset(stats,userId):
    query = "UPDATE pokewordle SET currentword = %s, guesses = %s, lives = %s, stats = %s WHERE userId = %s"
    myCursor.execute(query, ("", [], 5, stats, str(userId)))
    db.commit()

def viewRows(userId):
    a = ""
    myCursor.execute("SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    for row in rows:
        a += str(row) + "\n"
    return a


def comparePokemon(userId, guess):
    myCursor.execute("SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    currentPokemon = rows[0][2]

    
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
    guessedGeneration = guessedGenInfo['generation']['url']
    print(guessedTypeNames, guessedWeight, guessedHeight, guessedGeneration)
    
    
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
    actualGeneration = actualGenInfo['generation']['url']
    print(actualTypeNames, actualWeight, actualHeight, actualGeneration)

    res = ""
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
    elif guessedWeight < actualWeight:
        res += "Weight: The Pokemon you guessed is too light\n"
    else:
        res += "Weight: The Pokemon you guessed is too heavy\n"
    
    if actualHeight == guessedHeight:
        res += "Height: They have the same Height\n"
    elif guessedHeight < actualHeight:
        res += "Height: The Pokemon you guessed is too short\n"
    else:
        res += "Height: The Pokemon you guessed is too tall\n"
    return res
# -1 need to start game
# 1 guessed correctly
# 0 Out of lives
# 2 Wrong guess

def makeGuess(userId, guess):
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

def storeCurrentPokemon(userId):
    pokemonId = getRandomPokemon()
    pokemonName = getPokemonName(pokemonId)
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
    
def getPokemonName(id):
    res =  requests.get(f'https://pokeapi.co/api/v2/pokemon/{id}')
    response = json.loads(res.text)
    return response['species']['name']
    
def getRandomPokemon():
    id = random.randint(1,908)
    return id

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.content.startswith('start'):
        storeCurrentPokemon(message.author.id)
        await message.channel.send(f'Hello! {message.author.name}')
    elif message.content.startswith('guess'):
        try:
            guess = message.content.split()[1]
            storedInfo = makeGuess(message.author.id, guess)
            result,stats = storedInfo[0], storedInfo[1]
            if result == -1:
                await message.channel.send('You need to start the game first!')
            elif result == 1 :
                reset(stats, message.author.id)
                await message.channel.send(f'You guessed correctly!')
            elif result == 0:
                reset(stats, message.author.id)
                await message.channel.send(f'You are out of lives!')
            else:
                res = comparePokemon(message.author.id, guess)
                await message.channel.send(res)
        except:
            await message.channel.send('Please enter a guess!')
    elif message.content.startswith('rows'):
        a = viewRows(message.author.id)
        await message.channel.send(f'{a}')
        
client.run(TOKEN)

