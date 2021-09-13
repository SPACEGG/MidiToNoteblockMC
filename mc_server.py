import json
from rcon import Client as rc

#minecraft rcon server info
fjson = open('server_config.json', 'r')
config = json.load(fjson)
fjson.close()

server = rc(config['host'], config['port'])
server.connect()
server.login(config['password'])

def execute(text):
    r = server.run(text)
    print(r)
    return r

execute('gamerule sendCommandFeedback false')