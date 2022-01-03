#!/usr/bin/env python3

"""Calculator to calculate the viscosity of a mixture of water and another substance.
The default substance is formamide.

Usage: python ViscosityFractionCalculator.py volume_percent [dynamic viscosity cp] [density g/cm^3]
"""

## This python code is based on the MatLab code orginaly provided by Chris Westbrook
## http://www.met.reading.ac.uk/~sws04cdw/viscosity_calc.html

__author__  = "Eric Evje"
__license__ = "GPL"
__version__ = "1.0"
__credits__ = "Chris Westbrook"


#Required packages ----------------

import numpy
import math
import argparse

def solution_viscosity(volume_percent, solute_den=1.13, solute_vis=0.003302):
    '''
    Function to compute the viscosity of an aqueous solution. The default density and viscosity
    are for formamide. The temperature is 20C as a default and cannot be changed. 

    params: 
        volume_percent: the percent of the solution made up by the solute
        solute_den: density of the solute in g/cm3
        solute_vis: dynamic viscosity of the solute in Pa*s
    returns:
        kinematic viscosity of solution in centiStokes
    '''
    #Variables ----------------
    volume_percent = float(volume_percent)
    waterDen = .9982 #Density of water (g/cm3) .9982
    water_vol = 100.0 - volume_percent
    water_vis = 0.001 #Pa * s .001
    T = 20.0 # Constant for temperature in C

    #Fraction cacluator ----------------
    solute_mass = solute_den * volume_percent
    waterMass = waterDen * water_vol
    totalMass = solute_mass + waterMass
    mass_fraction = solute_mass / totalMass
    vol_fraction = volume_percent / (volume_percent + water_vol)
    
    # Density of solution equation
    density_mix = (solute_den * vol_fraction + waterDen * (1 - vol_fraction))

    #Viscosity calcualtor
    a=0.705-0.0017*T
    b=(4.9+0.036*T)*numpy.power(a,2.5)
    alpha=1-mass_fraction+(a*b*mass_fraction*(1-mass_fraction))/(a*mass_fraction+b*(1-mass_fraction))
    A=numpy.log(water_vis/solute_vis)

    viscosity_mix=solute_vis*numpy.exp(A*alpha)
    viscosity_mix_kin = (viscosity_mix / density_mix) * 1000.0

    print ("Mass fraction of mixture =", round(mass_fraction, 5))
    print ("Volume fraction of mixture =", round(vol_fraction, 5))
    print ("Density of mixture =", round(density_mix,5),"g/cm3")
    print ("Dynamic Viscosity of mixture =", round(viscosity_mix,5), "Ns/m2")
    print ("Kinematic Viscosity of mixture =", round(viscosity_mix_kin,5), "centiStokes")

    return viscosity_mix_kin

def correction_factor(viscosity_kin):
    '''
    Function to calculate the viscosity correction factor for the V2 fluidics unit.

    params: 
        viscosity_kin: the kinematic viscosity of the reagent in centiStokes

    returns: Decmial correction factor
    '''
    # Equation found in G:\Team Drives\Engineering\Development\Projects\
    # SubsystemsProjects\FluidicsUnit\Testing\20181003_formamide_dispense_volume_troubleshooting\
    # 20181004_Regression_flow_rate_vs formamide_concentration.xlsx
    correction_factor = -0.306 * math.log(viscosity_kin) + 0.9642
    print ("correction factor for solution is %f" % correction_factor) 

    return correction_factor

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process incoming solute information.')
    parser.add_argument('volume_percent', type=int,
                        help='percent of the mixture by volume of the solute')
    parser.add_argument('-d','--density', dest='solute_den', default=1.13, action='store', nargs='?', type=float,
                        help='density of the solute in g/cm^3')
    parser.add_argument('-v','--dynamic_viscosity', dest='solute_vis', default=0.003302, action='store', nargs='?', type=float,
                        help='dynamic viscosity of solute in Pa*s')

    args = parser.parse_args()

    viscosity_mix_kin = solution_viscosity(args.volume_percent, args.solute_den, args.solute_vis)
    vis_correction_f = correction_factor(viscosity_mix_kin)

