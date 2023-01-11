import asyncio
import time
import loguru; LOG = loguru.logger
import os
import json
import argus.config
from rcembedded.txg.fdc.hw_rev02.interface import RcFDC as FDC
import numpy as np

async def test_cool_down_time():
    fdc = FDC()
    await fdc.reset()
    await fdc.init()
    await heat_and_stabilize()
    await cool_and_stabilize()
    for i in range(1,4):
        await fdc.disable_temperature_controller(i)
    return

async def heat_and_stabilize(set_point_C=30, t_stabilize=60):
    fdc = FDC()
    await fdc.set_lur_temp(1, set_point_C)
    await asyncio.sleep(0.5)
    await fdc.set_lur_temp(2, set_point_C)
    await asyncio.sleep(0.5)
    await fdc.set_lur_temp(3, set_point_C)
    await asyncio.sleep(0.5)

    temp_stable = False
    while not temp_stable:
        state = await fdc.getState()
        temp_1 = min(float(state['tele']['lur_1']['temp_avg_1_2_c']), float(state['tele']['lur_1']['temp_avg_3_4_c']))
        temp_1_stable = state['tele']['lur_1']['temp_is_stable']

        temp_2 = min(float(state['tele']['lur_2']['temp_avg_1_2_c']), float(state['tele']['lur_2']['temp_avg_3_4_c']))
        temp_2_stable = state['tele']['lur_2']['temp_is_stable']

        temp_3 = min(float(state['tele']['lur_3']['temp_avg_1_2_c']), float(state['tele']['lur_3']['temp_avg_3_4_c']))
        temp_3_stable = state['tele']['lur_3']['temp_is_stable']

        print(temp_1, temp_2, temp_3)
        print(temp_1_stable, temp_2_stable, temp_3_stable)

        if temp_1 >= set_point_C - 1 and temp_2 >= set_point_C - 1 and temp_3 >= set_point_C - 1:
            temp_stable =- True

        await asyncio.sleep(1)
    await asyncio.sleep(t_stabilize)
    return

async def cool_and_stabilize(set_point_C=5):
    fdc = FDC()

    await fdc.set_lur_temp(1, set_point_C)
    await asyncio.sleep(0.5)
    await fdc.set_lur_temp(2, set_point_C)
    await asyncio.sleep(0.5)
    await fdc.set_lur_temp(3, set_point_C)
    await asyncio.sleep(0.5)

    start_time = time.time()
    temp_stables = [0, 0, 0]
    temp_stable_times = [0, 0, 0]
    temp_stable = False
    with open ("fdc_lur_temp.txt", 'w') as f:
        f.write("time, lur_1_temp, lur_1_stable, lur_2_temp, lur_2_stable, lur_3_temp, lur_3_stable\n")
        while not temp_stable:
            state = await fdc.getState()
            temp_1 = max(float(state['tele']['lur_1']['temp_avg_1_2_c']), float(state['tele']['lur_1']['temp_avg_3_4_c']))
            temp_1_stable = state['tele']['lur_1']['temp_is_stable']

            temp_2 = max(float(state['tele']['lur_2']['temp_avg_1_2_c']), float(state['tele']['lur_2']['temp_avg_3_4_c']))
            temp_2_stable = state['tele']['lur_2']['temp_is_stable']

            temp_3 = max(float(state['tele']['lur_3']['temp_avg_1_2_c']), float(state['tele']['lur_3']['temp_avg_3_4_c']))
            temp_3_stable = state['tele']['lur_3']['temp_is_stable']

            new_line = "{}, {}, {}, {}, {}, {}, {}".format(time.time(), temp_1, temp_1_stable, temp_2, temp_2_stable, temp_3, temp_3_stable)
            f.writelines(new_line)

            print(new_line)
            print(temp_stables, temp_stable)

            if temp_1_stable == True and temp_stables[0] == 0:
                temp_stables[0] = 1
                temp_stable_times[0] = time.time() - start_time
            if temp_2_stable == True and temp_stables[1] == 0:
                temp_stables[1] = 1
                temp_stable_times[1] = time.time() - start_time
            if temp_3_stable == True and temp_stables[2] == 0:
                temp_stables[2] = 1
                temp_stable_times[2] = time.time() - start_time
            if np.sum(temp_stables) == 3:
                temp_stable = True
            
            await asyncio.sleep(0.5)
    print("#"*80)
    print("times to stability")
    print(temp_stable_times[0], temp_stable_times[1], temp_stable_times[2])
    print("#"*80)
    return
            



async def main():
    await test_cool_down_time()
    return

if __name__ == "__main__":
    asyncio.run(main())