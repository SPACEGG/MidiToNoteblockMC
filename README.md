# 🎹 MidiToNoteblockMC
Build minecraft noteblock music using MIDI keyboard

## How to use

### Requirements
* Python 3.8 or higher
* MIDI device input
* Your own Minecraft server (JE 1.17+ recommended)

### Setup
```
> pip install -r requirements.txt
```

### Start
- Complete configurations first
```
> python3 start.py
```
---
## Configurations
- MIDI config (midi_config.json)

    #### `deviceID`
    Set MIDI device id. To find MIDI id list:
    ```
    > python3 start.py -ls
    ```

- Server config (server_config.json)

    #### `host`
    Minecraft server address
    #### `port`
    RCON port from server.properties
    #### `password`
    RCON password from server.properties

- Minecraft config (mc_config.json)

    #### `playerName`
    Player Name or UUID
    #### `solidBlock`
    Main block (Should be solid, not affected by gravity)
    #### `button`
    Start Button
    #### `blockOffset`
    Distance from the player
    #### `isDynamicRepeater`
    Use minimal repeaters
    #### `channels`
    Noteblock instruments setting
    #### `tickInterval`
    1 repeater tick in ms
