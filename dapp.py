import json
import logging
from collections import defaultdict
from datetime import datetime

from cartesi import DApp, Rollup, RollupData, URLRouter
from cartesi.models import _str2hex

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

dapp = DApp()
url_router = URLRouter()


class Player:
    def __init__(self, address, name):
        self.address = address
        self.name = name
        self.games_played = 0
        self.games_won = 0
        self.total_moves = 0


class Game:
    def __init__(self, game_id, grid_size, num_players):
        self.game_id = game_id
        self.grid_size = grid_size
        self.num_players = num_players
        self.board = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        self.current_player = 0
        self.players = []
        self.winner = None
        self.moves_history = []
        self.start_time = datetime.now()
        self.end_time = None

    def make_move(self, player, row, col):
        if self.board[row][col] is None:
            self.board[row][col] = player
            self.moves_history.append((player, row, col))
            self.current_player = (self.current_player + 1) % self.num_players
            return True
        return False

    def check_winner(self):
        # Check rows, columns, and diagonals
        for i in range(self.grid_size):
            if all(
                self.board[i][j] == self.board[i][0] != None
                for j in range(self.grid_size)
            ):
                self.winner = self.board[i][0]
                return True
            if all(
                self.board[j][i] == self.board[0][i] != None
                for j in range(self.grid_size)
            ):
                self.winner = self.board[0][i]
                return True
        if all(
            self.board[i][i] == self.board[0][0] != None for i in range(self.grid_size)
        ):
            self.winner = self.board[0][0]
            return True
        if all(
            self.board[i][self.grid_size - 1 - i]
            == self.board[0][self.grid_size - 1]
            != None
            for i in range(self.grid_size)
        ):
            self.winner = self.board[0][self.grid_size - 1]
            return True
        return False

    def end_game(self):
        self.end_time = datetime.now()


games = {}
waiting_players = []
players = {}
game_stats = defaultdict(int)


@dapp.advance()
def handle_advance(rollup: Rollup, data: RollupData) -> bool:
    rollup.report("")
    raw_payload = data.str_payload()
    payload = json.loads(raw_payload)
    command = payload.get("command")

    if command == "REGISTER_PLAYER":
        address = payload["data"]["address"]
        name = payload["data"]["name"]
        if address not in players:
            players[address] = Player(address, name)
            rollup.notice(f"Player {name} registered with address {address}")
        else:
            rollup.notice(f"Player with address {address} already exists")

    elif command == "START_GAME":
        grid_size = payload["data"]["grid_size"]
        num_players = payload["data"]["num_players"]
        player_address = payload["data"]["player_address"]

        if player_address not in players:
            rollup.notice(f"Player with address {player_address} not registered")
            return True

        if len(waiting_players) + 1 == num_players:
            game_id = len(games)
            game = Game(game_id, grid_size, num_players)
            game.players = waiting_players + [player_address]
            games[game_id] = game
            waiting_players.clear()

            for player in game.players:
                players[player].games_played += 1

            game_stats["total_games"] += 1
            game_stats[f"games_{grid_size}x{grid_size}"] += 1

            rollup.report(
                json.dumps(
                    {
                        "game_id": game_id,
                        "type": "game_start",
                        "players": game.players,
                        "grid_size": grid_size,
                    }
                )
            )

            rollup.notice(
                f"Game {game_id} started with {num_players} players and grid size {grid_size}"
            )
        else:
            waiting_players.append(player_address)
            rollup.notice(
                f"Player {player_address} added to waiting list. Waiting for {num_players - len(waiting_players) - 1} more players."
            )

    elif command == "MAKE_MOVE":
        game_id = payload["data"]["game_id"]
        player_address = payload["data"]["player_address"]
        row = payload["data"]["row"]
        col = payload["data"]["col"]

        if game_id in games:
            game = games[game_id]
            if game.make_move(player_address, row, col):
                players[player_address].total_moves += 1
                rollup.notice(
                    f"Move made by player {player_address} at ({row}, {col}) in game {game_id}"
                )
                if game.check_winner():
                    game.end_game()
                    players[game.winner].games_won += 1
                    rollup.report(
                        json.dumps(
                            {
                                "game_id": game_id,
                                "type": "game_win",
                                "winner": game.winner,
                            }
                        )
                    )
                    rollup.notice(f"Game {game_id} won by player {game.winner}")
            else:
                rollup.notice(
                    f"Invalid move by player {player_address} at ({row}, {col}) in game {game_id}"
                )
        else:
            rollup.notice(f"Invalid game ID: {game_id}")

    else:
        rollup.notice("Invalid command")

    return True


@url_router.inspect("/waiting_players")
def get_waiting_players():
    return {"waiting_players": waiting_players}


@url_router.inspect("/game/:game_id")
def get_game(game_id):
    game_id = int(game_id)
    if game_id in games:
        game = games[game_id]
        return {
            "game_id": game.game_id,
            "grid_size": game.grid_size,
            "num_players": game.num_players,
            "board": game.board,
            "current_player": game.current_player,
            "players": game.players,
            "winner": game.winner,
            "moves_history": game.moves_history,
            "start_time": game.start_time.isoformat(),
            "end_time": game.end_time.isoformat() if game.end_time else None,
        }
    return {"error": "Game not found"}


@url_router.inspect("/player/:address")
def get_player(address):
    if address in players:
        player = players[address]
        return {
            "address": player.address,
            "name": player.name,
            "games_played": player.games_played,
            "games_won": player.games_won,
            "total_moves": player.total_moves,
            "win_rate": (
                player.games_won / player.games_played if player.games_played > 0 else 0
            ),
        }
    return {"error": "Player not found"}


@url_router.inspect("/game_stats")
def get_game_stats():
    return dict(game_stats)


@url_router.inspect("/leaderboard")
def get_leaderboard():
    sorted_players = sorted(players.values(), key=lambda p: p.games_won, reverse=True)
    return [
        {
            "address": player.address,
            "name": player.name,
            "games_won": player.games_won,
            "win_rate": (
                player.games_won / player.games_played if player.games_played > 0 else 0
            ),
        }
        for player in sorted_players[:10]  # Top 10 players
    ]


@url_router.inspect("/active_games")
def get_active_games():
    return [
        {
            "game_id": game.game_id,
            "grid_size": game.grid_size,
            "num_players": game.num_players,
            "current_player": game.current_player,
            "moves_made": len(game.moves_history),
        }
        for game in games.values()
        if game.winner is None
    ]


if __name__ == "__main__":
    dapp.run()
