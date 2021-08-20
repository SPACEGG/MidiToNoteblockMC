#START ME
import json
import sys
import asyncio
import midi_input as midi
from minecraft import minecraft
import mc_server

#resolve asyncio warning for Windows
if __name__ == '__main__':
  py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
  if py_ver > 37 and sys.platform.startswith('win'):
  	asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

fjson = open('midi_config.json', 'r')
config = json.load(fjson)
fjson.close()

mc = minecraft()

def test(e):
    asyncio.run(mc_server.execute(f'say key:{e.data1}'))

def switch(e):
    key = e.data1

    if key == config['nextKey']:
        mc.next()
    elif key == config['stopKey']:
        mc.finish()
    else:
        mc.build(key - config['minKey'], e.timestamp)
        
midi.input_main(config['deviceID'], switch)