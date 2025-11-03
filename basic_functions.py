#import discord
#from discord.ext import commands
#from discord import app_commands


def debug_print(*args, **kwargs):
  """ print to console with flush=True """
  sep = kwargs.get('sep', ' ')
  end = kwargs.get('end', '\n')
  print(*args, sep=sep, end=end, flush=True)
