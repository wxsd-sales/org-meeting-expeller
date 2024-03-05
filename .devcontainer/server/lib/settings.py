import logging
import os
from dotenv import load_dotenv

load_dotenv()

def remove_items(mylist, remove_item):
    return [i for i in mylist if i != remove_item]

class Settings(object):
    port = int(os.environ.get("MY_APP_PORT"))
    dev_mode = os.environ.get("DEV_MODE","").lower() == "true"

    alert_bot_token = os.environ.get("WEBEX_ALERT_BOT_TOKEN")
    alert_room_id = os.environ.get("WEBEX_ALERT_ROOM_ID")

    client_id = os.environ.get("WEBEX_CLIENT_ID")
    client_secret = os.environ.get("WEBEX_CLIENT_SECRET")
    refresh_token = os.environ.get("WEBEX_REFRESH_TOKEN")

    my_uri = os.environ.get("MY_URI").strip("/")
    redirect_uri = my_uri + "/oauth"
    
    scopes = os.environ.get("WEBEX_SCOPES")

    admin_email = os.environ.get("ADMIN_EMAIL")
    expel_domains = os.environ.get("EXPEL_DOMAINS").split(",")


class LogRecord(logging.LogRecord):
    def getMessage(self):
        msg = self.msg
        if self.args:
            if isinstance(self.args, dict):
                msg = msg.format(**self.args)
            else:
                msg = msg.format(*self.args)
        return msg


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    blue = "\x1b[31;34m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: blue + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)