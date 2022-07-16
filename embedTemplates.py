"""
    Authors: Mahfuzur Rahman (m236rahm@uwaterloo.ca), Abdullah Abdullah (a55abdul@uwaterloo.ca)
    Date: June 2022
    Description: This is the file that contains the functions for generating
    embedded message templates.
"""

import discord
from typing import List


Color = discord.Color
Embed = discord.Embed


def start_embed(name: str, start: int, end: int) -> Embed:
    """ Embed for when the user starts the game 
        Color: green

        Args:
            name (str): Name of the user
            start (int): The starting generation
            end (int): The ending generation

        Returns:
            embed (Embed): The embed to be sent to the server
    """

    embed = Embed(
        type="rich",
        title=f"Pokeworlde Start User: {name}!",
        description=f"""**Welcome to pokewordle! Try your best to guess the right pokemon**\n\n
                            The pokemon you are guessing is between generations [{start}, {end}]\n\n
                            Rules:\n-You have **five** guesses, after each guess you will get information \n
                            about how close you were, try to get it in as few guesses as \npossible!
                            \n\nUse guess to start guessing! Good luck\n\n
                        """,
        color=Color.green()
    )
    embed.set_image(
        url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/25.png")
    return embed


def guessed_answer(guessedImage: str, res: str) -> Embed:
    """ Embed for when the user guesses incorrectly 
        Color: Blue

        Args:
            guessedImage (str): The url of the pokemon guessed
            res (str): The description for the embed

        Returns:
            embed (Embed): The embed to be sent to the server
    """

    embed = Embed(
        type="rich",
        title=f"Wrong Answer!",
        description=res,
        color=Color.blue()
    )
    embed.set_image(url=f"{guessedImage}")

    return embed


def game_over(actual: str, actualImage: str) -> Embed:
    """ Embed for when the user losesstr
        Color: Red

        Args:
            actual (str): The actual pokemon
            actualImage (str): The url of the actual pokemon

        Returns:
            embed (Embed): The embed to be sent to the server
    """

    embed = Embed(
        type="rich",
        title=f"Gosh darn it! You lost!",
        description=f"**The right answer was {actual} L + RATIO TEST = 1**",
        color=Color.red()
    )
    embed.set_image(url=f"{actualImage}")

    return embed


def game_won(actual: str, actualImage: str, lives: int) -> Embed:
    """ Embed for when the user wins
        Color: Green

        Args:
            actual (str): The actual pokemon
            actualImage (str): The url of the actual pokemon
            lives (int): The number of lives left

        Returns:
            embed (Embed): The embed to be sent to the server
    """

    embed = Embed(
        type="rich",
        title=f"You won in {6-lives} guesses!",
        description=f"**The right answer was {actual}, take a shot and celebrate or stay halal mode**",
        color=Color.green()
    )
    embed.set_image(url=f"{actualImage}")

    return embed


def stats_embed(name: str, stats: List[int]) -> Embed:
    """ Embed for the stats of the user
        Color: Orange

        Args:
            name (str): The name of the user
            stats (List[int]): The stats of the user

        Returns:
            embed (Embed): The embed to be sent to the server
    """

    embed = Embed(
        type="rich",
        title=f"{name}'s Stats",
        description=f"""**Won in 1 guess: {stats[0]} time(s)\n
                            Won in 2 guess: {stats[1]} time(s)\n
                            Won in 3 guess: {stats[2]} time(s)\n
                            Won in 4 guess: {stats[3]} time(s)\n
                            Won in 5 guess: {stats[4]} time(s)\n
                            Losses        : {stats[5]} time(s)\n
                        **""",
        color=Color.from_rgb(254, 231, 92)
    )
    embed.set_thumbnail(
        url=f"https://staticg.sportskeeda.com/editor/2019/12/7347a-15769410112866-800.jpg")
    return embed


def general_embed(text: str) -> Embed:
    """ Embed for general messages
        Color: Orange

        Args:
            text (str): The text to be displayed

        Returns:
            embed (Embed): The embed to be sent to the server
    """

    embed = Embed(
        type="rich",
        title=f"{text}",
        description="",
        color=Color.orange()
    )
    return embed


def help_embed() -> Embed:
    """ Embed for the help command
        Color: Orange

        Args:
            None

        Returns:
            embed (Embed): The embed to be sent to the server
    """

    embed = Embed(
        type="rich",
        title="Help",
        description=f""" 
                        **Description:**\n
                        Welcome to pokewordle! Try your best to guess the right pokemon. You have **five** guesses, try to get it in as few guesses as possible!\n
                        **Commands:**\n   
                        **$start <start>-<end>** - Starts the game within the given inclusive generation range, by default it is between generations 1 and 8\n
                        **$guess <pokemon>**\n
                        **$stats** - display your stats\n
                        """,
        color=Color.from_rgb(255, 255, 255)
    )
    return embed
