import discord
from discord import app_commands

import os
import time

from replit import db

from keep_alive import keep_alive
import functions

intents = discord.Intents.all()
client = discord.Client(command_prefix="/", intents=intents)
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
      db[id] = {"role": "", "autorole": "", "verify": ""}
      
  await tree.sync()

  print("We have logged in as {0.user}".format(client))
  print("Running on " + str(len(client.guilds)) + " servers")

  await client.change_presence(status=discord.Status.online, activity=discord.Game(name="/help"))

# client joined guild
@client.event
async def on_guild_join(guild):
  db[str(guild.id)] = {"role": "", "autorole": "", "verify": ""}
  time.sleep(5)
  await tree.sync()

# client removed from guild
@client.event
async def on_guild_remove(guild):
  del db[str(guild.id)]
  time.sleep(5)
  await tree.sync()

# user joined guild
@client.event
async def on_member_join(member):
  guild = member.guild
  key = db[str(guild.id)]
  password = functions.generate_password()
  
  if key["verify"] == "True":
    channel = await member.create_dm()

    emb = discord.Embed(
      title=str(member),
      description=
      f"You just joined **{guild.name}**.\nTo get access to the server, send '**{password}**' in this DM",
      colour=MAIN
    )
    emb.set_footer(text=f"{password} - {guild.id}")
    await channel.send(embed=emb)
    return
  elif key["autorole"] == "True":
    role = guild.get_role(key["role"])
    await member.add_roles(role)
    return


@tree.command(name="ping", description="Returns the latency of the client in ms")
async def ping(interaction):
  emb = discord.Embed(title="Pong!", description="> " + str(round(client.latency*1000,2)) + "ms" , colour=MAIN)
  await interaction.response.send_message(embed=emb)
  return
  

@tree.command(name="verify", description="Turn verification DM for new members on/off")
async def verify(interaction, verify: bool):
  guild = client.get_guild(interaction.guild_id)
  member = guild.get_member(interaction.user.id)

  if member.guild_permissions.administrator:
    if ((db[str(guild.id)]["autorole"] == "False") or (db[str(guild.id)]["autorole"] == "")) and verify:
      emb = discord.Embed(title=str(member), description="Autorole must be on to turn verification on", colour=RED)
      await interaction.response.send_message(embed=emb)
      return
    else:
      db[str(guild.id)]["verify"] = "True" if verify else "False"

      desc = "Verification turned on" if verify else "Verification turned off"
      emb = discord.Embed(title=str(member), description=desc, colour=MAIN)
      await interaction.response.send_message(embed=emb)
      return
  else:
    emb = discord.Embed(title=str(member), description="Only members with Administrator permission can use this command", colour=RED)
    await interaction.response.send_message(embed=emb)
    return
  

@tree.command(name="setrole", description="Set the member role to be given to verified members")
async def setrole(interaction, role: discord.Role):
  guild = client.get_guild(interaction.guild_id)
  member = guild.get_member(interaction.user.id)

  if member.guild_permissions.administrator:
    if role > guild.get_member(client.user.id).top_role:
      emb = discord.Embed(title=str(member), description="Chosen role must be lower on hierarchy than bot role", colour=RED)
      await interaction.response.send_message(embed=emb)
      return
    
    db[str(guild.id)]["role"] = role.id

    emb = discord.Embed(title=str(member), description=f"Verified role set to {role}", colour=MAIN)
    await interaction.response.send_message(embed=emb)
    return
  else:
    emb = discord.Embed(title=str(member), description="Only members with Administrator permission can use this command", colour=RED)
    await interaction.response.send_message(embed=emb)
    return
    

@tree.command(name="autorole", description="Set whether a role is given to new/verified members")
async def autorole(interaction, autorole: bool):
  guild = client.get_guild(interaction.guild_id)
  member = guild.get_member(interaction.user.id)

  if member.guild_permissions.administrator:
    if db[str(guild.id)]["role"] == "":
      emb = discord.Embed(title=str(member), description="Use /setrole before turning autorole on/off", colour=RED)
      await interaction.response.send_message(embed=emb)
      return
    elif db[str(guild.id)]["verify"] == "True":
      if autorole == False:
        emb = discord.Embed(title=str(member), description="Turn off verication with /verify before turning off autorole", colour=RED)
        await interaction.response.send_message(embed=emb)
        return
    else:
      db[str(guild.id)]["autorole"] = "True" if autorole else "False"
  
      desc = "Autorole turned on" if autorole else "Autorole turned off"
      emb = discord.Embed(title=str(member), description=desc, colour=MAIN)
      await interaction.response.send_message(embed=emb)
      return
  else:
    emb = discord.Embed(title=str(member), description="Only members with Administrator permission can use this command", colour=RED)
    await interaction.response.send_message(embed=emb)
    return


@client.event
async def on_message(message):
  if message.author == client.user:
    return
  
  msg = message.content
  
  if message.guild == None: # message is a DM
    channel = await message.author.create_dm()

    async for m in channel.history(limit=100):
      if m.author == client.user:
        if len(m.embeds) == 1:
          print(type(m.embeds[0].footer.text[0]))
          print(m.embeds[0].footer.text[0])
          password = m.embeds[0].footer.text[0].split(" - ")[0]
      
          if password == msg:
            try:
              guild = client.get_guild(int(m.embeds[0].footer.text[0].split(" - ")[1]))
              if guild == None:
                raise TypeError

              member = guild.get_member(message.author.id)
              if member == None:
                raise IndexError
            except TypeError:
              emb = discord.Embed(title=str(message.author), description="I am no longer in the server you are trying to access", colour=RED)
              message.channel.send(embed=emb, delete_after=10)
              return
            except IndexError:
              emb = discord.Embed(title=str(message.author), description="You are no longer in the server you are trying to access", colour=RED)
              message.channel.send(embed=emb, delete_after=10)
              return

            await member.add_roles(guild.get_role(int(db[str(guild.id)]["role"])))
            emb = discord.Embed(title=str(message.author), description=f"Password correct. You have been given access to **{str(guild)}**", colour=MAIN)
            await message.channel.send(embed=emb, delete_after=10)
            await m.delete()
            return

            


keep_alive()
client.run(os.getenv("TOKEN"))
