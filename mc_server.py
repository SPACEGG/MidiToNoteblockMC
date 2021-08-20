import sys
import asyncio
import json
from rcon import rcon

#minecraft rcon server info
fjson = open('server_config.json', 'r')
config = json.load(fjson)
fjson.close()

async def execute(text):
    return await rcon(text, host=config['host'], port=config['port'], passwd=config['passward'])

# res = asyncio.run(execute('scoreboard players get x dummy'))
# print(res)
