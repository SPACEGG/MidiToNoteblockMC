#START ME
import json
import midi_input as midi
from minecraft import minecraft

fjson = open('midi_config.json', 'r')
config = json.load(fjson)
fjson.close()

mc = minecraft()

def switch(e):
    key = e.data1

    if key == config['nextKey']:
        mc.build(-1, e.timestamp)
        mc.next()
    elif key == config['stopKey']:
        mc.build(-1, e.timestamp)
        mc.finish()
    else:
        mc.build(key - config['minKey'], e.timestamp)
        
midi.input_main(config['deviceID'], switch)