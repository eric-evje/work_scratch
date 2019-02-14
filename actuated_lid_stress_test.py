import time
import pprint
import asyncio
import json
import serial

from rcembedded.readcoor.rc_pcb_0011.v1.interface import RcW17Fluidics

class gecko_drives():
    def init(gecko_arduino):
        self.geckos = serial.Serial(gecko_arduino, 9600, timeout=1)

    async def seal():
        self.geckos.write(b'S\n')
        time.sleep(10)
        return

    async def unseal():
        self.geckos.write(b'U\n')
        time.sleep(10)
        return

    async def home():
        self.geckos.write(b'H\n')
        time.sleep(10)
        return

    async def reset():
        self.geckos.write(b'R\n')
        time.sleep(1)
        return

async def pressurize(gecko_arduino, flu_unit):
    fl = RcW17Fluidics(flu_unit)
    home(gecko_arduino)
    seal(gecko_arduino)
    fl.initPneumaticValve(1)
    return()

async def depressurize(gecko_arduino, flu_unit):
    fl = RcW17Fluidics(flu_unit)
    home(gecko_arduino)
    seal(gecko_arduino)
    fl.endPneumaticValve(1)
    return()

async def main():

    parser = argparse.ArgumentParser(
        description='This script assists in the Calibration of the '
                    'fluidic unit differential pressure sensor. This sensor '
                    'acts as a volumetric mass flow sensor with proper '
                    'Calibration. '
    parser.add_argument('file_name', type=str,
                        help='Filename to save Calibration data.')
    parser.add_argument('f', '--fluidics_unit_board_ser', dest='fluidics_unit_board_ser', default='/dev/ttyUSB0', type=str,
                        help='Serial port of the fluidics unit control board.')
    parser.add_argument('-g', '--gecko_arduino', dest='gecko_arduino', default='/dev/ttyUSB1', type=str,
                        help='Serial port of the arduino.')
    )
    args = parser.parse_args()

    file = args.file_name
    fl = RcW17Fluidics(args.fluidics_unit_board_ser)
    ge = gecko_arduino(args.gecko_arduino)

    ge.reset()

    with open(file, 'x') as f:
        f.write("cycle, diff pressure, micros, static pressure, temp\n")
        for i in range(1, 100):
            ge.home()
            ge.seal()
            await fl.initPneumaticValve(1)

            time_start = time.now()
            while (time.now - time_start < 300):
                new_state = await fl.getState()
                pprint.pprint(new_state)
                time.sleep(5)
                # f.write(json.dumps(new_state))
                f.write(i + ", " + str(new_state.get('diff_pressure')) + ", " + time.now() + ", " + str(new_state.get('static_pressure')) + ", " + str(new_state.get('temperature')) + "\n")

            await fl.endPneumaticValve(1)
            ge.unseal()


asyncio.run(main())
