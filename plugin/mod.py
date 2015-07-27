def plugin(Plugin):
    class Temp(Plugin):
        patterns = ["!(mod|unmod)(?: (.+))?$"]
        name = 'mod_set'
        is_privileged = True
        warn_privileged = False

        def on_msg(self, msg, target):
            is_mod = self.group(1).lower() == 'mod'
            if is_mod:
                if self.group(2) != None:
                    usr = self.bot.find_user(self.group(2).strip())
                    if usr:
                        self.bot.add_mod(usr)
                        target.send_msg("{0} добавлен в список модераторов.".format(usr.name.replace('_', ' ')))
                    else:
                        target.send_msg("Пользователь не найден.")
                else:
                    txt = "Список модераторов: {0}".format(", ".join(u['name'] for u in self.bot.mods))
                    target.send_msg(txt)
            else:
                if self.group(2) != None:
                    name = self.group(2)
                    id = None
                    usr = None
                    if name.startswith('@'):
                        name = name[1:]
                        ids = [m['id'] for m in self.bot.mods if m['username'] == name]
                        if len(ids) > 0:
                            id = ids[0]
                    else:
                        ids = [m['id'] for m in self.bot.mods if m['username'] == name or m['name'] == name.replace('_', ' ')]
                        if len(ids) > 0:
                            id = ids[0]
                    if id == None:
                        usr = self.bot.find_user(name)
                        if usr:
                            id = usr.id
                    if id != None:
                        removed = self.bot.remove_mod(id)
                        if removed:
                            target.send_msg("{0} удален из списка модераторов.".format(removed['name']))
                        else:
                            target.send_msg("Пользователь {0} не является модератором.".format(usr.name))
                    else:
                        target.send_msg("Пользователь не найден.")

    return Temp()
