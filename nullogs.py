import discord
from configobj import ConfigObj
import logging
import os
import asyncio

# pid = os.getpid()
# op = open("/var/run/steven.pid", "w")
# op.write("%s" % pid)
# op.close()
#

my_logger = logging.getLogger(__name__)
my_logger.setLevel(logging.INFO)

#
# # create a file handler
# handler = logging.FileHandler('/var/log/steven.log')
# handler.setLevel(logging.INFO)
#
# # create a logging format
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
#
# # add the handlers to the logger
# logger.addHandler(handler)

#if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    #discord.opus.load_opus('opus')
    #discord.opus.load_opus('/usr/lib/x86_64-linux-gnu/libopus.so.0')


class Nullogs(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = kwargs['config']
        self.text_channel = None

    async def on_ready(self):
        my_logger.warning('Logged in as %s/%s' % (self.user.name, self.user.id))
        for g in self.guilds:
            for c in g.text_channels:
                if c.name == self.config["log_channel"]:
                    self.text_channel = c
                    break

    async def on_voice_state_update(self, member, before, after):
        msg = []
        srv = []
        if before.deaf and not after.deaf:
            srv.append("undeafended")
        if not before.mute and after.mute:
            srv.append("unmuted")
        if len(srv) == 1:
            msg.append(srv[0] + " by the server")
        elif len(srv) > 1:
            msg.append(' and '.join(srv) + " by the server")

        slf = []
        if before.self_deaf and not after.self_deaf:
            slf.append("undeafended")
        if not before.self_mute and after.self_mute:
            slf.append("deafended")
        if len(slf) == 1:
            msg.append(slf[0] + " themselves")
        elif len(slf) > 0:
            msg.append(' and '.join(slf) + " themselves")

        if before.channel is None and after.channel is not None:
            msg.append('joined the server in #' + after.channel.name)
        elif before.channel is not None and after.channel is None:
            msg.append('disconnected from #' + before.channel.name)
        elif before.channel is not None and after.channel is not None:
            if before.channel.name != after.channel.name:
                msg.append('switched from #' + before.channel.name + ' #' + after.channel.name)

        if self.text_channel is not None:
            if len(msg) > 0:
                if len(msg) == 1:
                    message = msg[0]
                elif len(msg) > 1:
                    message = ' and '.join([", ".join(msg[:-1]), msg[-1]])
                send_str = member.display_name + ' ' + message
                my_logger.warning(send_str)
                self.text_channel.send(send_str)


config = ConfigObj(".env")
client = Nullogs(config=config)
client.run(config['token'])
