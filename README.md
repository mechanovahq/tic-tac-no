#Tic-Tac-No

## Introduction

Welcome to tic-tac-no, designed to bring a new twist to the classic Tic-Tac-Toe game, Powered by Cartesi.

## Getting Started

### Step 1: Clone the Repository

Begin by cloning the repository to your local machine:

```bash
git clone https://github.com/dasoourcecode/tic-tac-no.git
cd tic-tac-no
```

### Step 2: Install Dependencies

Ensure that Python 3.7+ is installed on your system. Then, install the necessary packages:

```bash
pip install -r requirements.txt
```

### Step 4: Launch the Application

Start the DApp with the following command:

```bash
python main.py
```

## How to Use

### Payloads

To interact with the DApp, you’ll use a structured payload like this:

```json
{
  "command": "COMMAND_NAME",
  "data": {
    // Command-specific data
  }
}
```

### Executing Commands

Use the `cartesi send` utility to send commands. Below are examples of common actions:

- **Register as a Player:**

  ```bash
  cartesi send --payload '{
    "command": "REGISTER_PLAYER",
    "data": {
      "address": "0x1234...",
      "name": "johnny"
    }
  }'
  ```

- **Start a New Game:**

  ```bash
  cartesi send --payload '{
    "command": "START_GAME",
    "data": {
      "grid_size": 3,
      "num_players": 2,
      "player_address": "0x1234..."
    }
  }'
  ```

- **Make Your Move:**
  ```bash
  cartesi send --payload '{
    "command": "MAKE_MOVE",
    "data": {
      "game_id": 1,
      "player_address": "0x1234...",
      "row": 0,
      "col": 0
    }
  }'
  ```

### Notifications and Rewards

- After each command, you’ll receive a notification with the operation's outcome.
- A voucher detailing game specifics is issued when a game starts.
- Upon a game’s conclusion, the final results will also be provided in a voucher.

### Accessing Game Information

Retrieve game data and stats with these requests:

- **Check Waiting Players:**

  ```http
  GET {{INSPECT_URL}}/waiting_players
  ```

- **View Game Details:**

  ```http
  GET {{INSPECT_URL}}/game/:game_id
  ```

- **Player Information:**

  ```http
  GET {{INSPECT_URL}}/player/:address
  ```

- **Game Statistics:**

  ```http
  GET {{INSPECT_URL}}/game_stats
  ```

- **Leaderboard:**

  ```http
  GET {{INSPECT_URL}}/leaderboard
  ```

- **Active Games:**
  ```http
  GET {{INSPECT_URL}}/active_games
  ```

## Game Mechanics

1. Register before joining any game.
2. Choose from various grid sizes (3x3, 4x4, 5x5) and number of players.
3. Players alternate turns, marking their symbols on the grid.
4. The first player to align their symbols in a row, column, or diagonal wins.
5. A full grid without a winner results in a draw.

## Key Features

- Register players with unique blockchain addresses.
- Enjoy flexible grid sizes and player counts.
- Track game history and player statistics.
- Climb the leaderboard and review active games.

## Security Measures

- Every move is validated to ensure it’s by the correct player and within the rules.
- The DApp relies on Cartesi's secure framework to protect game integrity.

## Current Limitations

- No Frontend(working on learning the skills to add that)
- No tie-breaker for games with more than two players.
- Absence of a time limit for moves could result in prolonged games.

## Future Upgrades

- Implement Frontend(ASAP)
- Introduce time limits for each move.
- Support for tournament play.
- Expand winning patterns for larger grids.
- Implement a player rating system based on match difficulty.

If you encounter any issues or have suggestions, please feel free to reach out to me or raise an issue
