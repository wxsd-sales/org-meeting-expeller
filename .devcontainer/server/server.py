
import asyncio
import json
import logging
import traceback
import urllib.parse

from aiohttp import web
from datetime import datetime, timedelta
from lib.settings import Settings, LogRecord, CustomFormatter
from lib.spark_asyncio import Spark
from lib.token_refresh import TokenRefresher

import lib.oauth as oauth

logging.setLogRecordFactory(LogRecord)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


class SharedSpark(object):
    admin = None
    orgId = None

async def ensure_admin_is_cohost(meeting_series_id, host_email):
    logger.debug("meeting_series_id: {0}".format(meeting_series_id))
    #Add Admin as CoHost/Invitee
    try:
        list_invitees_result = await SharedSpark.admin.get("https://webexapis.com/v1/meetingInvitees?meetingId={0}&hostEmail={1}".format(meeting_series_id, urllib.parse.quote(host_email)))
        existing_data = None
        for item in list_invitees_result.get('items',[]):
            if item.get("email") == Settings.admin_email:
                existing_data = item
                break
        logger.debug("existing data: {0}".format(existing_data))
        if existing_data and existing_data.get("coHost") == False:
            data = {"email":Settings.admin_email,
                    "coHost":True,
                    "hostEmail":host_email}
            update_invitees_result = await SharedSpark.admin.put("https://webexapis.com/v1/meetingInvitees/{0}".format(existing_data.get("id")), data)
            logger.debug("Updated Admin as CoHost Resp:")
            logger.debug(update_invitees_result)
        elif existing_data == None:
            data = {"meetingId":meeting_series_id,
                    "email":Settings.admin_email,
                    "coHost":True,
                    "hostEmail":host_email}
            create_invitee_result = await SharedSpark.admin.post("https://webexapis.com/v1/meetingInvitees", data)
            logger.debug("Added Admin as CoHost Invitee status_code:")
            logger.debug(create_invitee_result)
        else:
            logger.debug("Admin is already CoHost Invitee")
    except Exception as ex:
        traceback.print_exc()
        logger.debug("Failed to add Admin as CoHost/Invitee.")

async def main(request):
    """
    """
    logger.debug("MAIN HIT")
    default_error_msg = "An unknown error occurred."
    response = {}
    try:
        body = await request.json()
    except Exception as e:
        logger.warning("Bad JSON, request probably not from Webex.")
        return web.HTTPInternalServerError()
    try:
        if body.get('orgId') == SharedSpark.orgId:
            if body.get('event') == "joined":
                logger.debug(body)
                #Get Meeting Participant Details
                participant_id = body.get("data")["id"]
                host_email = body.get("data")["hostEmail"]
                logger.debug("participant_id: {0}".format(participant_id))
                url = "https://webexapis.com/v1/meetingParticipants/{0}?hostEmail={1}".format(participant_id, urllib.parse.quote(host_email))
                participant = await SharedSpark.admin.get(url)
                logger.debug("Participant Email: {0}".format(participant.get("email")))
                if participant.get("email","").endswith(tuple(Settings.expel_domains)):
                    logger.debug("Participant {0} should be banned, expelling now!".format(participant["email"]))

                    meeting_id = body.get("data")["meetingId"]
                    meeting_series_id, unused = meeting_id.split("_",1)
                    await ensure_admin_is_cohost(meeting_series_id, host_email)

                    #Expel participant
                    data = {"expel":True}
                    expel_result = await SharedSpark.admin.put(url, data)
                    logger.debug("expel result: {0}".format(expel_result))
                    logger.debug("Participant expelled!")
                    msg = "<blockquote class=\"success\"><p>{0} - expelled from meeting series: {1} (meeting host:{2}).</p>".format(participant["email"], meeting_series_id, host_email)
                    msg_data = {"roomId":Settings.alert_room_id, "html":msg}
                    post_msg_result = await Spark(Settings.alert_bot_token).post("https://webexapis.com/v1/messages", msg_data)
                else:
                    logger.debug("Participant is valid, not expelling.")
            else:
                logger.debug("Event was {0}.".format(body.get('event')))
        else:
            logger.warning("Bad OrgId, we're return 4XX in an effort to tell Webex to disable this webhook.")
            return web.HTTPForbidden()
    except Exception as e:
        response = {"error": default_error_msg}
        traceback.print_exc()
        logger.debug("Something went wrong!  Particpant was likely not expelled!")
    return web.Response(text=json.dumps(response), content_type="application/json")


async def main_page(request):
    if request.cookies.get('id'):
        msg = "Thank you. We've notified the application admin of your sign in."
        logger.debug(msg)
        return web.Response(text=msg)
    else:
        return web.HTTPFound("/oauth")
    

async def is_alive(request):
    """
    GET Health check
    """
    return web.Response(text='OK/Alive')


async def initial_config():
    webhooks = await SharedSpark.admin.get('https://webexapis.com/v1/webhooks?ownedBy=org')
    webhook_exists = False
    for webhook in webhooks.get("items", []):
        if webhook.get('resource') == 'meetingParticipants' and webhook.get('targetUrl').strip("/") == Settings.my_uri:
            if webhook.get('status') == "active":
                logger.debug("Webhook exists and is active.")
                SharedSpark.orgId = webhook.get('orgId')
                webhook_exists = True
                break
            else:
                logger.warn("Webhook exists but is NOT active. - Need to delete it.")
                deleted_webhook = await SharedSpark.admin.delete('https://webexapis.com/v1/webhooks/{0}'.format(webhook.get('id')))
    if not webhook_exists:
        data = {"name":"Org Meeting Expeller", "targetUrl":Settings.my_uri,
                "resource": "meetingParticipants", "event": "joined",
                "ownedBy": "org"}
        created_webhook = await SharedSpark.admin.post('https://webexapis.com/v1/webhooks', data)
        SharedSpark.orgId = created_webhook.get('orgId')
        logger.debug("created webhook: {0}".format(created_webhook))
    
async def run_loop():
    while True:
        logger.debug("run_loop - running")
        try:
            token_refresher = TokenRefresher()
            access_token = await token_refresher.refresh_token()
            SharedSpark.admin = Spark(access_token)
            await initial_config()
            logger.debug("SharedSpark.orgId is {0}".format(SharedSpark.orgId))
            now = datetime.utcnow()
            logger.debug("run_loop - utc now:{0}".format(now))
            next_run = now + timedelta(days=1)
            next_run = next_run.replace(hour=7, minute=0, second=0, microsecond=0)
            logger.debug("run_loop - next_run:{0}".format(next_run))
            next_run_seconds = (next_run - now).seconds
        except Exception as e:
            traceback.print_exc()
        logger.debug("run_loop - done. Sleeping for {0} seconds.".format(next_run_seconds))
        await asyncio.sleep(next_run_seconds)


if __name__ == '__main__':
    logger.info("Running on port {0}".format(Settings.port))
    logger.info("Redirect URI:{0}".format(Settings.redirect_uri))
    logger.info("Admin Email:{0}".format(Settings.admin_email))
    logger.info("Expel Domains:{0}".format(Settings.expel_domains))
    app = web.Application()
    app.add_routes([web.get('/alive', is_alive),
                    web.get('/oauth', oauth.get),
                    web.get('/', main_page),
                    web.post('/', main),
                    ])
    loop = asyncio.get_event_loop()
    loop.create_task(run_loop())
    web.run_app(app, loop=loop, port=Settings.port)