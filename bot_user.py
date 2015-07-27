from datetime import datetime, timedelta

users = {}

MAX_MESSAGES = 10
MIN_TIME = 30

def now():
    return datetime.now()

class User(object):
    @classmethod
    def get_by_peer(cls, peer):
        global users

        id = peer.id
        if id not in users:
            users[id] = cls(peer)
        return users[id]

    def __init__(self, peer):
        self.peer_id = peer.id
        self.times = []
        self.banned_until = None

    def is_allow(self, msg):
        self.times.append(now())
        if len(self.times) > MAX_MESSAGES:
            self.times = self.times[1:]
            time_diff = self.times[-1] - self.times[0]
            if time_diff.total_seconds() < MIN_TIME:
                #you fucking spammer
                self.banned_until = now() + timedelta(minutes=1)
                print("User {0} banned until {1}".format(self.peer_id, self.banned_until))
        return self.banned_until == None or self.banned_until <= now()