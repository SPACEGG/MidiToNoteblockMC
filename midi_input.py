import pygame as pg
import pygame.midi as midi
import json

fjson = open('midi_config.json', 'r')
config = json.load(fjson)
fjson.close()

# code from pygame Example (python -m pygame.examples.midi --input)
def print_device_info():
    for i in range(midi.get_count()):
        r = midi.get_device_info(i)
        (interf, name, input, output, opened) = r

        in_out = ""
        if input:
            in_out = "(input)"
        if output:
            in_out = "(output)"

        print(
            "%2i: interface :%s:, name :%s:, opened :%s:  %s"
            % (i, interf, name, opened, in_out)
        )

def input_main(device_id=None, *callbacks):
    pg.init()
    pg.fastevent.init()
    event_get = pg.fastevent.get
    event_post = pg.fastevent.post

    midi.init()

    # print_device_info()

    if device_id is None:
        input_id = midi.get_default_input_id()
    else:
        input_id = device_id

    print("using input_id :%s:" % input_id)
    i = midi.Input(input_id)

    pg.display.set_mode((1, 1))

    going = True
    while going:
        events = event_get()
        for e in events:
            if e.type in [pg.QUIT]:
                going = False
            if e.type in [midi.MIDIIN]:
                midiEvent(e, callbacks)
                
                #stop
                if e.data1 == config['stopKey']:
                    going = False

        if i.poll():
            midi_events = i.read(10)
            # convert them into pygame events.
            midi_evs = midi.midis2events(midi_events, i.device_id)

            for m_e in midi_evs:
                event_post(m_e)

    del i
    midi.quit()

def midiEvent(e, callbacks):
    channel = e.status - config['firstChannel'] + 1
    if channel > 0:
        # print(f'Channel:{channel}, Key: {e.data1}, Timestamp: {e.timestamp}')
        for i in callbacks:
            i(e)

# input_main(config['deviceID'])