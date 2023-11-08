'''
BreadAI: Sleeping Crumbs

Author: Eric Pan

What is this?
    This is a light program to put bots in standby mode,
    a barebone version of a bot with no commands. This 
    program will end when a message is received and will
    send a post request to the locally running Bread API,
    then terminate itself. From there, the Bread API will
    launch a full version of the bots with commands, and
    process the user's message.
'''

import requests
import json
import asyncio
import websockets

class SleepingCrumb(object):
    seq = None

    async def send_heartbeat(self, ws, interval):
        while True:
            await asyncio.sleep(interval / 1000)
            payload = {
                "op": 1,
                "d": self.seq
            }
            await ws.send(json.dumps(payload))

    async def standby_bot(self, token):
        gateway_url = 'wss://gateway.discord.gg/?v=10&encoding=json'

        try:
                async with websockets.connect(gateway_url) as ws:
                    response = await ws.recv()
                    response = json.loads(response)
                    if response["op"] == 10:
                        heartbeat_interval = response["d"]["heartbeat_interval"]
                        asyncio.create_task(self.send_heartbeat(ws, heartbeat_interval))

                    payload = {
                        "op": 2,
                        "d": {
                            "token": token,
                            "properties": {
                                "os": "linux",
                                "browser": "disco",
                                "device": "disco"
                            },
                            "presence": {
                            "activities": [{
                                "name": "Sleeping",
                                "type": 1
                            }],
                            "status": "online",
                            "afk": False
                            },
                            "intents": 3276541
                        }
                    }

                    await ws.send(json.dumps(payload))


                    print("Crumb connected to gateway, watching for activation")
                    while True:
                        response = await ws.recv()
                        response = json.loads(response)
                        if "t" in response:
                            event = response["t"]

                            if event == "MESSAGE_CREATE":
                                if not "bot" in response:
                                    if response["d"]["type"] == 0 or response["d"]["type"] == 14:
                                        channel_id = response["d"]["channel_id"]
                                
                                        await ws.close()
                                    
                            elif event == "INTERACTION_CREATE":
                                ...
                                # todo

                        self.seq = response.get("s", self.seq)
                        
                        if response["op"] == 9:
                            print("Invalid session, reconnecting.")
                            break
        except:
            ...

        print("Activating Crumb...")
        await self.activate("channel", token, channel_id)

    async def activate(self, channeltype, token, channelid):
        if channeltype == "channel":
            e = requests.post(f"https://discord.com/api/v10/channels/{channelid}/messages", headers={
                "accept": "*/*",
                "authorization": "Bot " + token
            },
            json={
                "embeds": [{
                    "title": "Bot is waking up from sleep mode...",
                    "description": "**What's this?**\nAfter 3 days of inactivity, this bot will go into sleep mode to save server resources. The bot will exit sleep mode once it recieves a message or slash command.",
                    "color": 16562691,
                    "footer": {
                        "text": "💡 Protip: Bots usually take 30 seconds to exit sleep mode!"
                    }
                }]
            })

            # make post request to bread API here

    def __init__(self, token):
        self.token = token
        asyncio.get_event_loop().run_until_complete(self.standby_bot(token))

SleepingCrumb("token")
