import sys
import asyncio
import json
from rcon import rcon

#resolve asyncio warning for Windows
if __name__ == '__main__':
  py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
  if py_ver > 37 and sys.platform.startswith('win'):
  	asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

#minecraft rcon server info
fjson = open('server_config.json', 'r')
config = json.load(fjson)
fjson.close()

async def main(text):
    return await rcon(text, host=config['host'], port=config['port'], passwd=config['passward'])

# res = asyncio.run(main('execute as @a at @s run playsound minecraft:block.note_block.pling master @s ~ ~ ~'))
res = asyncio.run(main('scoreboard players get x dummy'))

print(res)
