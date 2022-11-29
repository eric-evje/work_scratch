import asyncio
import time
import loguru; LOG = loguru.logger
import os
import json
import argus.config
from rcembedded.readcoor.rc_pcb_fgc.cs1.interface import FGC
import numpy as np
# from rcembedded.oem.maestro.v7.interface import RcMaestro
# from argus.config.instrument_models.cs1.cs1_wrapper import CS1_Wrapper



async def adp_test():
    fgc = FGC()

    await fgc.home_adp()
    # await fgc.home_sipper()
    # await fgc.home_gantry()
    # await fgc.initialize_adp(linResolution_nmpS=31800)
    # await fgc.set_gantry_x_position(400000000)
    cycles = 50000
    check_cycles = 1000
    with open ("{}_adp_stress_test.txt".format(time.strftime("%Y%m%d_%H%M%S")), 'w') as f:
        f.write("time, cycle, z_pos_nm\n")
        for cycle in range(cycles):
            print("cycle {} of {}".format(cycle+1, cycles), end='\r')
            position = 110000000
            await fgc.set_adp_position(position)
            await asyncio.sleep(0.1)
            new_line = "{}, {}, {}\n".format(time.time(), cycle, position)
            f.writelines(new_line)

            position = 0
            await fgc.set_adp_position(position)
            await asyncio.sleep(0.1)
            new_line = "{}, {}, {}\n".format(time.time(), cycle, position)
            f.writelines(new_line)

            if (cycle%check_cycles == 0):
                await check_connectivity(cycle)

        await fgc.home_sipper()
        return

async def check_connectivity(cycle):
    fgc = FGC()
    plunger_positions = [100, 110]

    steps = np.arange(0, 110000000, 500000)
    for i, step in enumerate(steps):
        await fgc.set_adp_position(step)
        try:
            await fgc.adp_absolute_position(200, plunger_positions[i%2], 0)
        except Exception as error:
            print(error)
            print("Failed after {} cycles".format(cycle))
            raise

    steps = np.flip(np.arange(0, 110000000-250000, 500000))
    for i, step in enumerate(steps):
        await fgc.set_adp_position(step)
        try:
            await fgc.adp_absolute_position(200, plunger_positions[i%2], 0)
        except Exception as error:
            print(error)
            print("Failed after {} cycles".format(cycle))
            raise

    return
        


async def main():
    await adp_test()
    return

if __name__ == "__main__":
    asyncio.run(main())