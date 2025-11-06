
import time
import asyncio
from basic_functions import *

class LobbyManager():
  elo_function = create_elo_function(K=20, diff=100, xtimes=2)
  lobbies: dict[int, dict] = dict() # lobby ID -> {}; see `new_lobby`
  # `lobbies`: key identifier(1,2,3,...) -> Dict:
  #   "region":_, "platform":_,
  #   "start_time":_, "last_interaction":_,
  #   "players":{},
  #   "records": dict[player, dict[W/L/D -> int]]
  #   "invited_players":{}
  keepalive_duration = 30 * 60 # seconds; initial time to keep a lobby alive for
  refresh_duration = 3 * 60 # seconds; time to keep a lobby alive without activity

  @classmethod
  async def __lobby_autocloser(cls, lobby_ID: dict) -> None:
    """ Periodically check if it's time to close a lobby based on last_interaction."""
    sleep_duration = cls.keepalive_duration
    lobby = cls.lobbies[lobby_ID]
    start_time = time.time()
    while True:
      await asyncio.sleep(sleep_duration)
      now = time.time()
      sleep_duration = \
        max(
          lobby['last_interaction'] + cls.refresh_duration, # since the last refresh
          start_time + cls.keepalive_duration, # since lobby creation
        ) - now
      if sleep_duration < 0:
        print(f'Closing lobby #{lobby_ID}.')
        del cls.lobbies[lobby_ID]
        return

  @classmethod
  async def new_lobby(cls, player: Player, region: str, platform: str) -> int:
    """ Create lobby if player not already in a lobby; return lobby identifier.
        raise ValueError if player is already in a lobby on this platform. """
    # Check if they're already in a lobby
    for identifier,lobby in cls.lobbies.items():
      if player in lobby["players"]:
        raise ValueError(f"Player {player.ID=} is already in a lobby.")
    # Make sure they have a record with this region+platform
    _ = player.get_record(region, platform)
    # Find a free lobby ID and create a lobby using it
    for lobby_ID in range(1,1000):
      if lobby_ID not in cls.lobbies:
        now = time.time()
        cls.lobbies[lobby_ID] = {
          "region": region,
          "platform": platform,
          "start_time": now,
          "last_interaction": now,
          "players": {player,},
          "records": { # keep a temporary match result record for each player
            player: {'W': 0, 'L': 0, 'D': 0},
          },
          "invited_players": set(),
        }
        print(f'Created lobby #{lobby_ID}')
        # Spawn a task to automatically close the lobby
        asyncio.create_task(cls.__lobby_autocloser(lobby_ID))
        return lobby_ID

  @classmethod
  def update_lobby(cls, lobby_ID: int) -> None:
    """ Refresh a lobby's last_interaction time. """
    now = time.time()
    debug_print(f"Lobby #{lobby_ID} updating last_interaction to {now}")
    cls.lobbies[lobby_ID]['last_interaction'] = now

  @classmethod
  def join_lobby(cls, player: Player, lobby_ID: int) -> None:
    """ Join `player` to a lobby. Doesn't check platform or region.
        Raise ValueError if lobby is full, doesn't exist, already has `player`,
        or if the player is in another lobby.
        Raise PermissionError if the player is not invited. """
    # Check if lobby exists
    if lobby_ID not in cls.lobbies:
      raise ValueError(f"Lobby #{lobby_ID} does not exist.")
    target_lobby = cls.lobbies[lobby_ID]
    # Check if player is aleady in the lobby
    if player in target_lobby['players']:
      raise ValueError(f"You're already in this lobby.")
    # Check if player is in another lobby
    for lobby in cls.lobbies:
      if player in lobby['players'] and lobby != target_lobby:
        raise ValueError(f"You're already in a lobby.")
    # Check if lobby is full
    if len(target_lobby['players']) > 1:
      raise ValueError(f"Lobby #{lobby_ID} is full.")
    # Check if they're invited
    if player not in target_lobby['invited_players']:
      raise PermissionError(f"Player tried joining lobby #{lobby_ID} without having been invited.")
    # Join the player and update the lobby
    update_lobby(lobby_ID)
    target_lobby['players'].add(player)
    target_lobby['records'][player] = {'W': 0, 'L': 0, 'D': 0}

  ''' # Use `leave_lobby`
  @classmethod
  def close_lobby(cls, lobby_ID: int) -> None:
    """ Close a lobby.
        Raise ValueError if lobby doesn't exist. """
    # Check if lobby exists
    if lobby_ID not in cls.lobbies:
      raise ValueError(f"Lobby #{lobby_ID} does not exist.")
    del cls.lobbies[lobby_ID]
    # Check if player is in lobby
    if player not in target_lobby['players']:
      raise ValueError(f"Player not in lobby #{lobby_ID}.")
    # Leave the lobby without updating the lobby
    target_lobby['players'].remove(player)
    target_lobby['records'].remove(player)
    # Let the lobby auto-close if it's empty
  '''

  @classmethod
  def find_lobby(cls, player: Player) -> int:
    """ Find the lobby which `player` is in and return its ID.
        Raise ValueError if the player isn't in a lobby. """
    for i,lobby in cls.lobbies.items():
      if player in lobby['players']:
        return i
    raise ValueError("Player not in a lobby.")

  @classmethod
  def leave_lobby(cls, player: Player) -> None:
    """ Remove `player` from their lobby.
        Raise ValueError if player isn't in a lobby. """
    lobby_ID = cls.find_lobby(player)
    lobby = cls.lobbies[lobby_ID]
    lobby['players'].remove(player)
    lobby['records'].remove(player)
    cls.update_lobby(lobby_ID)
    # Do not manually close an empty lobby - let close automatically

  @classmethod
  def report_match_result(cls, winner: Player, draw: bool = False) -> int:
    """ Updates the W/L/D of either player and update their Elos.
        `winner` can be either player in a draw. """
    lobby_ID = cls.find_lobby(winner)
    # Let Player p1 be the winner, and p2 the loser
    p1,p2 = None,None
    this_lobby = cls.lobbies[lobby_ID]
    if not draw:
      for player,record in this_lobby['records'].items():
        if player == winner:
          record['W'] += 1
          p1 = player
        else:
          record['L'] += 1
          p2 = player
    else:
      for player,record in this_lobby['records'].items():
        record['D'] += 1
        if p1 is None:
          p1 = player
        else:
          p2 = player
    # Update the Elos
    p1_elo = p1.get_elo(region, platform)
    p2_elo = p2.get_elo(region, platform)
    result = cls.elo_function(p1_elo, p2_result)
    p1[(region, platform)] += result['p1_gain']
    p2[(region, platform)] += result['p2_gain']
