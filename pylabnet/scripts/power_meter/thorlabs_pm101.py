import pylabnet.utils.logging.logger as lg
import pylabnet.utils.helper_methods as hm
import pyvisa
import numpy as np

import os
import discord
from dotenv import load_dotenv

logger = lg.LogClient()

pmX = hm.autoconnect_device(device_tag='red power meter', logger=logger)

# loading doesn't work, maybe the path is wrong?
# Plan was to load it from there, so it's included in the gitignore files and the Token isn't uploaded to the internet.
# It is a security risk for discord to have the Token of a bot uploaded to the internet
# Other Idea: Disable the Discord security measurements
load_dotenv('C:\\GithubSync\\pylabnet\\pylabnet\\configs\\devices\\thorlabs_pm101')
TOKEN = os.getenv('DISCORD_TOKEN') # Because loading didn't work, the TOKEN equals None right now
print('Token:' + str(TOKEN)) # This is a print statement to test if the Token has a not None value

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

client.run('MTE3NzI0MTc3MjY3ODcwOTI4OA.GTh7fV.WiR-SaLaMmtkCqLQRXyW5_mkRGoU_fTMk2Y2Gk')
#client.run(TOKEN) doesn't work right now, because TOKEN equals None

"""
for i in range(5):
    power = pmX.get_power()
    print(power)
    time.sleep(1)

"""
