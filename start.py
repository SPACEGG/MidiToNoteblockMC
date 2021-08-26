#START ME
import json
import sys
import midi_input as midi
from minecraft import minecraft

fjson = open('midi_config.json', 'r')
config = json.load(fjson)
fjson.close()


def switch(e):
    key = e.data1
    mc = minecraft()

    if key == config['nextKey']:
        mc.next()
    elif key == config['stopKey']:
        mc.finish()
    else:
        mc.build(key - config['minKey'], e.timestamp)

def arg(a):
    if a in ['-ls', '--list']:
        midi.print_device_info()
    return False

def main(argv):
    a = arg(argv[-1])
    if a:
        midi.input_main(config['deviceID'], switch)

if __name__ == "__main__":
    main(sys.argv)