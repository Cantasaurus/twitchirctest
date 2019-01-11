import socket
import sys
import os
import multiprocessing
import curses 
import regex

#TODO use nonblocking sockets or just asyncio. Make it so you can type in chat. Make chat look like actual twitch chat 

class TwitchIRCReader:
    HOST = "irc.chat.twitch.tv"
    PORT = 6667
    #Should be large enough
    MAX_RECV = 2048

    def __init__(self, nick, channel, oauth=None):
        self.socket = self.socket_connect(self.HOST, self.PORT)
        self.nick = nick
        self.oauth = oauth
        self.channel = channel
        self.listen = True
        self._connected = False
        self._authenticated = False

    def socket_connect(self, host, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            s.settimeout(10)
        except:
            print("Twitch irc chat connection was unsuccessful!")
            sys.exit(0)    
        print("Connection successfully established with {}".format(self.HOST + ":" + str(self.PORT)))    
        return s

    def socket_close(self):
        self.socket.close()

    def PART(self):
        try:
            self.socket.send("PART #{}\r\n".format(self.channel).encode("utf8"))
        except:
            print("There was an error trying to leave {}'s channel.".format(self.channel))
            sys.exit(0)
        self.channel = None    

    def JOIN(self):
        try:
            self.socket.send("JOIN #{}\r\n".format(self.channel).encode("utf-8"))
        except:
            print("There was an error trying to join {}'s channel".format(self.channel))
            sys.exit(0) 

    def NICK(self):
        try:
            self.socket.send("NICK {}\r\n".format(self.nick).encode("utf-8"))
        except:
            print("There was an error trying to announce your nickname.")
            sys.exit(0)    

    def PASS(self):
        try:
            self.socket.send("PASS {}\r\n".format(self.oauth).encode("utf-8"))
        except:
            print("There was an error trying to announce your nickname.")
            sys.exit(0)       

    def run(self):
        #Send password, nickname, and then join a channel
        self.PASS()
        self.NICK()
        self.JOIN()
        while self.listen:
            try:
                resp = self.socket.recv(self.MAX_RECV).decode("utf-8")
                print(resp) 
                if resp == "PING :tmi.twitch.tv\r\n":
                    self.socket.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                if "End of /NAMES list" in resp:
                    self._connected = True
                    print("Successfully connected to the channel! Enjoy :)")
            except IOError:
                print("....")
                continue        
            except KeyboardInterrupt:
                print("Bye bye!")
                self.socket_close()
                sys.exit(0)

    @property
    def authenticated(self):
        return self._authenticated

    @property
    def connected(self):
        return self._connected          


def main():
    if len(sys.argv) < 4:
        print("You didn't provide all the required parameters.")
        sys.exit(0)
    irc = TwitchIRCReader(sys.argv[1], sys.argv[2], sys.argv[3]) 
    irc.run()

if __name__ == "__main__":
    main()    