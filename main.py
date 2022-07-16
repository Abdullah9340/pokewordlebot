import discord
import os
from dotenv import load_dotenv
from embedTemplates import *
from functions import *


load_dotenv()
TOKEN = os.environ.get('TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    author_id, channel, content = message.author.id, message.channel, message.content

    if message.author == client.user:
        return
    elif content.startswith('$start'):
        start, end, flag = 0, 8, False
        if game_started(author_id):
            await channel.send(embed = general_embed('You have an ongoing game!'))
            return
        if len(content.split(' ')) > 1:
            range = content.split(' ')[1]
            start = int(range[0]) - 1
            if len(range) > 2:
                end = int(range[2])
            else:
                end = start+1
            if start >= 0 and end > 0 and start <= end:
                store_current_pokemon(author_id, start , end)
            else:
                flag = True
                await channel.send(embed = general_embed('Invalid range'))
        else:
            store_current_pokemon(author_id, 0 , 8)
        if not flag:
            embed = start_embed(message.author, start + 1, end)
            await channel.send(embed = embed)
    elif content.startswith('$guess'):
        try:
            guess = content.split()[1]
            storedInfo = make_guess(author_id, guess)
            result, stats = storedInfo[0], storedInfo[1]
            if result == -1:
                await channel.send(embed = general_embed('You need to start the game first!'))
            elif result == 1 :
                embed = game_won_poke_info(author_id)
                reset(stats, author_id)
                await channel.send(embed=embed)
            elif result == 0:
                embed=game_over_poke_info(author_id)
                reset(stats, author_id)
                await channel.send(embed=embed)
            elif result == 3:
                await channel.send(embed = general_embed('Pokemon not found!'))
            else:
                embed = compare_pokemon(author_id, guess)
                await channel.send(embed=embed)
        except:
            await channel.send(embed = general_embed("Please enter a guess!"))
    elif content.startswith('$stats'):
        await channel.send(embed = get_stats(author_id, message.author))
    elif content.startswith('$help'):
        await channel.send(embed = help_embed())
        
client.run(TOKEN)

