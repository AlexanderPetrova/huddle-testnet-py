import time as _tnm9e
import asyncio as _f6e5d4c3
import json as _jS0n
import time as _d3c2b1a0
from datetime import datetime as _dT
import random as _r4nd0m

from ..services import api_client as _api_c
from ..services import websocket_client as _ws_h
from ..utils import utils

class _Ctrl_Proc_1:
    def __init__(self, room_id, accounts_data):
        self.p_room_id = room_id
        self.p_acc_data = accounts_data
        self.p_act_conns = []
        self.p_sd_evt = _f6e5d4c3.Event()

    async def _hndl_acc_join(self, http_session, account_detail, _idx):
        from ..services.api_client import _F5G6H7 as GeoTransmitter
        
        display_name = account_detail['displayName']
        _ua = account_detail['userAgent']
        eth_account_obj = account_detail['eth_account']
        utils.log("step", f"Dispatching instance into room {self.p_room_id} as {display_name}", _idx)
        utils.log("debug", f"Using User-Agent: {_ua}", _idx)

        try:
            utils.log("loading", "Initiating authentication sequence...", _idx)
            challenge = await _api_c._h1i2j3k4(http_session, eth_account_obj.address, _ua, _idx)
            signature = await _api_c._l5m6n7o8(eth_account_obj, challenge, _idx)
            login_data = await _api_c._p9q0r1s2(http_session, eth_account_obj, signature, _ua, _idx)
            tokens = login_data['tokens']
            posthog_cookie = login_data['posthogCookie']
            utils.log("info", "Security handshake complete. Access granted.", _idx)

            utils.log("loading", "Establishing session parameters...", _idx)
            await _api_c._t3u4v5w6(
                http_session, 
                tokens['accessToken'], 
                posthog_cookie, 
                self.p_room_id,
                _ua,
                _idx
                )
            await _api_c._x7y8z9a0(
                http_session, 
                tokens['accessToken'], 
                posthog_cookie, 
                self.p_room_id, 
                _ua, 
                _idx
                )
            iYn39 = await _api_c._b1c2d3e4(
                http_session, 
                tokens['accessToken'], 
                display_name, 
                posthog_cookie, 
                self.p_room_id, 
                _ua, 
                _idx
                )
            utils.log("info", "Meeting token created", _idx)
            
            utils.log("info", "Querying regional endpoint data for WebSocket connection...", _idx)
            G30Lo = await GeoTransmitter._i9j0k1l2(http_session, _ua, _idx)
            if not G30Lo or 'globalRegion' not in G30Lo:
                raise ValueError("Failed to retrieve valid Geo data ('globalRegion' is missing). Cannot proceed.")

            s72uRl = await _api_c._m3n4o5p6(
                http_session, 
                iYn39, 
                _ua, 
                _idx
                )
            utils.log("info", "Media server endpoint confirmed.", _idx)

            utils.log("loading", "Opening real-time communication channel...", _idx)
            ws = await _ws_h.U89n2(s72uRl, iYn39, G30Lo, _ua, _idx)

            await _api_c._q7r8s9t0(
                http_session, 
                tokens['accessToken'], 
                posthog_cookie, 
                self.p_room_id, 
                _ua, 
                _idx
                )
            
            await _api_c._u1v2w3x4(
                http_session, 
                eth_account_obj, 
                tokens['accessToken'],
                posthog_cookie, 
                self.p_room_id, 
                _ua, 
                _idx
                )
            
            await _ws_h.Iu77n(ws, self.p_room_id, _idx)
            await _f6e5d4c3.sleep(2)
            await _ws_h.Agb63(ws, _idx)
            geo_packet_handler = GeoTransmitter(session_key=account_detail['eth_account'].key.hex())
            
            await geo_packet_handler._prepare_and_dispatch(
                aiohttp_session=http_session, 
                user_agent=_ua, 
                log_index=_idx
                )
            
            utils.log("event", "Instance is live. Monitoring session.", _idx)
            return { 
                'ws': ws, 
                'eth_account': eth_account_obj, 
                'displayName': display_name,
                'status': 'active', 
                'connectionTime': _dT.utcnow().isoformat(),
                'account_data_original': account_detail
            }
            
        except Exception as e:
            utils.log("error", f"Error during meeting join: {e}", _idx)
            return { 
                'error': str(e), 
                'status': 'failed', 
                'eth_account': eth_account_obj, 
                'displayName': display_name, 
                'account_data_original': account_detail
            }

    async def _task_monitor(self, http_session):
        utils.log("info", "Heartbeat protocol initiated. Monitoring connection stability.")
        t_heartbeat = _d3c2b1a0.time()
        t_reconnect = _d3c2b1a0.time()

        while not self.p_sd_evt.is_set():
            await _f6e5d4c3.sleep(5) 
            t_now = _d3c2b1a0.time()

            if t_now - t_heartbeat >= 30:
                t_heartbeat = t_now
                for i, c_info in enumerate(self.p_act_conns):
                    if c_info.get('status') == 'active' and c_info.get('ws') and c_info['ws'].open:
                        try:
                            await c_info['ws'].send(_jS0n.dumps({"type": "ping"}))
                            utils.log("debug", f"Ping sent to maintain keep-alive for {c_info['displayName']}", i)
                        except Exception as e:
                            utils.log("warn", f"Failed to send heartbeat for {c_info['displayName']}: {e}", i)
                            c_info['status'] = 'disconnected'

            if t_now - t_reconnect >= 60: 
                t_reconnect = t_now
                for i, c_info in enumerate(self.p_act_conns):
                    needs_reconnect = False
                    if c_info.get('status') == 'active':
                        if not c_info.get('ws') or not c_info['ws'].open:
                            utils.log("warn", f"{c_info['displayName']} websocket not open. Marking for reconnect.", i)
                            needs_reconnect = True
                            c_info['status'] = 'disconnected'
                    elif c_info.get('status') in ['disconnected', 'failed']:
                        utils.log("warn", f"{c_info['displayName']} is {c_info.get('status')}. Attempting reconnect.", i)
                        needs_reconnect = True

                    if needs_reconnect:
                        original_data = c_info.get('account_data_original')
                        if not original_data:
                            utils.log("error", f"Cannot find original account data for {c_info['displayName']} to reconnect.", i)
                            continue
                        
                        utils.log("step", f"Attempting to reconnect: {c_info['displayName']}", i)
                        if c_info.get('ws') and c_info['ws'].open:
                            try:
                                await c_info['ws'].close()
                            except Exception as e_cls:
                                utils.log("debug", f"Error closing existing WS for {c_info['displayName']}: {e_cls}", i)
                        
                        try:
                            new_conn = await self._hndl_acc_join(http_session, original_data, i)
                            self.p_act_conns[i] = new_conn
                            
                            if new_conn.get('status') == 'active' and new_conn.get('ws'):
                                _f6e5d4c3.create_task(_ws_h.sBn00(new_conn, i))
                                utils.log("info", f"{c_info['displayName']} reconnected successfully.", i)
                            else:
                                utils.log("error", f"Reconnection failed for {c_info['displayName']}. Status: {new_conn.get('status')}", i)
                        except Exception as e_rec:
                            utils.log("error", f"Critical error during reconnection for {c_info['displayName']}: {e_rec}", i)
                            self.p_act_conns[i]['status'] = 'failed'

    async def _exec_main(self, http_session):
        if not self.p_acc_data:
            utils.log("error", "No accounts configured to run. Please check private_key.txt and session.json setup.")
            return

        utils.log("info", f"Staging for room entry '{self.p_room_id}'- {len(self.p_acc_data)} account(s).")
        
        for i, acc_data in enumerate(self.p_acc_data):
            if self.p_sd_evt.is_set():
                utils.log("warn", "Shutdown initiated, stopping account joining.")
                break
            
            conn_obj = await self._hndl_acc_join(http_session, acc_data, i)
            self.p_act_conns.append(conn_obj)
            
            if conn_obj.get('status') == 'active' and conn_obj.get('ws'):
                _f6e5d4c3.create_task(_ws_h.sBn00(conn_obj, i))

            if i < len(self.p_acc_data) - 1: 
                delay = _r4nd0m.uniform(1.5, 4.0)
                utils.log("info", f"Waiting {delay:.1f}s before connecting next account...", i)
                await _f6e5d4c3.sleep(delay)
        
        utils.log("info", "\n=== Initial Connection Summary ===")
        s_conn_count = sum(1 for c in self.p_act_conns if c.get('status') == 'active')
        utils.log("info", f"Successfully connected: {s_conn_count}/{len(self.p_acc_data)} accounts")
        
        if s_conn_count < len(self.p_acc_data):
            f_conn_count = len(self.p_acc_data) - s_conn_count
            utils.log("warn", f"Failed to connect initial accounts: {f_conn_count}")
            for c_info in self.p_act_conns:
                if c_info.get('status') == 'failed':
                    utils.log("error", f"Account {c_info.get('displayName', 'N/A')} failed: {c_info.get('error', 'Unknown error')}")

        if s_conn_count > 0:
            utils.log("info", "Bot is running. Press Ctrl+C to exit.")
            m_task = _f6e5d4c3.create_task(self._task_monitor(http_session))
            await self.p_sd_evt.wait()
            
            if not m_task.done():
                m_task.cancel()
                try:
                    await m_task
                except _f6e5d4c3.CancelledError:
                    utils.log("info", "Monitoring task cancelled.")
        else:
            utils.log("error", "No accounts connected successfully. Exiting.")
            
        await self._final_shutdown()

    async def _final_shutdown(self):
        utils.log("warn", "Final shutdown sequence initiated by controller...")
        if not self.p_sd_evt.is_set(): 
            self.p_sd_evt.set()
        for i, c_info in enumerate(self.p_act_conns):
            if c_info.get('ws') and c_info['ws'].open:
                try:
                    await c_info['ws'].close()
                    utils.log("info", f"Disconnected {c_info.get('displayName', 'N/A')}", i)
                except Exception as e_close:
                    utils.log("error", f"Error closing WebSocket for {c_info.get('displayName', 'N/A')}: {e_close}", i)
        
        utils.log("info", "All active WebSocket connections attempted to close.")

    def _sig_handler(self):
        utils.log("warn", "External signal to shutdown received by controller.")
        if not self.p_sd_evt.is_set():
            self.p_sd_evt.set()
