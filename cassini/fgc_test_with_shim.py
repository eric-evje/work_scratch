#from cgi import test
#from re import M
#from interface import Cs1RcSCC
import asyncio
import time
import loguru; LOG = loguru.logger
import sys
# import argus.config
from rcembedded.readcoor.rc_pcb_fgc.cs1.interface import FGC
from rcembedded.oem.maestro.v7.interface import RcMaestro
from argus.config.instrument_models.cs1.cs1_wrapper import CS1_Wrapper

async def main():
    fgc = FGC()
    
    input("Press FGC reset button then press ENTER")
    time.sleep(10)
    
    input("Press ENTER to reset FGC")
    res = await fgc.reset()
    print(res)
    
    input("Press ENTER to init FGC")
    res = await fgc.init()
    print(res)
    
    input("Press ENTER to HOME ADP Axis")
    res = await fgc.home_adp()
    print(res)

    input("Press ENTER to HOME SIP Axis")
    res = await fgc.home_sipper()
    print(res)
    
    input("Press ENTER to HOME GANTRY Axis")
    res = await fgc.home_gantry()
    print(res)
  
    input("Press ENTER to MOVE GANTRY Axis")
    res = await fgc.set_gantry_x_position(470000000)
    print(res)
    
    #input("Press ENTER to MOVE GANTRY Axis")
    res = await fgc.set_gantry_x_position(0)
    print(res)

    input("Press ENTER to MOVE SIP Axis")
    res = await fgc.set_sipper_position(30000000)
    print(res)

    #input("Press ENTER to MOVE SIP Axis")
    res = await fgc.set_sipper_position(0)
    print(res)
        
    input("Press ENTER to MOVE ADP Axis")
    res = await fgc.set_adp_position(70000000)
    print(res)

    #input("Press ENTER to MOVE ADP Axis")
    res = await fgc.set_adp_position(0)
    print(res)

    input("Remove TIP from ADP and Press ENTER")
    state = await fgc.get_state()
    res = state['tele']['AdpTelemetry']['tipPresent']
    print("tipPresent = " + str(res))
      
    input("Attach TIP from ADP and Press ENTER")
    state = await fgc.get_state()
    res = state['tele']['AdpTelemetry']['tipPresent']
    print("tipPresent = " + str(res))
      
    input("Press ENTER to Eject ADP Tip")
    res = await fgc.eject_adp_tip()
    print(res)
    
    input("Open PPUMP LID and Press ENTER")
    state = await fgc.get_state()
    res = state['tele']['PPumpTelemetry']['lidOpen']
    print("lidOpen = " + str(res))

    input("Close PPUMP LID and Press ENTER")
    state = await fgc.get_state()
    res = state['tele']['PPumpTelemetry']['lidOpen']
    print("lidOpen = " + str(res))    
    
    input("Press ENTER to RUN Reristaltic Pump")        
    res = await fgc.start_peristaltic_pump(rpm = 100, startDelay_ms=10)  
    print(res)
    time.sleep(3)
    state = await fgc.get_state()
    res = state['tele']['PPumpTelemetry']['targetRpm']
    print("PPUMP TARGET = " + str(res))      
    res = state['tele']['PPumpTelemetry']['rpm']
    print("PPUMP RPM = " + str(res))  
 
    input("Press ENTER to STOP Reristaltic Pump")        
    res = await fgc.stop_peristaltic_pump()
    print(res)
    time.sleep(3)
    state = await fgc.get_state()
    res = state['tele']['PPumpTelemetry']['targetRpm']
    print("PPUMP TARGET = " + str(res))      
    res = state['tele']['PPumpTelemetry']['rpm']
    print("PPUMP RPM = " + str(res))  
 
    input("Press ENTER to MOVE GANTRY Axis")
    res = await fgc.set_gantry_x_position(470000000)
    print(res)
    
    input("Press ENTER to INITIALIZE SPUMP1")        
    res = await fgc.initialize_syringe_pump(pump_id = 0, syringe_capacity_uL = 5000, in_port_select = 0, backup_rate_uLps = 100, backup_volume_uL = 0)
    print(res)

    input("Press ENTER to INITIALIZE SPUMP2")        
    res = await fgc.initialize_syringe_pump(pump_id = 1, syringe_capacity_uL = 5000, in_port_select = 0, backup_rate_uLps = 100, backup_volume_uL = 0)
    print(res)
    
    input("Press ENTER to INITIALIZE SPUMP3")        
    res = await fgc.initialize_syringe_pump(pump_id = 2, syringe_capacity_uL = 5000, in_port_select = 0, backup_rate_uLps = 100, backup_volume_uL = 0)
    print(res)
    
    input("Press ENTER to INITIALIZE SPUMP4")        
    res = await fgc.initialize_syringe_pump(pump_id = 3, syringe_capacity_uL = 5000, in_port_select = 0, backup_rate_uLps = 100, backup_volume_uL = 0)
    print(res)
    
    input("Press ENTER to RUN Water Pump at 100")        
    res = await fgc.lcb_pump_ctrl(enable = True, speed=100)  
    print(res)
    time.sleep(10)
    state = await fgc.get_state()
    res = state['tele']['LcbTelemetry']['cameraFlow_lpm']
    print("cameraFlow_lpm = " + str(res))      
    res = state['tele']['LcbTelemetry']['coolantFlow_lpm']
    print("coolantFlow_lpm = " + str(res))         
    res = state['tele']['LcbTelemetry']['ledFlow_lpm']
    print("ledFlow_lpm = " + str(res))  
    res = state['tele']['LcbTelemetry']['loop1Flow_lpm']
    print("loop1Flow_lpm = " + str(res))      
    res = state['tele']['LcbTelemetry']['loop1Flow_lpm']
    print("loop1Flow_lpm = " + str(res))  
    res = state['tele']['LcbTelemetry']['loop2Flow_lpm']
    print("loop2Flow_lpm = " + str(res))   
    res = state['tele']['LcbTelemetry']['loop3Flow_lpm']
    print("loop3Flow_lpm = " + str(res))   
    
    input("Press ENTER to RUN Water Pump at 30")        
    res = await fgc.lcb_pump_ctrl(enable = True, speed=30)  
    print(res)
    time.sleep(10)
    state = await fgc.get_state()
    res = state['tele']['LcbTelemetry']['cameraFlow_lpm']
    print("cameraFlow_lpm = " + str(res))      
    res = state['tele']['LcbTelemetry']['coolantFlow_lpm']
    print("coolantFlow_lpm = " + str(res))         
    res = state['tele']['LcbTelemetry']['ledFlow_lpm']
    print("ledFlow_lpm = " + str(res))  
    res = state['tele']['LcbTelemetry']['loop1Flow_lpm']
    print("loop1Flow_lpm = " + str(res))      
    res = state['tele']['LcbTelemetry']['loop1Flow_lpm']
    print("loop1Flow_lpm = " + str(res))  
    res = state['tele']['LcbTelemetry']['loop2Flow_lpm']
    print("loop2Flow_lpm = " + str(res))   
    res = state['tele']['LcbTelemetry']['loop3Flow_lpm']
    print("loop3Flow_lpm = " + str(res))     
 
    input("Press ENTER to FANS at 100")        
    res = await fgc.lcb_set_fan_speed(fan1DutyCycle = 100, fan2DutyCycle = 100, fan3DutyCycle = 100)  
    print(res)
    time.sleep(10)
    state = await fgc.get_state()
    res = state['tele']['LcbTelemetry']['fan1Speed_rpm']
    print("fan1Speed_rpm = " + str(res))      
    res = state['tele']['LcbTelemetry']['fan1DutySp']
    print("fan1DutySp = " + str(res))         
    res = state['tele']['LcbTelemetry']['fan2Speed_rpm']
    print("fan2Speed_rpm = " + str(res))  
    res = state['tele']['LcbTelemetry']['fan2DutySp']
    print("fan2DutySp = " + str(res))      
    res = state['tele']['LcbTelemetry']['fan3Speed_rpm']
    print("fan3Speed_rpm = " + str(res))  
    res = state['tele']['LcbTelemetry']['fan3DutySp']
    print("fan3DutySp = " + str(res))        
 
    input("Press ENTER to FANS at 20")        
    res = await fgc.lcb_set_fan_speed(fan1DutyCycle = 20, fan2DutyCycle = 20, fan3DutyCycle = 20)  
    print(res)
    time.sleep(10)
    state = await fgc.get_state()
    res = state['tele']['LcbTelemetry']['fan1Speed_rpm']
    print("fan1Speed_rpm = " + str(res))      
    res = state['tele']['LcbTelemetry']['fan1DutySp']
    print("fan1DutySp = " + str(res))         
    res = state['tele']['LcbTelemetry']['fan2Speed_rpm']
    print("fan2Speed_rpm = " + str(res))  
    res = state['tele']['LcbTelemetry']['fan2DutySp']
    print("fan2DutySp = " + str(res))      
    res = state['tele']['LcbTelemetry']['fan3Speed_rpm']
    print("fan3Speed_rpm = " + str(res))  
    res = state['tele']['LcbTelemetry']['fan3DutySp']
    print("fan3DutySp = " + str(res))    
    
    input("Press ENTER to MOVE GANTRY Axis")
    res = await fgc.set_gantry_x_position(0)
    print(res)
    
    input("Press FGC reset button then press ENTER")
 
