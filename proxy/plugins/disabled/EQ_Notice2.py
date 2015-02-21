# Plugin by Flyergo
# Encoding: utf-8
import plugins
import json
import data
import packetFactory

from twisted.internet import task, reactor
from twisted.python import log
from twisted.web.client import readBody
from twisted.web.http_headers import Headers
from commands import Command

debug = 0
url = 'http://pso2emq.flyergo.eu/emergencyQuest_v2.php'
interval = 60
oldtext = ''

def logdebug(message):
    if debug:
        print "[EQ_Notice2-Debug] %s" % message

try:
    from twisted.web.client import Agent, HTTPConnectionPool
    pool = HTTPConnectionPool(reactor)
    pool._factory.noisy = False
    agent = Agent(reactor, pool=pool)
except ImportError:
    from twisted.web.client import Agent
    agent = Agent(reactor)

def LookupForEQ():
    header = Headers({'User-Agent': ['PSO2Proxy']})
    EQ0 = agent.request('GET', url, header)
    EQ0.addCallback(EQResponse)
    EQ0.addErrback(log.err)

def EQResponse(response):
    if response.code != 200:
        logdebug("Invalid response code: {0}", response.code)
        return
    d = readBody(response)
    d.addCallback(EQNotice)

def EQNotice(value):
    try:
        obj = json.loads(value)
    except Exception:
        return
    text = obj[0]["text"]
    global oldtext
    if(oldtext != text):
        sysmessage = packetFactory.SystemMessagePacket("The upcoming Emergency Quests info has been updated!\nEnter !checkeq to redisplay upcoming Emergency Quests!", 0x0).build()
        message = packetFactory.SystemMessagePacket("{yel}%s" % text, 0x3).build()
        oldtext = text
        for client in data.clients.connectedClients.values():
            try:
                chandle = client.get_handle()
                if chandle is not None:
                    chandle.send_crypto_packet(sysmessage)
                    chandle.send_crypto_packet(message)
            except AttributeError:
                logdebug("Dead client ... skipping")

@plugins.on_start_hook
def on_start():
    global taskrun
    taskrun = task.LoopingCall(LookupForEQ)
    taskrun.start(interval)

@plugins.CommandHook("checkeq", "Redisplay of upcoming Emergency Quests")
class RedisplayEQs(Command):
    def call_from_client(self, client):
        message = packetFactory.SystemMessagePacket("{yel}%s" % oldtext, 0x3).build()
        client.send_crypto_packet(message)
    def call_from_console(self):
        return
