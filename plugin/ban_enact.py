import time

def plugin(Plugin):
    class Temp(Plugin):
        name = 'ban_enact'

        def is_accept_msg(self, msg):
            return self.bot.is_banned(msg.src.id, msg.dest.id)

        def on_msg(self, msg, target):
            target.chat_del_user(msg.src)

        def is_accept_service_msg(self, msg):
            #return self.bot.is_banned(msg.src.id, msg.dest.id) and msg.action != 9 # delete_user
            return msg.action != 9

        def on_service_msg(self, msg, target):
            if self.bot.is_banned(msg.src.id, target.id):
                target.chat_del_user(msg.src)
                return
            print(repr(msg))
            for ban in self.bot.get_bans_for(target):
                usr = self.bot.find_user(str(ban['user_id']))
                print("Trying to ban: {0}".format(ban['user_id']))
                if usr:
                    #if not slept:
                    #    slept = True
                    #    time.sleep(0.1)
                    print("Banning: {0}".format(usr.username))
                    target.chat_del_user(usr)
                else:
                    print("User not found: {0}".format(ban['user_id']))
            #target.chat_del_user(msg.src)

    return Temp()