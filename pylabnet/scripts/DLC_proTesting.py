import pylabnet.utils.logging.logger as lg
import pylabnet.utils.helper_methods as hm
#import pyvisa
import numpy as np
import os
import discord
from dotenv import load_dotenv


logger = lg.LogClient()

pmX = hm.autoconnect_device(device_tag='DLC', logger=logger)

load_dotenv("C:\GithubSync\pylabnet\pylabnet\Discord_tokens\discord.env")
TOKEN = os.getenv('DISCORD_TOKEN')

laser_on = pmX.is_laser_on()
#message = pmX.read_until(b'>', timeout=1)#.split()[-3].decode('utf')[1:-1]
logger.info(f'Laser is on: , {laser_on}')

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

    if message.content.startswith('$DLPro_on'):
        laser_on = pmX.is_laser_on()
        await message.channel.send("The DLPro is on: " + str(laser_on))
    if message.content.startswith('$Cryo_destroyed?'):

        await message.channel.send("The Cryo is destroyed")
client.run(TOKEN) # This is the actual token that is used to run the bot
