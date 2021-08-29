import json
from math import ceil, floor
from enum import Enum
import mc_server as s

class minecraft:

    class Facing(Enum):
        east = 0
        south = 1
        west = 2
        north = 3

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
        self.direction = self.__getPlayerFacing(self.config['playerName'])
        self.offset = self.config['blockOffset']
        self.solidBlock = self.config['solidBlock']
        self.progress = self.offset

    __strJoin = lambda self, x: " ".join(map(str, x))

    def __getPlayerFacing(self, name : str) -> Facing:
        res = s.execute(f'data get entity {name} Rotation[0]')
        if 'was found' in res:
            raise Exception(f'{name} is not in the server!')
        else:
            rotation = float(res.split()[-1][:-1])

            if rotation >= -135.0 and rotation < -45.0:
                return self.Facing.east
            elif rotation >= -45.0 and rotation < 45.0:
                return self.Facing.south
            elif rotation >= 45.0 and rotation < 135.0:
                return self.Facing.west
            elif rotation >= 135.0 or rotation < -135.0:
                return self.Facing.north

    def __getPlayerPos(self, name :str) -> list:
        res = [
            s.execute(f'data get entity {name} Pos[0]'),
            s.execute(f'data get entity {name} Pos[1]'),
            s.execute(f'data get entity {name} Pos[2]')
        ]
        result = []
        for i in res:
            if 'was found' in i:
                raise Exception(f'{name} is not in the server!')
            result.append(float(i.split(' ')[-1][:-1]))
        return result

    def __rotate(self, pos :list) -> list:
        anchor = list(map(int, self.pos))
        direction=self.direction
        offsetX = pos[0] - anchor[0]
        offsetZ = pos[2] - anchor[2]

        if direction == self.Facing.south:
            return [anchor[0] - offsetZ, pos[1], anchor[2] + offsetX]
        elif direction == self.Facing.west:
            return [anchor[0] - offsetX, pos[1], anchor[2] - offsetZ]
        elif direction == self.Facing.north:
            return [anchor[0] + offsetZ, pos[1], anchor[2] - offsetX]
        else:
            return pos

    def __direction(self, dFrom :Facing, dTo :Facing) -> Facing:
        return self.Facing((dFrom.value + dTo.value) % 4)

    #Build repeater
    def __repeater(self, pos :list, delay :int, requireFloor=True, isDynamicRepeater=True):
        count = 0
        result = []
        if delay == 0:
            return [], 0

        direction = self.__direction(self.Facing.west, self.direction).name

        if isDynamicRepeater:
            count = delay // 4
            last = delay % 4
            if last != 0:
                count += 1

            if requireFloor:
                result.append(f'fill {self.__strJoin(self.__rotate(pos))} {self.__strJoin(self.__rotate([pos[0] + count - 1, pos[1] + 1, pos[2]]))} {self.solidBlock}')

            if last == 0:
                result.append(f'fill {self.__strJoin(self.__rotate([pos[0], pos[1] + 2, pos[2]]))} {self.__strJoin(self.__rotate([pos[0] + count - 1, pos[1] + 2, pos[2]]))} repeater[facing={direction}, delay=4]')
            elif count == 1:
                result.append(f'setblock {self.__strJoin(self.__rotate([pos[0], pos[1] + 2, pos[2]]))} repeater[facing={direction}, delay={last}]')
            else:
                result.append(f'fill {self.__strJoin(self.__rotate([pos[0], pos[1] + 2, pos[2]]))} {self.__strJoin(self.__rotate([pos[0] + count - 2, pos[1] + 2, pos[2]]))} repeater[facing={direction}, delay=4]')
                result.append(f'setblock {self.__strJoin(self.__rotate([pos[0] + count - 1, pos[1] + 2, pos[2]]))} repeater[facing={direction}, delay={last}]')
        else:
            count = delay * 2 - 1

            if requireFloor:
                result.append(f'fill {self.__strJoin(self.__rotate(pos))} {self.__strJoin(self.__rotate([pos[0] + count - 1, pos[1] + 1, pos[2]]))} {self.solidBlock}')
            for i in range(1, count + 1):
                if i % 2 == 1:
                    result.append(f'setblock {self.__strJoin(self.__rotate([pos[0] + i - 1, pos[1] + 2, pos[2]]))} repeater[facing={direction}, delay=1]')
                else:
                    result.append(f'setblock {self.__strJoin(self.__rotate([pos[0] + i - 1, pos[1] + 2, pos[2]]))} {self.solidBlock}')
                pass

        return result, count

    #Build Noteblock
    def __note(self, pos :list, instBlock: str, pitch: str) -> list:
        if pitch >= 0 and pitch <= 24:
            return [
                f"setblock {self.__strJoin(self.__rotate(pos))} {self.solidBlock}",
                f'setblock {self.__strJoin(self.__rotate([pos[0], pos[1] + 1, pos[2]]))} {instBlock}',
                f'setblock {self.__strJoin(self.__rotate([pos[0], pos[1] + 2, pos[2]]))} minecraft:note_block[note={pitch}]'
                ]
        else:
            return [f"fill {self.__strJoin(self.__rotate(pos))} {self.__strJoin(self.__rotate([pos[0], pos[1] + 2, pos[2]]))} {self.solidBlock}"]

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
            f"fill {self.__strJoin(self.__rotate(pos))} {self.__strJoin(self.__rotate([pos[0], pos[1] + 2, pos[2]]))} {self.solidBlock}",
            f'setblock {self.__strJoin(self.__rotate([pos[0], pos[1] + 3, pos[2]]))} redstone_wire'
        ]

    def __create(self, notes):
        commands = []
        for i in notes:
            dur = i[0]
            if dur != 0:
                pos = [self.pos[0] + self.progress, self.pos[1] + 4 * self.channel, self.pos[2]]
                commands, progress = self.__repeater(pos, dur, isDynamicRepeater=self.config['isDynamicRepeater'])
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
        self.__create(self.notes)
        self.notes = []

        self.isWaiting = True
        self.channel += 1
        self.progress = self.offset

        #TODO: Stop if out of channel index
        if self.channel >= len(self.config['channels']):
            pass
    
    #Finish build
    def finish(self):
        self.__create(self.notes)
        self.notes = []

        length = (self.channel + 1) // 3 + 1
        x = self.pos[0] + self.offset - length - 1
        y = self.pos[1]
        blockY = range(y + (4 * self.channel) + 1, y, -2)
        z = self.pos[2]
        commands = []
        #startblock
        commands.append(f'setblock {self.__strJoin(self.__rotate([x - 1, y, z]))} {self.solidBlock}')
        commands.append(f'setblock {self.__strJoin(self.__rotate([x - 2, y, z]))} {self.config["button"]}[face=wall, facing={self.__direction(self.Facing.west, self.direction).name}]')
        commands.append(f'setblock {self.__strJoin(self.__rotate([x, y, z]))} redstone_wall_torch[facing={self.__direction(self.Facing.east, self.direction).name}]')

        #solidBlock + redstone
        tick = 0
        for i in blockY:
            if i % 4 == blockY[0] % 4:
                commands.append(f'fill {self.__strJoin(self.__rotate([x, i, z]))} {self.__strJoin(self.__rotate([x + length, i, z]))} {self.solidBlock}')
                commands.append(f'fill {self.__strJoin(self.__rotate([x + 1, i + 1, z]))} {self.__strJoin(self.__rotate([x + length, i + 1, z]))} redstone_wire')
                commands += self.__repeater([x + 1, i - 1, z], tick, False)[0]
            else:
                commands.append(f'setblock {self.__strJoin(self.__rotate([x, i, z]))} {self.solidBlock}')
            
            tick += 1

        #redstone_torch
        commands.append(f'fill {self.__strJoin(self.__rotate([x, y + 1, z]))} {self.__strJoin(self.__rotate([x, y + (4 * self.channel) + 2, z]))} minecraft:redstone_torch[lit=false] replace air')

        #gamerule reset
        commands.append('gamerule sendCommandFeedback true')

        for i in commands:
            s.execute(i)

        s.execute('say STOP')

    def build(self, pitch :int, timestamp :int):
        dur = 0
        if self.isWaiting:
            dur += 1
            self.isWaiting = False
            self.previousTime = timestamp
        
        dur += round((timestamp - self.previousTime) / self.config['tickInterval'])
        block = self.config['channels'][self.channel]['block']
        self.previousTime = timestamp

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