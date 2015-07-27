import urllib.request
import re
import mimetypes
import tempfile
import traceback
import os

def done(fn):
    def _done(success, msg):
        print("Success: {0}. Removing temp file: {1}".format(success, fn))
        os.remove(fn)
    return _done

class Plugin(object):
    patterns = []
    name = None
    bot = None
    match = None
    is_privileged = False
    warn_privileged = True
    is_conf = False
    is_accept_fwd = False

    def is_accept_service_msg(self, msg):
        return False

    def on_service_msg(self, msg, target):
        pass

    def is_accept_msg(self, msg):
        return self.match_patterns(msg.text)

    def match_patterns_real(self, text, patterns):
        if not text:
            return False
        for pat in patterns:
            match = re.match(pat, text, re.I | re.S)
            if match:
                print("{0}: matched {1}".format(self.name, pat))
                self.match = match
                return True
        return False

    def match_patterns(self, text):
        return self.match_patterns_real(text, self.patterns)

    def on_msg(self, msg, target):
        pass

    def group(self, i):
        if i <= len(self.match.groups()):
            return self.match.group(i)
        else:
            return None

    def download_to_temp_file(self, url):
        try:
            print("Downloading: {0}".format(url))
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0')            
            with urllib.request.urlopen(req) as web:
                ct = web.getheader('Content-type')
                if not ct:
                    return None
                ext = mimetypes.guess_extension(ct)
                if not ext:
                    return None
                if ext == ".jpe":
                    ext = ".jpeg"
                buf = web.read()
                print("Image size: {0}".format(len(buf)))
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
                fname = f.name
                f.write(buf)
            return fname
        except:
            traceback.print_exc()
            return None

    def send_image_from_url(self, target, url):
        fn = self.download_to_temp_file(url)
        if not fn:
            target.send_msg("Не загружается: {0}".format(url))
        else:
            target.send_photo(fn, done(fn))        

    def trigger(self, msg, target, text):
        self.bot.trigger(msg, target, text)

    def get_data_fn(self, fn):
        return self.bot.get_data_fn(fn)

    def is_sudo(self, msg):
        return self.bot.is_sudo(msg)

    def check_sudo(self, msg, target):
        if not self.is_sudo(msg):
            print("sudo failed")
            if self.warn_privileged:
                target.send_msg('You are not my master!', reply=msg.id)
            return False
        return True