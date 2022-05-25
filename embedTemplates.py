import discord

def startEmbed(name, start, end):

    embed = discord.Embed(
        type = "rich",
        title = f"Pokeworlde Start User: {name}!",
        description = f"**Welcome to pokewordle! Try your best to guess the right pokemon**\n\nThe pokemon you are guessing is between generations [{start}, {end}]\n\nRules:\n-You have **five** guesses, after each guess you will get information \nabout how close you were, try to get it in as few guesses as \npossible!\n\nUse guess to start guessing! Good luck\n\n",
        color = discord.Color.blue()
    )   
    # embed.set_thumbnail(url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/25.png")
    embed.set_image(url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/25.png")
    return embed

def guessedAnswer(guessed, guessedImage, res):
    embed = discord.Embed(
        type = "rich",
        title = f"Wrong Answer!",
        description = res,
        color = discord.Color.blue()
    )   
    # embed.set_thumbnail(url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/25.png")
    embed.set_image(url=f"{guessedImage}")
    
    return embed

def gameOver(actual, actualImage):
    embed = discord.Embed(
        type = "rich",
        title = f"Gosh darn it! You lost!",
        description = f"**The right answer was {actual} L + RATIO TEST = 1**",
        color = discord.Color.red()
    )   
    # embed.set_thumbnail(url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/25.png")
    embed.set_image(url=f"{actualImage}")
    
    return embed

def gameWon(actual, actualImage, lives):
    embed = discord.Embed(
        type = "rich",
        title = f"You won in {6-lives} guesses!",
        description = f"**The right answer was {actual}, take a shot and celebrate or stay halal mode**",
        color = discord.Color.green()
    )
    # embed.set_thumbnail(url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/25.png")
    embed.set_image(url=f"{actualImage}")
    
    return embed

def statsEmbed(name,stats):
    embed = discord.Embed(
        type = "rich",
        title = f"{name}'s Stats",
        description = f"""**Won in 1 guess: {stats[0]} time(s)\n
                            Won in 2 guess: {stats[1]} time(s)\n
                            Won in 3 guess: {stats[2]} time(s)\n
                            Won in 4 guess: {stats[3]} time(s)\n
                            Won in 5 guess: {stats[4]} time(s)\n
                            Losses        : {stats[5]} time(s)\n
                        **""",
        color = discord.Color.from_rgb(254, 231, 92)
    )
    embed.set_thumbnail(url=f"https://staticg.sportskeeda.com/editor/2019/12/7347a-15769410112866-800.jpg")
    return embed

def generalEmbed(text):
    embed = discord.Embed(
        type = "rich",
        title = f"{text}",
        description = f"",
        color = discord.Color.orange()
    )
    return embed

def helpEmbed():
    embed = discord.Embed(
        type = "rich",
        title = "Help",
        description = f""" 
                        **Description:**\n
                        Welcome to pokewordle! Try your best to guess the right pokemon. You have **five** guesses, try to get it in as few guesses as possible!\n
                        **Commands:**\n   
                        **$start <start>-<end>** - Starts the game within the given inclusive generation range, by default it is between generations 1 and 8\n
                        **$guess <pokemon>**\n
                        **$stats** - display your stats\n
                        """,
        color = discord.Color.from_rgb(255,255,255)
    )
    return embed

# start game
# how to make a guess
# choose generations
# stats
# 5 guesses