import pylabnet.utils.logging.logger as lg
import pylabnet.utils.helper_methods as hm
import pyvisa
import numpy as np

import os
import discord
from dotenv import load_dotenv

logger = lg.LogClient()

pmX = hm.autoconnect_device(device_tag='red power meter', logger=logger)


load_dotenv("C:\GithubSync\pylabnet\pylabnet\Discord_tokens\discord.env")
TOKEN = os.getenv('DISCORD_TOKEN')
# print('Token:' + str(TOKEN)) # This is a print statement to test if the Token has a not None value

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$power'):
        power = pmX.get_power()
        await message.channel.send("The power of the red power meter is at: " + str(power))

client.run(TOKEN) # This is the actual token that is used to run the bot

"""
for i in range(5):
    power = pmX.get_power()
    print(power)
    time.sleep(1)

"""
