def plugin(Plugin):
    class Temp(Plugin):
        patterns = ["^!id$"]
        name = 'ID'

        def on_msg(self, msg, target):
            target.send_msg("{0}".format(msg.src.id), reply = msg.id)

    return Temp()