async def home_all_axes():
    '''Homes all FGC controlled fluidics axes
    params:
    returns:
    '''
    fgc = FGC()
    await fgc.home_sipper()
    await fgc.home_adp()
    await fgc.home_gantry()
    return

async def move_carrier():
    '''Homes maestro coordinated motors and moves sample carrier to safe position to exercise full range of sipper axis
    params:
    returns:
    '''
    # Instantiates RcMaestro class
    mmc = RcMaestro(device_variant='rc2')
    # Homes maestro controlled motors
    await mmc.init()
    # Computes location of ADP tip eject location
    results = CS1_Wrapper().solve_for_ADP_tip_to_tip_eject(1)
    # Sends sample carrier to tip eject location
    await mmc.set_group_position_abs(
        group_name='g_sc0_xy',
        pa_x_nm=results['carrier_x'],
        pa_y_nm=results['carrier_y'])
    return

async def sipper_breakin(sc_motion):
    print(sc_motion)
    # fgc = FGC()
    
    input("Press ENTER to home motors ... ")
    # await home_all_axes()

    if sc_motion:
        input("Press ENTER to home carrier and move to safe position ... ")
        await move_carrier()

    input("Press ENTER to move X to safe position ... ")
    position = 325000000
    await fgc.set_gantry_x_position(position)
    print("X set to {} mm".format(position/1000000))

    input("Press ENTER to drive sipper to bottom of travel ")
    await fgc.set_sipper_position(50000000, acceleration_nmps=15000000, speed_nmps=5000000, deceleration_nmps=15000000)
    await asyncio.sleep(0.25)
    
    input("Remove lead screw stiffener and homing flag, then loosen motor mount bolts\n******\n\
        Press ENTER when complete ... ")
    await fgc.set_sipper_position(0, acceleration_nmps=15000000, speed_nmps=5000000, deceleration_nmps=15000000)
    await asyncio.sleep(0.25)

    input("Press ENTER to exercise extract axis (slow speed) ... ")
    cycles = 5
    for cycle in range(cycles):
        print("cycle {} of {}".format(cycle+1, cycles))
        await fgc.set_sipper_position(50000000, acceleration_nmps=15000000, speed_nmps=5000000, deceleration_nmps=15000000)
        await asyncio.sleep(0.25)
        await fgc.set_sipper_position(0, acceleration_nmps = 15000000, speed_nmps = 5000000, deceleration_nmps=15000000)
        await asyncio.sleep(0.25)
    
    input("Carefully tighten rear right and front left motor mount bolts\n******\n\
        Press ENTER when complete ... ")
    await fgc.set_sipper_position(50000000, acceleration_nmps=15000000, speed_nmps=5000000, deceleration_nmps=15000000)
    await asyncio.sleep(0.25)
    
    input("Tighten all motor mount bolts\n******\n\
        Add lead screw stiffener and homing flag. Shim under the bolts between the stiffener and flag to tilt stiffener\n******\n\
        Align top of stiffener as best possible with the lead screw left to right by eye and feel\n******\n\
        Insert O-Ring as far as possible. Pulling the stiffener forward can help make space\n******\n\
        Press Enter when complete")
        
    await fgc.set_sipper_position(0, acceleration_nmps= 15000000, speed_nmps = 5000000, deceleration_nmps=15000000)
    await asyncio.sleep(0.25)
    
    return

