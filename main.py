import tgl
from bot import Bot

#define TGL_PEER_USER 1
#define TGL_PEER_CHAT 2
#define TGL_PEER_GEO_CHAT 3
#define TGL_PEER_ENCR_CHAT 4
#define TGL_PEER_UNKNOWN 0
tgl.PEER_USER = 1
tgl.PEER_CHAT = 2
tgl.PEER_ENCR_CHAT = 4

def on_binlog_replay_end():
  _bot.on_binlog_replay_end()

def on_get_difference_end():
  _bot.on_get_difference_end()

def on_our_id(id):
  _bot.on_our_id(id)

def on_msg_receive(msg):
  _bot.on_msg_receive(msg)

def on_secret_chat_update(peer, what_changed):
  _bot.on_secret_chat_update(peer, what_changed)

def on_user_update(peer, what_changed):
  _bot.on_user_update(peer, what_changed)

def on_chat_update(peer, what_changed):
  _bot.on_chat_update(peer, what_changed)

# def handle_sigint(signal, frame):
#     print("CTRL-C: exiting.")
#     tgl.safe_exit(0)

print("GuardBot starting...")

_bot = Bot()
# !!!ENTER YOUR ID HERE!!!
_bot.sudo_list = []
_bot.banned_ids = []

tgl.set_on_binlog_replay_end(on_binlog_replay_end)
tgl.set_on_get_difference_end(on_get_difference_end)
tgl.set_on_our_id(on_our_id)
tgl.set_on_msg_receive(on_msg_receive)
tgl.set_on_secret_chat_update(on_secret_chat_update)
tgl.set_on_user_update(on_user_update)
tgl.set_on_chat_update(on_chat_update)

# signal.signal(signal.SIGINT, handle_sigint)

_bot.reload_plugins()

print("GuardBot started successfully.")