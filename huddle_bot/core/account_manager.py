import json
import os
from faker import Faker
from eth_account import Account
from ..utils import utils
from huddle_bot import config

class _DataHandler_7f3b:
    def __init__(self, private_key_file=config.PRIVATE_KEY_FILE, session_file=config.SESSION_FILE):
        self._v_path1 = private_key_file
        self._v_path2 = session_file
        self._v_faker = Faker()

    def _mthd_a1(self):
        d_list1 = []
        if not os.path.exists(self._v_path1):
            utils.log("error", f"{self._v_path1} not found. Please create it and add private keys, one per line.")
            return d_list1
        
        try:
            with open(self._v_path1, 'r') as f_h:
                for ln in f_h:
                    k_str = ln.strip()
                    if k_str and (k_str.startswith('0x') or len(k_str) == 64): 
                        d_list1.append(k_str)
                    elif k_str: 
                        utils.log("warn", f"Skipping invalid private key format in {self._v_path1}: {k_str[:10]}...")
            if not d_list1:
                utils.log("warn", f"{self._v_path1} is empty or contains no valid keys.")
        except Exception as e:
            utils.log("error", f"Error reading {self._v_path1}: {e}")
        return d_list1

    def _mthd_b2(self):
        if os.path.exists(self._v_path2):
            try:
                with open(self._v_path2, 'r') as f_h:
                    return json.load(f_h)
            except json.JSONDecodeError:
                utils.log("warn", f"Error decoding {self._v_path2}. A new session file will be created.")
            except Exception as e:
                utils.log("error", f"Error reading {self._v_path2}: {e}")
        return {}

    def _mthd_c3(self, sess_obj):
        try:
            with open(self._v_path2, 'w') as f_h:
                json.dump(sess_obj, f_h, indent=4)
            utils.log("info", f"Session data saved to {self._v_path2}")
        except Exception as e:
            utils.log("error", f"Error writing to {self._v_path2}: {e}")
            
    def _mthd_d4(self, pk_str):
        if not pk_str.startswith('0x'):
            return '0x' + pk_str
        return pk_str

    def _Ga33t(self, num_load):
        pk_strings = self._mthd_a1()
        if not pk_strings:
            return []

        sess_map = self._mthd_b2()
        acct_list = []
        is_updated = False

        if num_load == float('inf') or num_load >= len(pk_strings):
            keys_to_run = pk_strings
            num_log_str = "all available" if num_load == float('inf') else num_load
        else:
            keys_to_run = pk_strings[:int(num_load)]
            num_log_str = int(num_load)
        
        utils.log("info", f"Initializing {len(keys_to_run)} session(s) (up to {num_log_str} requested).")

        for pk_orig in keys_to_run:
            pk_norm = self._mthd_d4(pk_orig)
            try:
                eth_inst = Account.from_key(pk_norm)
                _addr = eth_inst.address
                
                acc_sess = sess_map.get(pk_norm)

                if acc_sess and isinstance(acc_sess, dict) and \
                   acc_sess.get('displayName') and acc_sess.get('userAgent'):
                    d_name = acc_sess['displayName']
                    _ua = acc_sess['userAgent']
                    utils.log("info", f"Restored session data for peer {_addr[:6]}...{_addr[-4:]}: Name='{d_name}'")
                else:
                    d_name = self._v_faker.user_name() 
                    _ua = utils.generate_random__ua()
                    sess_map[pk_norm] = {
                        'displayName': d_name,
                        'userAgent': _ua,
                        'address': _addr 
                    }
                    is_updated = True
                    utils.log("info", f"Generated new session for {_addr[:6]}...{_addr[-4:]}: Name='{d_name}'")

                acct_list.append({
                    'privateKey': pk_norm, 
                    'eth_account': eth_inst, 
                    'displayName': d_name,
                    'address': _addr,
                    'userAgent': _ua
                })

            except ValueError as ve: 
                utils.log("error", f"Invalid private key format encountered: {pk_orig[:10]}... Error: {ve}")
            except Exception as e:
                utils.log("error", f"Error Initializing session(s) {pk_orig[:10]}...: {e}")

        if is_updated:
            self._mthd_c3(sess_map)
        
        return acct_list
