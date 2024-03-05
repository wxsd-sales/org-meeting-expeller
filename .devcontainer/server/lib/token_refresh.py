#import aiohttp
#import json
import logging
import traceback

from lib.settings import Settings, LogRecord, CustomFormatter
from lib.spark_asyncio import Spark

logging.setLogRecordFactory(LogRecord)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

class TokenRefresher(object):
    def __init__(self):
        self._refresh_token = Settings.refresh_token

    def build_access_token_payload(self):
        payload = "grant_type=refresh_token&"
        payload += "client_id={0}&".format(Settings.client_id)
        payload += "client_secret={0}&".format(Settings.client_secret)
        payload += "refresh_token={0}".format(self._refresh_token)
        return payload

    async def refresh_token(self):
        logger.debug('TokenRefresher.refresh_token called')
        ret_val = None
        payload = self.build_access_token_payload()
        logger.debug("TokenRefresher.refresh_token payload:{0}".format(payload))
        try:
            resp = await Spark(None).token_post(payload)
            logger.debug("TokenRefresher.refresh_token /access_token Response: {0}".format(resp))
            ret_val = resp["access_token"]
        except Exception as e:
            logger.debug("TokenRefresher.refresh_token Exception:{0}".format(e))
            traceback.print_exc()
        return ret_val