async def sipper_test():
    fgc = FGC()
    input("Press ENTER to begin Extract axis stress test ... ")
    print("Beginning test: Check for audible resonance of motor during travel")
    await fgc.home_sipper()
    cycles = 25
    for cycle in range(cycles):
        print("cycle {} of {}".format(cycle+1, cycles))
        await fgc.set_sipper_position(50000000, acceleration_nmps = 15000000, speed_nmps = 18000000, deceleration_nmps=15000000)
        await asyncio.sleep(0.25)
        await fgc.set_sipper_position(500000, acceleration_nmps = 15000000, speed_nmps = 18000000, deceleration_nmps=15000000)
        await asyncio.sleep(0.25)
    await fgc.home_sipper()
    return

async def peri_tube_breakin():
    fgc = FGC()
    input("Press ENTER to home all fluidics axes ... ")
    await home_all_axes()
    input("Open lid of peristaltic pump, then press ENTER ... ")
    try:
        await fgc.start_peristaltic_pump(rpm = 100, startDelay_ms=10)
        input("Beginning peri pump. With tube in place, hold lid about halfway down. \n \
            If the motor stalls, Open the lid and start again. \n \
            When you can close the lid completely with the motor still running, press ENTER ... ")
        await fgc.stop_peristaltic_pump()
        input("Press ENTER to run peri pump for 10 seconds. Ensure the pump spins ... ")
        await fgc.start_peristaltic_pump(rpm = 100, startDelay_ms=10)
        await asyncio.sleep(10)
        await fgc.stop_peristaltic_pump()
    finally:
        await fgc.stop_peristaltic_pump()
    return

if __name__ == "__main__":
    selection = ''
    sc_motion = True
    n = len(sys.argv)
    if n > 1:
        if sys.argv[1] == '-m':
            sc_motion = False
        else:
            print("#" * 80)
            print("WARNING: Did you mean -m ?")
            print("Will try to move sample carrier motors")
            print("#" * 80)

    while selection.lower() != 'q':
        selection = input("******\nFor sipper test and exit, press [ENTER], for extract install [1], for peri tube install [2], [Q] to quit: ")
        if selection == '':
            asyncio.run(main())
            selection = 'Q'
        elif selection == '1':
            asyncio.run(sipper_breakin(sc_motion))
            asyncio.run(sipper_test())
        elif selection == '2':
            asyncio.run(peri_tube_breakin())
