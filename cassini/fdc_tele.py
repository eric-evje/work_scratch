import asyncio
import time
import loguru; LOG = loguru.logger
import os
import json
import argus.config
from rcembedded.txg.fdc.hw_rev02.interface import RcFDC

async def fdc_tele():
    fdc = RcFDC()
    await fdc.reset()
    await fdc.init()
    print("Waste\tHUR1\tHUR2\tHUR3\tHUR4")
    while True:
        state = await fdc.getState()
        waste_state = state['tele']['bulks']['is_waste_present']
        hur1_state = state['tele']['bulks']['is_hur_1_bottle_present']
        hur2_state = state['tele']['bulks']['is_hur_2_bottle_present']
        hur3_state = state['tele']['bulks']['is_hur_3_bottle_present']
        hur4_state = state['tele']['bulks']['is_hur_4_bottle_present']
        print("{}\t{}\t{}\t{}\t{}".format(waste_state, hur1_state, hur2_state, hur3_state, hur4_state), end='\r')
        await asyncio.sleep(1)

async def main():
    await fdc_tele()
    return

if __name__ == "__main__":
    asyncio.run(main())