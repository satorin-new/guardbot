import os
from functools import partial
from pluginbase import PluginBase
from bot_user import User
from threading import Timer
import json
import os.path

# For easier usage calculate the path relative to here.
here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)

import tgl
import traceback
from plugin import Plugin
from datetime import datetime

def emptycb(success):
    tgl.status_offline()

def go_offline(success, msg):
    tgl.status_offline()

class Bot(object):
    def __init__(self):
        self.replay_ended = False
        self.id = None
        self.plugins = []
        self.start_date = datetime.now()
        self.sudo_list = []
        self.mods = []
        self.banned_ids = []
        self.peer = None
        self.last_fwd_cb = None
        self.user_map = {}
        self.user_map_name = {}
        self.bans = []
        self.populated = False
        self.ban_fn = self.get_data_fn('bans.json')
        self.load_bans()
        self.mod_fn = self.get_data_fn('mods.json')
        self.load_mods()

    def mod_ids(self):
        return [m['id'] for m in self.mods]

    def add_mod(self, usr):
        if usr.id not in self.mod_ids():
            self.mods.append({'id': usr.id, 'username': usr.username, 'name': usr.name.replace('_', ' ')})
            self.save_mods()
        return True

    def remove_mod(self, usr_id):
        removed = [m for m in self.mods if m['id'] == usr_id]
        if len(removed) > 0:
            self.mods = [m for m in self.mods if m['id'] != usr_id]
            self.save_mods()
            return removed[0]
        else:
            return None

    def find_user(self, username):
        if username.startswith('@'):
            username = username[1:]
        return self.user_map_name.get(username)

    def save_user(self, user):
        if user.type_name != 'user':
            return
        username = user.username
        if username != None:
            if username.startswith('@'):
                username = username[1:]
            #print(username)
            self.user_map_name[username] = user
        else:
            username = '(no name)'
        uid = str(user.id)
        if uid not in self.user_map_name:
            print("Added user @{0}".format(username))
            self.user_map_name[uid] = user
        #found = self.find_user(username)
        #print("Found? {0}".format(found))

    def add_ban(self, usr, target):
        usr_id = usr.id
        if usr_id != self.id and usr_id not in self.sudo_list and usr_id not in self.mod_ids():
            self.bans.append({'username': usr.username, 'user_id': usr.id, 'chat_id': target.id})
            self.save_bans()
            return True
        else:
            target.send_msg("Обломись :(")
            return False

    def remove_ban(self, usr, target):
        return self.remove_ban_by_id(usr.id, target)

    def remove_ban_by_id(self, usr_id, target):
        removed = [b for b in self.bans if b['user_id'] == usr_id and b['chat_id'] == target.id]
        if len(removed) > 0:
            self.bans = [b for b in self.bans if b not in removed]
            self.save_bans()
            return removed[0]
        else:
            return None

    def is_banned(self, usr_id, chat_id):
        return len([1 for b in self.bans if b['user_id'] == usr_id and b['chat_id'] == chat_id]) > 0

    def save_bans(self):
        with open(self.ban_fn, "w") as f:
            f.write(json.dumps(self.bans, ensure_ascii=False))

    def load_bans(self):
        if os.path.exists(self.ban_fn):
            with open(self.ban_fn) as f:
                content = f.read()
                self.bans = json.loads(content)

    def save_mods(self):
        with open(self.mod_fn, "w") as f:
            f.write(json.dumps(self.mods, ensure_ascii=False))

    def load_mods(self):
        if os.path.exists(self.mod_fn):
            with open(self.mod_fn) as f:
                content = f.read()
                self.mods = json.loads(content)                

    def get_bans_for(self, target):
        return [b for b in self.bans if b['chat_id'] == target.id]

    def on_msg_receive(self, msg):
        self.save_user(msg.src)
        if msg.fwd_src:
            self.save_user(msg.fwd_src)
        if not self.ready():
            return
        if not self.is_valid_msg(msg):
            return
        self.user_map[msg.src.id] = msg.src.name
        #print("got: {0}".format(msg.text))
        if self.is_own_msg(msg):
            #print("You got owned...")
            if self.last_fwd_cb != None and msg.fwd_date != None:
                print("You got it!")
                fwd_cb = self.last_fwd_cb
                self.last_fwd_cb = None
                fwd_cb(True, msg)
            if self.peer == None:
                self.peer = msg.src
            tgl.status_offline()
            return
        target = self.target(msg)
        print("From: {0} ({1})".format(msg.src.id, target.id))
        if not self.is_sudo(msg) and target.id in self.banned_ids:
            return
        if msg.text == '!!r' and self.is_sudo(msg):
            target.mark_read(emptycb)
            self.reload_plugins()
            target.send_msg("Перезагрузила.", go_offline)
            return
        user = User.get_by_peer(msg.src)
        if self.is_sudo(msg):
            allow = True
        else:
            allow = None
        for plugin in self.plugins:
            try:
                if msg.fwd_src:
                    if not plugin.is_accept_fwd:
                        continue
                if msg.service:
                    if plugin.is_accept_service_msg(msg):
                        if allow == None:
                            allow = user.is_allow(msg)
                        if allow:
                            #target.send_typing(emptycb)
                            target.mark_read(emptycb)

                            if not plugin.is_privileged or plugin.check_sudo(msg, target):
                                plugin.on_service_msg(msg, target)
                            #target.send_typing_abort(emptycb)
                else:
                    if plugin.is_accept_msg(msg):
                        if allow == None:
                            allow = user.is_allow(msg)
                        if allow:
                            #target.send_typing(emptycb)
                            target.mark_read(emptycb)

                            if not plugin.is_privileged or plugin.check_sudo(msg, target):
                                if plugin.is_conf and target.type != tgl.PEER_CHAT and not plugin.is_sudo(msg):
                                    target.send_msg("Эта команда только для конференций. Извини!", reply = msg.id)
                                else:
                                    plugin.on_msg(msg, target)
                            #target.send_typing_abort(emptycb)
            except:
                traceback.print_exc()
                #target.send_typing_abort(emptycb)
        tgl.status_offline()

    def on_binlog_replay_end(self):
        print("** REPLAY_ENDED **")
        self.replay_ended = True
        tgl.status_offline()
        if not self.populated:
            self.populated = True
            self.populate_dlg()
            return

    def on_our_id(self, id):
        print("** OUR ID: {0} **".format(id))
        self.id = id

    def on_get_difference_end(self):
        pass

    def on_user_update(self, peer, what_changed):
        pass

    def on_chat_update(self, peer, what_changed):
        pass

    def on_secret_chat_update(self, peer, what_changed):
        pass

    def reload_plugins(self):
        print("Reloading plugins...")

        plugin_base = PluginBase(package='bot.plugins')
        plugin_source = plugin_base.make_plugin_source(searchpath=[get_path('plugin')], persist = True)
        self.plugins = []

        for _plugin in plugin_source.list_plugins():
            print("Loading: " + _plugin)
            try:
                plugin_mod = plugin_source.load_plugin(_plugin)
                plugin_instance = plugin_mod.plugin(Plugin)
                if plugin_instance:
                    if not plugin_instance.name:
                        plugin_instance.name = _plugin
                    self.add_plugin(plugin_instance)
                else:
                    print("Skipped: " + _plugin)
            except:
                traceback.print_exc()

    def add_plugin(self, plugin):
        self.plugins.append(plugin)
        plugin.bot = self

    def ready(self):
        return self.replay_ended and self.id

    def is_valid_msg(self, msg):
        if msg.date < self.start_date:
            return False
        if msg.dest.type == tgl.PEER_ENCR_CHAT:
            return False
        if msg.src.id == 777000:
            return False
        return True

    def is_own_msg(self, msg):
        return msg.out or msg.src.id == self.id

    def target(self, msg):
        if msg.dest.type == tgl.PEER_CHAT:
            return msg.dest
        else:
            return msg.src

    def is_sudo(self, msg):
        return msg.src.id in self.sudo_list

    def trigger(self, msg, target, text):
        for plugin in self.plugins:
            try:
                if plugin.match_patterns(text):
                    #target.send_typing(emptycb)
                    target.mark_read(emptycb)

                    if plugin.is_privileged and not self.is_sudo(msg):
                        print("sudo failed")
                        if plugin.warn_privileged:
                            target.send_msg('You are not my master!', reply=msg.id)
                    else:
                        plugin.on_msg(msg, target)
            except:
                traceback.print_exc()
                return None

    def get_data_fn(self, fn):
        return get_path('data', fn)

    def get_msg_by_id(self, target, id, cb):
        def fwd_cb(success, msg):
            if not success or msg != None:
                self.last_fwd_cb = None
                cb(success, msg)
        self.last_fwd_cb = cb
        if self.peer:
            self.peer.fwd_msg(id, fwd_cb)
        else:
            target.fwd_msg(id, fwd_cb)

    def resolve_user(self, user_id):
        return self.user_map.get(user_id)

    def populate_dlg(self):
        def cb(success, dlg_list):
            peers = (d['peer'] for d in dlg_list)
            for p in peers:
                self.save_user(p)
        tgl.get_dialog_list(cb)