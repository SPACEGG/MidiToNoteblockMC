import json
import asyncio
from math import floor
import mc_server

class minecraft:
    def __init__(self):
        #minecraft noteblock info
        fjson = open('mc_config.json', 'r')
        self.config = json.load(fjson)
        fjson.close()

        self.isWaiting = True
        self.previousTime = 0
        self.channel = 0
        self.sync = 0
        self.initPos = list(map(floor, self.__getPlayerPos(self.config['playerName'])))
        self.initProgress = 2
        self.mainBlock = self.config['mainBlock']
        self.progress = self.initProgress

    def __getPlayerPos(self, name :str) -> list:
        res = [
            asyncio.run(mc_server.execute(f'data get entity {name} Pos[0]')),
            asyncio.run(mc_server.execute(f'data get entity {name} Pos[1]')),
            asyncio.run(mc_server.execute(f'data get entity {name} Pos[2]'))
        ]
        result = []
        for i in res:
            result.append(float(i.split(' ')[-1][:-1]))
        return result

    #Build repeater
    def __repeater(self, delay :int) -> list:
        x = self.initPos[0] + self.progress
        y = self.initPos[1]
        z = self.initPos[2]
        if delay == 0:
            return []

        count = delay // 4
        last = delay % 4
        if last != 0:
            count += 1

        result = []
        result.append(f'fill {x} {y} {z} {x + count - 1} {y + 1} {z} {self.mainBlock}')
        if last == 0:
            result.append(f'fill {x} {y + 2} {z} {x + count - 1} {y + 2} {z} repeater[facing=west, delay=4]')
        elif count == 1:
            result.append(f'setblock {x} {y + 2} {z} repeater[facing=west, delay={last}]')
        else:
            result.append(f'fill {x} {y + 2} {z} {x + count - 2} {y + 2} {z} repeater[facing=west, delay=4]')
            result.append(f'setblock {x + count - 1} {y + 2} {z} repeater[facing=west, delay={last}]')


        self.progress += count
        return result

    #Build Noteblock
    def __note(self, instBlock: str, pitch: str) -> list:
        x = self.initPos[0] + self.progress
        y = self.initPos[1]
        z = self.initPos[2]

        self.progress += 1
        return [
            f'setblock {x} {y} {z} {self.mainBlock}',
            f'setblock {x} {y + 1} {z} {instBlock}',
            f'setblock {x} {y + 2} {z} minecraft:note_block[note={pitch}]'
            ]

    #Change to next channel/instrument
    def next(self):
        self.isWaiting = True
        self.channel += 1
        self.progress = self.initProgress

        #TODO: Stop if out of channel index
        if self.channel >= len(self.config['channels']):
            pass
        
        x = 'hihihihiihi'
        asyncio.run(mc_server.execute(f'say {x}'))
    
    #TODO: Finish build
    def finish(self):
        asyncio.run(mc_server.execute('say Stop'))

    #TODO: Build noteblock circuit
    def build(self, key :int, timestamp :int):
        if self.isWaiting:
            self.isWaiting = False
            self.previousTime = timestamp

        dur = round((timestamp - self.previousTime) / self.config['tickInterval'])
        block = self.config['channels'][self.channel]['block']
        self.previousTime = timestamp

        #same time
        if dur == 0:
            self.sync += 1
        else:
            self.sync = 0

        commands = self.__repeater(dur) + self.__note(block, key)

        for i in commands:
            asyncio.run(mc_server.execute(i))
