import discord
from discord.ext import commands
from cogs.tasks.on_ready_message import OnReady_Message
import os
import json
from flask import Flask 
from threading import Thread

app = Flask('discord bot')

@app.route('/')
def hello_world():
    return 'beep boop'

def start_server():
  app.run(host='0.0.0.0',port=8080)
  
t = Thread(target=start_server)
t.start()

client = discord.Client()

if __name__ == '__main__':
  with open('./rationality.json', 'r') as f:
    rationality_uris = json.loads(f.read())


  intents = discord.Intents(messages=True, guilds=True)
  # make the client
  client = commands.Bot(command_prefix = ".", intents=intents)
  # Make the cog
  cog = OnReady_Message(client, rationality_uris)
  # Add cog to the client. Circular reference? maybe, but this is
  # kosher according to the docs
  client.add_cog(cog)

  my_secret = os.environ['TOKEN']

  client.run(my_secret)