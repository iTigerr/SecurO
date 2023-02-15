import discord
from discord import app_commands

import os

from replit import db

from keep_alive import keep_alive

intents = discord.Intents.all()
client = discord.Client(command_prefix="s!", intents=intents)
tree = app_commands.CommandTree(client)

MAIN = discord.Color.from_rgb(77,109,243)
RED = discord.Color.from_rgb(255,0,0)

test_guild = discord.Object(id=1074124752437923871)
  

# client is loaded
@client.event
async def on_ready():
  for key in db.keys():
    if key not in [str(guild.id) for guild in client.guilds]:
      del db[key]

  for id in [str(guild.id) for guild in client.guilds]:
    if id not in db.keys():
      db[id] = {"password": ""}
      
  await tree.sync(guild=test_guild)

  print("We have logged in as {0.user}".format(client))
  print("Running on " + str(len(client.guilds)) + " servers")

  await client.change_presence(status=discord.Status.online, activity=discord.Game(name="/help"))

# client joined guild
@client.event
async def on_guild_join(guild):
  db[str(guild.id)] = {"password": ""}

# client removed from guild
@client.event
async def on_guild_remove(guild):
  del db[str(guild.id)]

# user joined guild
@client.event
async def on_member_join(member):
  guild = member.guild
  password = db[str(guild.id)]["password"]

  if password != "":
    channel = await member.create_dm()

    emb = discord.Embed(
      title=str(member),
      description=
      f"You just joined **{guild.name}**.\nTo get access to the server, send '**{password}**' in this DM",
      colour=MAIN
    )
    await channel.send(embed=emb)


@tree.command(name="ping", description="Returns the latency of the client in ms", guild=test_guild)
async def ping(interaction):
  emb = discord.Embed(title="Pong!", description="> " + str(round(client.latency*1000,2)) + "ms" , colour=MAIN)
  await interaction.response.send_message(embed=emb)

@tree.command(name="test", description="Returns the argument", guild=test_guild)
async def test(interaction, arg: str):
  await interaction.response.send_message(arg)

@tree.command(name="setpassword", description="Set guild password - set to empty to remove password", guild=test_guild)
async def setpassword(interaction, password: str):
  guild = discord.Object(id=interaction.guild_id)
  db[str(guild.id)]["password"] = str(password)
  desc = f"Guild password set to {password}" if password != "" else "Guild password removed"
  emb = discord.Embed(title=str(interaction.user), description=desc)
  await interaction.response.send_message(embed=emb)

@tree.command(name="setrole", description="Set the member role to be given to verified users", guild=test_guild)
async def setrole(interaction, role: discord.Role):
  print(role)
  

@client.event
async def on_message(message):
  pass


keep_alive()
client.run(os.getenv("TOKEN"))
