# Functions that can be separated from bot.py but still use Discord functionality
import re
import discord
from basic_functions import *


async def handle_autoreply(msg: discord.message.Message) -> bool:
  """ apply all the functions that automatically reply to a message.
      return True if there is any match """
  text: str = msg.content
  author: discord.member.Member = msg.author.mention
  beggar_pattern = r'(?=.{0,40}tourn.{0,30}|(help|final|last)).{0,30}achiev'
  if re.search(beggar_pattern, text):
    # TODO: check if it's their first 3 messages
    debug_print('!!! Beggar Detected !!!')
    await bot_say(msg.channel, f'You probably won\'t find anyone to help with getting the tournament achievement here {msg.author.mention}')
  else: # no matches
    return False
  return True
