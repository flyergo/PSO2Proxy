# Plugin by Flyergo
# Encoding: utf-8
# Requires pytz
import plugins
import packetFactory

from commands import Command
from datetime import datetime
from pytz import timezone

timezone_utc = timezone('UTC')
timezone_jst = timezone('Asia/Tokyo')

@plugins.CommandHook("time", "Displays the current japanese standard time (JST).")
class ShowJstTime(Command):
    def call_from_client(self, client):
        now_utc = datetime.now(timezone_utc)
        now = now_utc.astimezone(timezone_jst)
        message = packetFactory.SystemMessagePacket("It's currently %s in Japan." % now.strftime('%H:%M:%S'), 0x3).build()
        client.send_crypto_packet(message)

    def call_from_console(self):
        now_utc = datetime.now(timezone_utc)
        now = now_utc.astimezone(timezone_jst)
        print "It's currently %s in Japan." % now.strftime('%H:%M:%S')
        return

