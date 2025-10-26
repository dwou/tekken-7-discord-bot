from os import getenv

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

from helper_functions import *
from _players import *
from basic_functions import *

# TODO: test permissions
# needs '268536832' permissions (I think)

''' <--- NOTES: Types & naming conventions, Functions, Data --->
"msg": discord.message.Message (a Discord message)
  .channel.send() (send a message)
  .content: str (the message's content)
  .author (the author, a Member)
discord.member.Member
  .guild_permissions.administrator: bool (is an admin)
  .mention: str? (the username)
  .bot: bool (is a bot)
  .display_name
  .global_name (display_name but sometimes returns None)
"itx" discord.Interaction (for slash commands (among other things?))
  .response.send_message(text: str, ephemeral: bool)
  .user: Member (the message sender)
  .channel
"ctx" (discord.ext.)commands.context.Context (it's like a Member)
  .send (send a message; different from Message.channel.send()?)
'''


###############
# Main/global #
###############


# get "intents" (incoming messages, reactions etc) and create the bot
intents = discord.Intents.default()
intents.message_content = True  # see (incoming messages'?) content
bot = commands.Bot(command_prefix="!", intents=intents)

def main():
  global bot, players
  players = Players()
  load_dotenv()
  bot.run(getenv("DISCORD_TOKEN"))


##################
# Events/intents #
##################


@bot.event
async def on_ready():
  await bot.tree.sync()
  debug_print(f"{bot.user} is online!")


@bot.event
async def on_message(msg: discord.message.Message):
  """ handle new messages """
  # drop DMs
  # TODO: try testing if "member" (what?)
  if not msg.guild:
    return

  #text: str = msg.content
  is_bot: bool = msg.author.bot
  #is_admin: bool = msg.author.guild_permissions.administrator

  # print message and resolve mentioned users/roles
  await pretty_print_message(msg)

  # ignore bots' messages
  if is_bot:
    return

  # handle automatic replies
  responded: bool = await handle_autoreply(msg)

  # execute ! commands
  await bot.process_commands(msg)


##################
# Slash commands #
##################


@commands.has_permissions(administrator=True)
@bot.tree.command(name='save', description='Saves player data')
async def save(
    itx: discord.Interaction,
    backup: bool):
  #debug_print(arg)
  debug_print('Saving...')
  players.save_to_file(backup=backup)
  debug_print('Saved.')
  await itx.response.send_message(f'Saved.', ephemeral=True)


@bot.tree.command(name='playerdata', description='Prints player data')
async def playerdata(itx: discord.Interaction):
  players.print_players()
  await bot_say(itx.channel, f'Printed.')


##############
# ! commands #
##############


# ping pong test
@bot.command(name='ping')
async def ping(ctx: discord.ext.commands.context.Context):
  await ctx.send("Pong!")


####################################
# Other functions that use the bot #
####################################


async def pretty_print_message(msg: discord.message.Message):
  # print message and resolve mentioned users/roles
  raw_text: str = msg.content
  is_bot: bool = msg.author.bot
  is_admin: bool = msg.author.guild_permissions.administrator
  title: str = 'bot' if is_bot else ('admin' if is_admin else 'user')
  pretty_text: str = raw_text
  # iterate through each <> part in the message, resolve, and replace
  for prefix,digits in re.findall(r'<(@|@&|#)(\d{18,19})>', raw_text):
    raw_match = f'<{prefix}{digits}>'
    match prefix:
      case "@&":  # role mention
        pretty_fragment = '@[a role]'
      case "@":  # user
        mention_username = (await bot.fetch_user(digits)).display_name
        pretty_fragment = f"@[{mention_username}]"
      case "#":  # channel
        pretty_fragment = '#[a channel]'
      case _:  # no match
        continue
    pretty_text = pretty_text.replace(raw_match, pretty_fragment)
  debug_print(f'[{title} {msg.author.display_name}]: {pretty_text}')


if __name__ == "__main__":
  main()
