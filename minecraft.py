import json
from math import ceil, floor
import mc_server as s

class minecraft:
    def __init__(self):
        #minecraft noteblock info
        fjson = open('mc_config.json', 'r')
        self.config = json.load(fjson)
        fjson.close()

        self.isWaiting = True
        self.previousTime = 0
        self.channel = 0
        self.notes = []
        self.pos = list(map(floor, self.__getPlayerPos(self.config['playerName'])))
        self.offset = self.config['blockOffset']
        self.solidBlock = self.config['solidBlock']
        self.progress = self.offset

    def __getPlayerPos(self, name :str) -> list:
        res = [
            s.execute(f'data get entity {name} Pos[0]'),
            s.execute(f'data get entity {name} Pos[1]'),
            s.execute(f'data get entity {name} Pos[2]')
        ]
        result = []
        for i in res:
            result.append(float(i.split(' ')[-1][:-1]))
        return result

    #Build repeater
    def __repeater(self, pos :list, delay :int, requireFloor=True):
        if delay == 0:
            return [], 0

        count = delay // 4
        last = delay % 4
        if last != 0:
            count += 1

        result = []
        if requireFloor:
            result.append(f'fill {pos[0]} {pos[1]} {pos[2]} {pos[0] + count - 1} {pos[1] + 1} {pos[2]} {self.solidBlock}')

        if last == 0:
            result.append(f'fill {pos[0]} {pos[1] + 2} {pos[2]} {pos[0] + count - 1} {pos[1] + 2} {pos[2]} repeater[facing=west, delay=4]')
        elif count == 1:
            result.append(f'setblock {pos[0]} {pos[1] + 2} {pos[2]} repeater[facing=west, delay={last}]')
        else:
            result.append(f'fill {pos[0]} {pos[1] + 2} {pos[2]} {pos[0] + count - 2} {pos[1] + 2} {pos[2]} repeater[facing=west, delay=4]')
            result.append(f'setblock {pos[0] + count - 1} {pos[1] + 2} {pos[2]} repeater[facing=west, delay={last}]')

        return result, count

    #Build Noteblock
    def __note(self, pos :list, instBlock: str, pitch: str) -> list:
        return [
            f"setblock {' '.join(map(str, pos))} {self.solidBlock}",
            f'setblock {pos[0]} {pos[1] + 1} {pos[2]} {instBlock}',
            f'setblock {pos[0]} {pos[1] + 2} {pos[2]} minecraft:note_block[note={pitch}]'
            ]

    #Calculate where noteblock will be placed
    def __calcPos(self, count :int) ->list:
        calc = lambda x, c: [[x, i + 1] for i in range(ceil(c / 2))] + [[x, -i - 1] for i in range(floor(c / 2))]
        result = []
        if count <= 3:
            result += calc(0, count - 1)
            result += [[0, 0]]
        else:
            result += calc(1, count)

        return result
    
    def __redstone(self, pos :list) ->list:
        return [
            f"fill {' '.join(map(str, pos))} {pos[0]} {pos[1] + 2} {pos[2]} {self.solidBlock}",
            f'setblock {pos[0]} {pos[1] + 3} {pos[2]} redstone_wire'
        ]

    def __create(self, notes):
        for i in notes:
            dur = i[0]
            if dur != 0:
                pos = [self.pos[0] + self.progress, self.pos[1] + 4 * self.channel, self.pos[2]]
                commands, progress = self.__repeater(pos, dur)
                self.progress += progress
                break

        pos = [self.pos[0] + self.progress, self.pos[1] + 4 * self.channel, self.pos[2]]
        offsets = self.__calcPos(len(notes))

        k = 0
        for i in offsets:
            commands += self.__note([pos[0] + i[0], pos[1], pos[2] + i[1]], notes[k][1], notes[k][2])
            k += 1

        if len(notes) >= 4:
            offsets.append([0, 0])
            for i in offsets:
                commands += self.__redstone([pos[0], pos[1], pos[2] + i[1]])
        self.progress += 1

        for i in commands:
            s.execute(i)

    #Change to next channel/instrument
    def next(self):
        self.isWaiting = True
        self.channel += 1
        self.progress = self.offset

        #TODO: Stop if out of channel index
        if self.channel >= len(self.config['channels']):
            pass
    
    #TODO: Finish build
    def finish(self):
        s.execute('say STOP')

        length = (self.channel + 1) // 3 + 1
        x = self.pos[0] + self.offset - length - 1
        y = self.pos[1]
        blockY = range(y + (4 * self.channel) + 1, y, -2)
        z = self.pos[2]
        commands = []

        #startblock
        commands.append(f'setblock {x - 1} {y} {z} {self.solidBlock}')
        commands.append(f'setblock {x - 2} {y} {z} {self.config["button"]}[face=wall, facing=west]')
        commands.append(f'setblock {x} {y} {z} redstone_wall_torch[facing=east]')

        #solidBlock + redstone
        tick = 0
        for i in blockY:
            if i % 4 == blockY[0] % 4:
                commands.append(f'fill {x} {i} {z} {x + length} {i} {z} {self.solidBlock}')
                commands.append(f'fill {x + 1} {i + 1} {z} {x + length} {i + 1} {z} redstone_wire')
                commands += self.__repeater([x + 1, i - 1, z], tick, False)[0]
            else:
                commands.append(f'setblock {x} {i} {z} {self.solidBlock}')
            
            tick += 1

        #redstone_torch
        commands.append(f'fill {x} {y + 1} {z} {x} {y + (4 * self.channel) + 2} {z} minecraft:redstone_torch replace air')

        for i in commands:
            s.execute(i)

    def build(self, pitch :int, timestamp :int):
        dur = 0
        if self.isWaiting:
            dur += 1
            self.isWaiting = False
            self.previousTime = timestamp

        dur += round((timestamp - self.previousTime) / self.config['tickInterval'])
        block = self.config['channels'][self.channel]['block']
        self.previousTime = timestamp

        if pitch < 0:
            self.__create(self.notes)
            self.notes = []
            return

        #same time
        if dur == 0:
            self.notes.append([dur, block, pitch])
        else:
            if self.notes:
                self.__create(self.notes)
                self.notes = []
                self.notes.append([dur, block, pitch])
            else:
                self.notes.append([dur, block, pitch])