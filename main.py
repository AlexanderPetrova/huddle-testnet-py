import asyncio
import sys
import signal
import argparse
import re
import aiohttp
import os
import json

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

try:
    from huddle_bot.core.account_manager import _DataHandler_7f3b
    from huddle_bot.core.controller import _Ctrl_Proc_1
    from huddle_bot.utils.utils import log
except ImportError as e:
    print(f"[ERROR] Failed to import huddle_bot modules: {e}")
    print("Ensure main.py is in the 'huddle_bot_project' directory, and 'huddle_bot' is a subdirectory.")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Sys.path: {sys.path}")
    sys.exit(1)

ROOM_ID_FILE = "last_room_id.json"

def save_room_id(room_id: str):
    try:
        with open(ROOM_ID_FILE, 'w') as f:
            json.dump({"last_room_id": room_id}, f)
        log("info", f"Room ID '{room_id}' saved for future use.")
    except IOError as e:
        log("error", f"Failed to save Room ID to {ROOM_ID_FILE}: {e}")

def load_room_id() -> str | None:
    if not os.path.exists(ROOM_ID_FILE):
        return None
    try:
        with open(ROOM_ID_FILE, 'r') as f:
            data = json.load(f)
            return data.get("last_room_id")
    except json.JSONDecodeError as e:
        log("error", f"Error decoding {ROOM_ID_FILE}: {e}. File might be corrupted.")
        os.remove(ROOM_ID_FILE) 
        return None
    except IOError as e:
        log("error", f"Failed to load Room ID from {ROOM_ID_FILE}: {e}")
        return None

controller_instance = None

def signal_handler_fn(sig, frame):
    log("warn", f"Signal {signal.Signals(sig).name if hasattr(signal, 'Signals') else sig} received, initiating shutdown...")
    if controller_instance:
        controller_instance._sig_handler()
    else:
        log("error", "Controller not initialized for graceful shutdown via signal. Exiting.")
        sys.exit(1)

async def main_logic():
    global controller_instance

    parser = argparse.ArgumentParser(description="Huddle01 Testnet Bot")
    parser.add_argument("room_id", nargs='?', help="Huddle01 Room ID atau full URL untuk bergabung.")
    parser.add_argument("-n", "--num_accounts", type=int, default=0,
                        help="The number of accounts to be used from private_key.txt (0 for all).")

    args = parser.parse_args()
    room_id_input = args.room_id
    num_accounts_to_use = args.num_accounts

    if not room_id_input:
        last_room_id = load_room_id()
        if last_room_id:
            while True:
                choice = input(f"The last room ID used was “{last_room_id}”. Use this (y/n)? ").strip().lower()
                if choice == 'y':
                    room_id_input = last_room_id
                    log("info", f"Using the last Room ID: {room_id_input}")
                    break
                elif choice == 'n':
                    break
                else:
                    log("error", "Invalid selection. Please enter “y” or “n”.")
        
        if not room_id_input:
            while True:
                room_id_input = input("Enter the Huddle01 room ID to join: ").strip()
                if room_id_input:
                    break
                log("error", "Room ID cannot be empty.")

    if 'huddle01.app/room/' in room_id_input:
        match = re.search(r'huddle01\.app/room/([^/?]+)', room_id_input)
        if match:
            room_id_input = match.group(1)
        else:
            log("error", f"Unable to extract Room ID from URL: {room_id_input}")
            sys.exit(1)

    save_room_id(room_id_input)
    
    if num_accounts_to_use < 0:
        log("warn", "The account balance cannot be negative. Use all available accounts from private_key.txt.")
        num_accounts_to_use = 0
    elif num_accounts_to_use == 0:
        log("info", "Using all available accounts from private_key.txt.")

    account_mgr = _DataHandler_7f3b()
    accounts_data = account_mgr._Ga33t(num_load=float('inf') if num_accounts_to_use == 0 else num_accounts_to_use)

    if not accounts_data:
        log("error", "No accounts loaded. Please check the settings in “private_key.txt” and “session.json”. Log out.")
        sys.exit(1)

    if num_accounts_to_use > 0 and len(accounts_data) < num_accounts_to_use:
        log("warn", f"{num_accounts_to_use} accounts are required, but only {len(accounts_data)} are available/loaded.")

    final_accounts_to_run_with = accounts_data
    controller_instance = _Ctrl_Proc_1(room_id=room_id_input, accounts_data=final_accounts_to_run_with)

    loop = asyncio.get_running_loop()
    for sig_name_enum in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig_name_enum, lambda s=sig_name_enum: signal_handler_fn(s, None))
        except (NotImplementedError, AttributeError, RuntimeError):
            signal.signal(sig_name_enum, signal_handler_fn)

    connector = aiohttp.TCPConnector(limit_per_host=25, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as http_session:
        try:
            await controller_instance._exec_main(http_session)
        except asyncio.CancelledError:
            log("warn", "The main execution task was cancelled..")
        except Exception as e:
            log("error", f"An unhandled error occurred in the main execution: {e}")

        finally:
            log("info", "Main execution completed or interrupted. Starting final cleanup.")
            if controller_instance and not controller_instance.p_sd_evt.is_set():
                controller_instance._sig_handler()
                await controller_instance.p_sd_evt.wait()

            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            if tasks:
                log("warn", f"Cancelling {len(tasks)} remaining tasks...")
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
            log("info", "Application shutdown complete.")

if __name__ == '__main__':
    from huddle_bot.utils import utils
    for sig_name_enum_main in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig_name_enum_main, signal_handler_fn)
    
    try:
        print("\033[H\033[J")
        utils._PlisFE_banner()
        asyncio.run(main_logic())
    except KeyboardInterrupt:
        log("warn", "\nKeyboardInterrupt caught at top level. Application will exit.")
    except SystemExit as se: 
        if se.code != 0:
             log("error", f"Application exited with code {se.code}")
    except Exception as e_top:
        log("error", f"Top-level unhandled exception: {e_top}")
