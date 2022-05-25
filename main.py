import discord
import psycopg2
import os
import random 
import requests
import json
from dotenv import load_dotenv
from embedTemplates import *


load_dotenv()

TOKEN = os.environ.get('TOKEN')
password = os.environ.get('password')

client = discord.Client()
URL = f'postgresql://abdullah:{password}@free-tier4.aws-us-west-2.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&options=--cluster%3Drunny-tiger-2222&sslrootcert=root.crt'

db = psycopg2.connect(URL)

myCursor = db.cursor()

# generationNum = generationEnds[first - 1] to generationEnds[second]

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

# Commands
# $pokewordle create
# This will randomly choose a pokemon and store it in the 

def gameStarted(userId):
    myCursor.execute("SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    if len(rows) == 0:
        return False
    return rows[0][2] != ""


def getStats(userId, name):
    myCursor.execute("SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    if len(rows) == 0:
        return [0,0,0,0,0,0]
    stats = rows[0][5]
    embed = statsEmbed(name, stats)
    return embed

def gameWonPokeInfo(userId):
    myCursor.execute("SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    currentPokemon = rows[0][2]
    lives = rows[0][4]
    actual = requests.get(f'https://pokeapi.co/api/v2/pokemon/{currentPokemon}')
    actualImage = json.loads(actual.text)['sprites']['front_default']
    res = gameWon(currentPokemon, actualImage, lives)
    return res

def gameOverPokeInfo(userId):
    myCursor.execute("SELECT * FROM pokewordle WHERE userId = %s", (str(userId),))
    rows = myCursor.fetchall()
    currentPokemon = rows[0][2]
    actual = requests.get(f'https://pokeapi.co/api/v2/pokemon/{currentPokemon}')
    actualImage = json.loads(actual.text)['sprites']['front_default']
    res = gameOver(currentPokemon, actualImage)
    return res


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
    embed = guessedAnswer(guess, guessedImage, res)
    return embed
# -1 need to start game
# 1 guessed correctly
# 0 Out of lives
# 2 Wrong guess

def makeGuess(userId, guess):
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

def storeCurrentPokemon(userId, start , end):
    pokemonId = getRandomPokemon(start, end)
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
    
def getRandomPokemon(start,end):
    id = random.randint(generationEnds[start],generationEnds[end])
    return id

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.content.startswith('$start'):
        # start 1-4
        if gameStarted(message.author.id):
            await message.channel.send(embed = generalEmbed('You have an ongoing game!'))
            return
        start = 0 
        end = 8
        flag = False
        if len(message.content.split(' ')) > 1:
            range = message.content.split(' ')[1]
            start = int(range[0]) - 1
            if len(range) > 2:
                end = int(range[2])
            else:
                end = start+1
            if start >= 0 and end > 0 and start <= end:
                storeCurrentPokemon(message.author.id, start , end)
            else:
                flag = True
                await message.channel.send(embed = generalEmbed('Invalid range'))
        else:
            storeCurrentPokemon(message.author.id, 0 , 8)
        if not flag:
            embed = startEmbed(message.author, start + 1, end)
            await message.channel.send(embed=embed)
    elif message.content.startswith('$guess'):
        try:
            guess = message.content.split()[1]
            storedInfo = makeGuess(message.author.id, guess)
            result,stats = storedInfo[0], storedInfo[1]
            if result == -1:
                await message.channel.send(embed = generalEmbed('You need to start the game first!'))
            elif result == 1 :
                embed = gameWonPokeInfo(message.author.id)
                reset(stats, message.author.id)
                await message.channel.send(embed=embed)
            elif result == 0:
                embed=gameOverPokeInfo(message.author.id)
                reset(stats, message.author.id)
                await message.channel.send(embed=embed)
            elif result == 3:
                await message.channel.send(embed=generalEmbed('Pokemon not found!'))
            else:
                embed = comparePokemon(message.author.id, guess)
                await message.channel.send(embed=embed)
        except:
            await message.channel.send(embed=generalEmbed("Please enter a guess!"))
    # elif message.content.startswith('rows'):
    #     a = viewRows(message.author.id)
    #     await message.channel.send(f'{a}')
    elif message.content.startswith('$stats'):
        await message.channel.send(embed=getStats(message.author.id, message.author))
    elif message.content.startswith('$help'):
        await message.channel.send(embed=helpEmbed())
        
client.run(TOKEN)

