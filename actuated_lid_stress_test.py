import time
import pprint
import asyncio
import json
import serial

from rcembedded.readcoor.rc_pcb_0011.v1.interface import RcW17Fluidics

async def seal:
    geckos = serial.Serial(gecko_arduino, 9600, timeout=1)
    geckos.write(b'S\n')
    return

async def unseal:
    geckos = serial.Serial(gecko_arduino, 9600, timeout=1)
    geckos.write(b'U\n')
    return

async def home:
    geckos = serial.Serial(gecko_arduino, 9600, timeout=1)
    geckos.write(b'H\n')
    return

async def main():
    fl = RcW17Fluidics("/dev/ttyUSB0")
    file = "/home/rc-eng/Desktop/6psi_post_reassembly_pressure_readout.txt"
    with open(file, 'w') as f:
        f.write("diff pressure, micros, static pressure, temp\n")
        while True:
            new_state = await fl.getState()
            pprint.pprint(new_state)
            time.sleep(5)
            # f.write(json.dumps(new_state))
            f.write(str(new_state.get('diff_pressure')) + ", " + str(new_state.get('micros')) + ", " + str(new_state.get('static_pressure')) + ", " + str(new_state.get('temperature')) + "\n")


asyncio.run(main())
