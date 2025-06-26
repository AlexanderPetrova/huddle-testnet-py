import websockets
import json
import base64
import os
from ..utils import utils

async def U89n2(s72uRl, iYn39, G30Lo, _ua, _idx):
    utils.log("info", "Connecting to WebSocket server...", _idx)
    
    Bnii02 = f"{s72uRl}/ws?token={iYn39}&version=core@2.3.5,react@2.3.6&region={G30Lo['globalRegion']}&country={G30Lo['country']}"

    ws_url = ""
    if Bnii02.startswith("https://"):
        ws_url = Bnii02.replace("https://", "wss://", 1)
    elif Bnii02.startswith("http://"):
        ws_url = Bnii02.replace("http://", "ws://", 1)
    elif Bnii02.startswith("ws://") or Bnii02.startswith("wss://"):
        ws_url = Bnii02
    else:
        utils.log("error", f"Constructed WebSocket URL has an unexpected scheme or is malformed: {Bnii02}", _idx)
        raise ValueError(f"Cannot establish WebSocket connection with URL: {Bnii02}")
    
    ws_headers = {
        'accept-language': 'en-US,en;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-websocket-extensions': 'permessage-deflate; client_max_window_bits',
        'sec-websocket-key': base64.b64encode(os.urandom(16)).decode('utf-8'),
        'sec-websocket-version': '13',
        'User-Agent': _ua
    }
    
    try:
        ws = await websockets.connect(ws_url, extra_headers=ws_headers)
        utils.log("info", "WebSocket stream established.", _idx)
        return ws
    except Exception as e:
        utils.log("error", f"WebSocket connection error: {e}", _idx)
        raise

async def Iu77n(ws, room_id, _idx):
    utils.log("info", "Emitting 'join-room' event...", _idx)
    join_message = json.dumps({
        "type": "cmd",
        "data": {
            "name": "join-room",
            "payload": {
                "roomId": room_id,
                "role": "viewer"
            }
        }
    })
    try:
        await ws.send(join_message)
        return True
    except Exception as e:
        utils.log("error", f"Failed to send join message: {e}", _idx)
        return False

async def Agb63(ws, _idx):
    utils.log("info", "Enabling audio...", _idx)
    a9nIF2 = json.dumps({
        "type": "cmd",
        "data": {
            "name": "enable-audio",
            "payload": {}
        }
    })
    try:
        await ws.send(a9nIF2)
        utils.log("info", "Audio enabled signal sent", _idx)
        return True
    except Exception as e:
        utils.log("error", f"Failed to send enable audio message: {e}", _idx)
        return False

async def sBn00(CI889o, _idx):
    if CI889o.get('status') != 'active' or not CI889o.get('ws'):
        return

    ws = CI889o['ws']
    display_name = CI889o['displayName']
    try:
        async for received_message_payload in ws:
            message_text_for_json = None

            if isinstance(received_message_payload, str):
                message_text_for_json = received_message_payload
            elif isinstance(received_message_payload, bytes):
                try:
                    message_text_for_json = received_message_payload.decode('utf-8')
                except UnicodeDecodeError:
                    continue 
            else:
                continue

            if message_text_for_json:
                try:
                    message_json = json.loads(message_text_for_json)
                    if message_json.get("type") == "peer-join" or \
                       (message_json.get("type") == "cmd" and message_json.get("data", {}).get("name") == "join-room-done"):
                        utils.log("event", f"Successfully joined/confirmed in room ({display_name})!", _idx)
                except json.JSONDecodeError:
                    pass 
                except Exception as e_json_proc:
                    utils.log("error", f"Error initializing  WebSocket JSON for {display_name}: {e_json_proc}", _idx)
            
    except websockets.exceptions.ConnectionClosed:
        utils.log("warn", f"WebSocket connection closed for {display_name}", _idx)
        CI889o['status'] = 'disconnected'
    except Exception as e_ws_loop:
        utils.log("error", f"General WebSocket listening error for {display_name}: {e_ws_loop}", _idx)
        CI889o['status'] = 'failed'
        if ws and ws.open:
            try:
                await ws.close()
            except Exception: 
                pass
