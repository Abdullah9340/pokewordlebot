import discord

Color = discord.Color
Embed = discord.Embed

def start_embed(name, start, end):

    embed = Embed(
        type = "rich",
        title = f"Pokeworlde Start User: {name}!",
        description = f"""**Welcome to pokewordle! Try your best to guess the right pokemon**\n\n
                            The pokemon you are guessing is between generations [{start}, {end}]\n\n
                            Rules:\n-You have **five** guesses, after each guess you will get information \n
                            about how close you were, try to get it in as few guesses as \npossible!
                            \n\nUse guess to start guessing! Good luck\n\n
                        """,
        color = Color.green()
    )   
    embed.set_image(url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/25.png")
    return embed

def guessed_answer(guessed, guessedImage, res):
    embed = Embed(
        type = "rich",
        title = f"Wrong Answer!",
        description = res,
        color = Color.blue()
    )   
    embed.set_image(url=f"{guessedImage}")
    
    return embed

def game_over(actual, actualImage):
    embed = Embed(
        type = "rich",
        title = f"Gosh darn it! You lost!",
        description = f"**The right answer was {actual} L + RATIO TEST = 1**",
        color = Color.red()
    )   
    embed.set_image(url=f"{actualImage}")
    
    return embed

def game_won(actual, actualImage, lives):
    embed = Embed(
        type = "rich",
        title = f"You won in {6-lives} guesses!",
        description = f"**The right answer was {actual}, take a shot and celebrate or stay halal mode**",
        color = Color.green()
    )
    embed.set_image(url=f"{actualImage}")
    
    return embed

def stats_embed(name,stats):
    embed = Embed(
        type = "rich",
        title = f"{name}'s Stats",
        description = f"""**Won in 1 guess: {stats[0]} time(s)\n
                            Won in 2 guess: {stats[1]} time(s)\n
                            Won in 3 guess: {stats[2]} time(s)\n
                            Won in 4 guess: {stats[3]} time(s)\n
                            Won in 5 guess: {stats[4]} time(s)\n
                            Losses        : {stats[5]} time(s)\n
                        **""",
        color = Color.from_rgb(254, 231, 92)
    )
    embed.set_thumbnail(url=f"https://staticg.sportskeeda.com/editor/2019/12/7347a-15769410112866-800.jpg")
    return embed

def general_embed(text):
    embed = Embed(
        type = "rich",
        title = f"{text}",
        description = f"",
        color = Color.orange()
    )
    return embed

def help_embed():
    embed = Embed(
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
        color = Color.from_rgb(255,255,255)
    )
    return embed
