import discord
from discord.ext import commands
from discord import app_commands

# use re.fullmatch
# Note: case insensitive, forced lowercase
# Rules: 2-32 length; _ . a-z 0-9 allowed; unique
#valid_name_pattern = r'(?!.*?\.\.)([a-z0-9_\.]{2,32})'


def debug_print(*args, **kwargs):
  """ print to console with flush=True """
  sep = kwargs.get('sep', ' ')
  end = kwargs.get('end', '\n')
  print(*args, sep=sep, end=end, flush=True)


async def bot_say(channel, text: str):
  """ send a simple Discord message """
  await channel.send(text)


# don't use; this is here for completeness of coverage
async def slash_bot_say(itx: discord.Interaction, text: str, **kwargs):
  ephemeral = kwargs.get('ephemeral', False)
  await itx.send(text, ephemeral=ephemeral)


async def bot_respond(text: str):
  # idk implement the other 2-3 Discord "print" functions
  # for Context (ctx) use .send(text: str)
  pass#interaction.response.send_message(text)
