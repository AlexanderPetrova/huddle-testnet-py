# Huddle01 Testnet Automations

A Python-based bot designed to automate participation in Huddle01 testnet rooms using multiple accounts. The bot handles authentication, session management, WebSocket communication, and aims to maintain presence in the specified Huddle01 room.

## Features

* **Multi-Account Support:** Load multiple Ethereum private keys to join a room with distinct participants.
* **Automated Room Joining:** Automatically handles the process of joining a Huddle01 room.
* **Wallet Authentication:** Implements the challenge-response signature mechanism for Huddle01 login.
* **Session Management:** Persists display names and user agents for accounts across sessions (`session.json`).
* **Randomized User Agents:** Generates random, yet plausible, user agents for each account.
* **WebSocket Communication:** Establishes and manages WebSocket connections for in-room interactions.
* **Graceful Shutdown:** Handles `SIGINT` (Ctrl+C) and `SIGTERM` for a clean shutdown process.
* **Connection Monitoring & Auto-Reconnect:** Monitors active connections and attempts to reconnect if a session drops.
* **Configurable Account Usage:** Specify the number of accounts to use or use all available from `private_key.txt`.
* **Dynamic Room ID Input:** Accepts room ID directly or extracts it from a full Huddle01 room URL.
* **Testnet Participation:** Includes functionality aimed at interacting with testnet-specific features (e.g., points collection).

## Prerequisites

* Python 3.8 or higher
* `pip` (Python package installer)

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/AlexanderPetrova/huddle-testnet-py.git
    cd huddle-testnet-py
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
     ```
    ### On Windows
    ```bash
    venv\Scripts\activate
    ```
    ### On macOS/Linux
    ```bash
    source venv/bin/activate
    ```

4.  **Install dependencies:**

    The `requirements.txt` ensure your `requirements.txt` looks like this before installing:
    ```txt
    aiohttp==3.9.5
    websockets==12.0
    eth-account==0.12.0
    Faker==25.8.0
    colorama==0.4.6
    brotli==1.1.0
    ```
    Then install:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **`private_key.txt`:**
    * Create a file named `private_key.txt` in the root directory of the project (same level as `main.py`).
    * Add your Ethereum private keys to this file, one private key per line.
    * Keys can be with or without the `0x` prefix.
    * Example:
        ```
        0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
        fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321
        ```

2.  **`session.json`:**
    * This file will be automatically created and updated by `account_manager.py` when the bot runs for the first time with new private keys.
    * It stores generated display names and user agents associated with each private key to maintain consistency across sessions. You generally don't need to edit this file manually.

3.  **`config.py`:**
    * This file contains API endpoints and the `NEXTJS_BUILD_ID`.
    * `NEXTJS_BUILD_ID`: This ID is used for fetching certain room data. If Huddle01 updates its frontend, this ID might change, potentially causing errors when the bot tries to fetch room metadata. If you encounter such issues, you may need to find and update this value by inspecting network requests on the Huddle01 website.

## Usage

Run the `main.py` script from the project's root directory.

**Basic syntax:**
```bash
python main.py [room_id_or_url] [-n num_accounts]
```
### Arguments:

room_id_or_url (optional):
`The Huddle01 Room ID (e.g., abc-defg-hij).`
Or the full Huddle01 room URL (e.g., https://huddle01.app/room/abc-defg-hij).
If not provided, the script will prompt you to enter it.
`-n num_accounts, --num_accounts num_accounts (optional):`

The number of accounts to use from `private_key.txt.`
If 0 (default) or not specified, all valid accounts from `private_key.txt` will be used.
If a positive number is given, that many accounts will be loaded. 

If fewer accounts are available than requested, a warning will be shown, and all available accounts will be used.
A negative number will be treated as a request for all accounts.

### Examples:

Join a room using its ID with all accounts:

```Bash
python main.py abc-defg-hij
```
Join a room using its URL with the first 5 accounts from private_key.txt:

```Bash
python main.py [https://huddle01.app/room/abc-defg-hij](https://huddle01.app/room/abc-defg-hij) -n 5
```
Run without arguments (will prompt for Room ID):

```Bash
python main.py
```
The bot will then ask: `Enter the Huddle01 room ID to join:`

The bot will log its actions to the console, including information about account connections, errors, and WebSocket events. Press Ctrl+C to initiate a graceful shutdown.

### File Structure Overview
```yaml.
HUDDLE-TESTNET-BOT/
│── private_key.txt
│── session.json
│── last_room_id.json
│
├── huddle_bot/
│   ├── __init__.py
│   │
│   ├── config.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── account_manager.py
│   │   └── controller.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── api_client.py
│   │   └── websocket_client.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── banner.py
│       ├── utils.py
│       └── logger.py
│
├── main.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Dependencies
Key dependencies are listed in requirements.txt and include:

- `aiohttp`: For asynchronous HTTP requests.
- `websockets`: For WebSocket communication.
- `eth-account`: For Ethereum account and signature handling.
- `Faker`: For generating random display names.
- `colorama`: For colored console output.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any bugs, features, or improvements.

## Disclaimer

* This bot is intended for educational and testing purposes, particularly for interacting with the Huddle01 testnet environment.
* Users are solely responsible for ensuring their use of this bot complies with Huddle01's terms of service and any applicable platform policies.
* The maintainers of this project are not responsible for any misuse, account restrictions, or other consequences arising from the use of this bot.

## License
MIT License none, "This project is unlicensed."

