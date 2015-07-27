def plugin(Plugin):
    class Temp(Plugin):
        patterns = ["!(ban|unban|бан|разбан)(?: (.+))?$"]
        name = 'ban_set'
        is_privileged = True
        warn_privileged = False

        def on_msg(self, msg, target):
            user_given = False
            banned = self.group(1).lower() in ['ban', 'бан']
            usr = None
            if self.group(2) != None:
                user_given = True
                usr = self.bot.find_user(self.group(2).strip())
            elif msg.reply != None:
                user_given = True
                usr = msg.reply.src
            if usr == None:
                if user_given:
                    if not banned:
                        user_id = None
                        try:
                            user_id = int(self.group(2))
                        except:
                            pass
                        if user_id != None:
                            old_ban = self.bot.remove_ban_by_id(user_id, target)
                            if old_ban != None:
                                target.send_msg("Разбанен: @{0}".format(old_ban["username"]))
                            return
                    target.send_msg("Пользователь не найден", reply = msg.id)
                else:
                    bans = self.bot.get_bans_for(target)
                    ban_msg = '\n'.join("{0} ({1})".format(ban["username"], ban["user_id"]) for ban in bans)
                    target.send_msg("Активные баны:\n\n" + ban_msg)
            else:
                if banned:
                    if self.bot.add_ban(usr, target):
                        target.send_msg("Забанен: @{0}".format(usr.username))
                        usr.send_msg("Вы забанены за нарушение правил конференции.")
                        target.chat_del_user(usr)
                else:
                    self.bot.remove_ban(usr, target)
                    target.send_msg("Разбанен: @{0}".format(usr.username))

        def is_sudo(self, msg):
            return self.bot.is_sudo(msg) or msg.src.id in self.bot.mod_ids()

    return Temp()