import asyncio
import time
from loguru import logger
from loguru import logger as LOG
import os
import sys
import json
import argus.config
from rcembedded.txg.pmc.hw_revXX.interface import PMC
from rcembedded.readcoor.rc_pcb_fgc.cs1.interface import FGC
import numpy as np
# from rcembedded.oem.maestro.v7.interface import RcMaestro
# from argus.config.instrument_models.cs1.cs1_wrapper import CS1_Wrapper


async def adp_test():
    time_str = time.strftime("%Y%m%d_%H%M%S")
    LOG.remove(0)
    LOG.add(sys.stderr)
    LOG.add("{}_output_0002.log".format(time_str))
    fgc = FGC()
    await fgc.reset()
    await fgc.init()
    await fgc.home_adp()
    # await fgc.home_sipper()
    # await fgc.home_gantry()
    await fgc.initialize_adp(linResolution_nmpS=31800)
    # await fgc.set_gantry_x_position(400000000)
    cycles = 11000 #Number of decoding cycles over 7 years
    exchange_cycle = [110, 50, 20, 90] # Corresponds to tip pickup, reagent pickup, dispense, tip eject
    exchange_cycles_per_cycle = 7 # Simplified version of liquid handling cycle
    check_cycles = 15 #Check once per simulated run
 
    with open ("{}_adp_stress_test_0002.txt".format(time_str), 'w') as f:
        f.write("time, cycle, exchange_cycles, z_pos_nm\n")
        for cycle in range(cycles):
            for exchange_cycles in range(exchange_cycles_per_cycle):
                for position in exchange_cycle:
                    tries = 3
                    for i in range(tries):
                        try:
                            LOG.info("cycle {} of {}, exchange {}, position {}".format(cycle+1, cycles, exchange_cycles, position))
                            await fgc.set_adp_position(position * 1000000, speed_nmps=100000000)
                            await asyncio.sleep(0.1)
                            new_line = "{}, {}, {}, {}\n".format(time.time(), cycle, exchange_cycles, position)
                            f.writelines(new_line)

                            position = 0
                            await fgc.set_adp_position(position, speed_nmps=100000000)
                            await asyncio.sleep(0.1)
                            new_line = "{}, {}, {}, {}\n".format(time.time(), cycle, exchange_cycles, position)
                            f.writelines(new_line)
                        except Exception as error:
                            LOG.critical(error)
                            if i < tries - 1:
                                LOG.warning("reseting and retrying")
                                await reset_fgc()
                                continue
                            else:
                                LOG.error("Failed after {} cycles".format(cycle))
                                raise
                        break
            if (cycle%check_cycles == 0):
                await check_connectivity(cycle)
                await fgc.home_adp()
        await fgc.home_sipper()
        return 

async def reset_fgc():
    pmc=PMC()
    fgc = FGC()
    await pmc.reset()
    await fgc.reset()
    await fgc.init()
    await fgc.home_adp()
    await fgc.initialize_adp(linResolution_nmpS=31800)
    return

async def check_connectivity(cycle):
    steps = np.arange(0, 110000000, 500000)
    await adp_cycle(cycle, steps)

    steps = np.flip(np.arange(250000, 110000000-250000, 500000))
    await adp_cycle(cycle, steps)

    return

async def adp_cycle(cycle, steps):
    fgc = FGC()
    LOG.info("Checking connectivity")
    plunger_positions = [100, 110]

    for i, step in enumerate(steps):    
        tries = 3
        fails = 0
        for j in range(tries):
            try:
                LOG.info("step {}, plunger position {}".format(step, plunger_positions[i%2]))
                await fgc.set_adp_position(step)
                await fgc.adp_absolute_position(200, plunger_positions[i%2], 0)
            except Exception as error:
                LOG.critical(error)
                if j < tries - 1:
                    LOG.warning("retrying {} more times".format(tries - j - 1))
                    await reset_fgc()
                    continue
                else:
                    LOG.error("Failed after {} cycles".format(cycle))
                    raise
            break
    return


@LOG.catch
async def main():
    await adp_test()
    return

if __name__ == "__main__":
    asyncio.run(main())
