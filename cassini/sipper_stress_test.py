import asyncio
import time
import loguru; LOG = loguru.logger
import os
import json
import argus.config
from rcembedded.readcoor.rc_pcb_fgc.cs1.interface import FGC
# from rcembedded.oem.maestro.v7.interface import RcMaestro
# from argus.config.instrument_models.cs1.cs1_wrapper import CS1_Wrapper



async def sipper_test():
    fgc = FGC()
    # input("Press ENTER to begin Extract axis stress test ... ")
    # print("Beginning test: Check for audible resonance of motor during travel")
    await fgc.home_sipper()
    cycles = 20000
    with open ("{}_sipper_stress_test.txt".format(time.strftime("%Y%m%d_%H%M%S")), 'w') as f:
        f.write("time, z_pos_nm\n")
        for cycle in range(cycles):
            print("cycle {} of {}".format(cycle+1, cycles), end='\r')
            position = 8000000
            await fgc.set_sipper_position(position, acceleration_nmps = 15000000, speed_nmps = 18000000, deceleration_nmps=15000000)
            await asyncio.sleep(0.1)
            state = await fgc.get_state()
            # z_pos_nm = state['tele']['MotionAxisTelemetry_SipperZ']['position_nm']
            new_line = "{}, {}\n".format(time.time(), position)
            f.writelines(new_line)

            position = 30000000
            await fgc.set_sipper_position(position, acceleration_nmps = 15000000, speed_nmps = 18000000, deceleration_nmps=15000000)
            await asyncio.sleep(0.1)
            z_pos_nm = state['tele']['MotionAxisTelemetry_SipperZ']['position_nm']
            new_line = "{}, {}\n".format(time.time(), position)
            f.writelines(new_line)

            position = 0
            await fgc.set_sipper_position(position, acceleration_nmps = 15000000, speed_nmps = 18000000, deceleration_nmps=15000000)
            await asyncio.sleep(0.1)
            z_pos_nm = state['tele']['MotionAxisTelemetry_SipperZ']['position_nm']
            new_line = "{}, {}\n".format(time.time(), position)
            f.writelines(new_line)

            if (cycle%50 == 0):
                position = 50000000
                await fgc.set_sipper_position(position, acceleration_nmps = 15000000, speed_nmps = 18000000, deceleration_nmps=15000000)
                await asyncio.sleep(0.1)
                # z_pos_nm = state['tele']['MotionAxisTelemetry_SipperZ']['position_nm']
                new_line = "{}, {}\n".format(time.time(), position)
                f.writelines(new_line)

                position = 0
                await fgc.set_sipper_position(position, acceleration_nmps = 15000000, speed_nmps = 18000000, deceleration_nmps=15000000)
                await asyncio.sleep(0.1)
                # z_pos_nm = state['tele']['MotionAxisTelemetry_SipperZ']['position_nm']
                new_line = "{}, {}\n".format(time.time(), position)
                f.writelines(new_line)

        await fgc.home_sipper()
        return

async def main():
    await sipper_test()
    return

if __name__ == "__main__":
    asyncio.run(main())