from Skype4Py.api import SkypeAPIBase
import logging
import socket
import select
import time
import struct
import threading


class SkypeAPI(SkypeAPIBase):

    def __init__(self, opts):
        self.logger = logging.getLogger('Skype4Py.api.posix_imo.SkypeAPI')
        SkypeAPIBase.__init__(self)
        self.host = opts.pop('host', '0.0.0.0')
        self.port = int(opts.pop('port', '1402'))
        self.logger.info(" Using %s:%d to connect to IMO proxy" % (self.host, self.port))

    def __msg_recv(self, owner):
        while not owner.stop_event.is_set():
            reply_len = struct.unpack('i', self._socket.recv(4))[0]
            reply = self._socket.recv(reply_len)
            self.logger.debug("Received: %s" % reply)
            #if not reply.startswith('#'):
            #self.notifier.notification_received(reply)
#            if reply.startswith(u'#%d ' % command.Id):
#                p = reply.find(u' ')
#                command = self.pop_command(int(reply[1:p]))
#                if command is not None:
#                    command.Reply = reply[p + 1:]
            if reply.startswith(u'#'):
                p = reply.find(u' ')
                command = self.pop_command(int(reply[1:p]))
                if command is not None:
                    command.Reply = reply[p + 1:]
                    if command.Blocking:
                        command._event.set()
                        self.notifier.reply_received(command)
                else:
                    self.notifier.notification_received(reply[p + 1:])
            else:
                self.notifier.notification_received(reply)

    def attach(self, timeout, wait):
        # connect to 127.0.0.1:1401
        self.logger.debug("Connecting...")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setblocking(True)
        try:
            self._socket.connect((self.host, self.port))
        except socket.error:
            pass

        self.logger.debug("Connected")
        self.stop_event = threading.Event()
        self.__msgrecv_thread = threading.Thread(target=self.__msg_recv, args=[self])
        self.__msgrecv_thread.start()

    def send_command(self, command):
        command._event = threading.Event()
        self.push_command(command)
        self.notifier.sending_command(command)
        cmd = '#%d %s' % (command.Id, command.Command)
        cmd_len = struct.pack('i', len(cmd))
        self.logger.debug("Sending command '%s'" % (cmd))
        self._socket.send(cmd_len)
        self._socket.send(cmd)
        self.logger.debug("Sent. Waiting for reply")
        self.reply_received_event = threading.Event()
        command._event.wait(None)
        #self.notifier.notification_received(reply)

        #self.notifier.reply_received("eirgtjhwkoc2llpg eirgtjhwkoc2llpg")
        #self.notifier.notification_received("eirgtjhwkoc2llpg eirgtjhwkoc2llpg")
        #1352893628

    def close(self):
        # close connection
        self.stop_event.set()
        self.logger.debug("Closing connection...")
        self._socket.close()
        self.logger.debug("Disconnected")
