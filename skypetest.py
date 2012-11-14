import Skype4Py
import logging
import sys
import time

def setupLogger():
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger('Skype4Py')
    log.setLevel(logging.ERROR)
    log = logging.getLogger('Skype4Py.api.posix_imo.SkypeAPI')
    log.setLevel(logging.DEBUG)

class EventHandler:

    def MessageStatus(self, msg, status):
        if status == Skype4Py.cmsReceived:
            #text = msg.Body
            print "Message: %s" % msg
            #if text == "!test":
            #    msg.Chat.SendMessage("test passed")

if __name__ == '__main__':
    setupLogger()

    arguments = {}
    if len(sys.argv) == 3:
        arguments['host'] = sys.argv[0]
        arguments['port'] = sys.argv[1]

    skype = Skype4Py.Skype(Events=EventHandler(), Transport="imo", **arguments)
    skype.Attach()

    #skype.SendMessage("easysly", "from imo")
    skype.ChangeUserStatus('AWAY')

    while True:
        time.sleep(0.5)
