import os
import re
import json
import time
from basic_functions import *


class Players():
  def __init__(self, filename='players.json'):
    self.filename=filename
    self.players: dict[str, Player] = self.load_players() # ID -> player

  def load_players(self):
    """ returns players from file, or create a new players """
    debug_print('Loading players...')
    this_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(this_dir, self.filename)
    debug_print(this_dir, file_path)
    players = dict()
    if os.path.isfile(file_path):
      debug_print('File exists.')
      with open(file_path, "r") as f:
        # TODO: check type annotation
        data: list[dict[str,_]] = json.load(f)
      for line in data:
        debug_print('Reading:', line)
        ID = line['ID']
        debug_print(f'{ID=}')
        new_player = Player(self, **line)
        players[ID] = new_player
    return players

  def print_players(self):
    for player in self.players.values():
      debug_print(vars(player))

  def get_player(self, ID) -> Player:
    """ fetch a player by their ID; create them if they don't exist """
    if ID not in self.players:
      self.players[ID] = Player(self)
    return self.players[ID]

  def save_to_file(self, backup=False):
    if not self.players:
      debug_print('There\'s nothing to save')
      return
    this_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(this_dir, self.filename)
    if backup:
      # rename the current <self.filename>.json to <self.filename>-<timestamp>.json
      old_basename = self.filename[:-5] # strip ".json"
      unix_time = time.strftime("%s")
      backup_name = os.path.join(this_dir, f'{old_basename}-{unix_time}.json')
      if os.path.isfile(file_path):
        os.rename(file_path, backup_name)
      else:
        debug_print('There\'s nothing to back up.')
    lines: list[dict] = [] # TODO: check type
    for ID,player in self.players.items():
      keys_to_write = list(vars(player).keys())
      debug_print(f'writing {ID=} with keys {keys_to_write}')
      if keys_to_write and keys_to_write != ['parent']:
        to_add = {key:value
                  for key,value in vars(player).items()
                  if key != 'parent'}
        lines.append(to_add)
    if lines:
      with open(file_path, 'w') as f:
        debug_print('Dumping:', lines)
        json.dump(lines, f)
    else:
      debug_print("There isn't enough data to write.")

  def new_player(self, ID: str):
    self.players[ID] = Player(self, ID=ID)


class Player():
  def __init__(self, parent, **kwargs):
    self.parent = parent
    for key,value in kwargs.items():
      setattr(self, key, value)
