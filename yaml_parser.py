import os
import yaml
import pandas as pd
import scipy
import numpy
from numpy.random import seed
from numpy.random import randn
from numpy import mean
from numpy import sqrt
from scipy.stats import chi2
from scipy.stats import norm
from scipy.stats import sem, t
from scipy.stats import linregress


def confint(data, confidence=0.95):
    '''
    params: 
            data: array-like. normally distributed continuous data
            con: level of confidence to achieve. Defaults to 0.95
    Returns:
            coefficient of confidence interval
    '''
    n = len(data)
    m = mean(data)
    std_err = sem(data)
    h = std_err * t.ppf((1 + confidence) / 2, n - 1)
    return (h / m)

def tolerance_interval(data, con=0.95, cov=0.95):
    """
    From https://machinelearningmastery.com/statistical-tolerance-intervals-in-machine-learning/
    From https://www.itl.nist.gov/div898/handbook/prc/section2/prc263.htm
    Calculates the 2-sided tolerance interval using Howe's method. Does not use Guenther's k2 correction.

    params: 
            data: array-like. normally distributed continuous data
            con: level of confidence to achieve. Defaults to 0.95
            cov: percent of population covered by the interval. Defaults to 0.95
    Returns:
            lower bound, upper bound
    """

    # specify degrees of freedom
    n = len(data)
    dof = n - 1
    # specify data coverage
    cov_inv = (1.0 - cov) / 2.0
    gauss_critical = norm.isf(cov_inv)
    #specify confidence
    chi_critical = chi2.isf(q=con, df=dof)
    # k_2
    k_2 = gauss_critical * sqrt((dof * (1 + (1/n))) / chi_critical)
    # summarize
    data_mean = mean(data)
    data_std = numpy.std(data)
    lower, upper = data_mean-(k_2*data_std), data_mean+(k_2*data_std)
    return (lower, upper)

def cal_statistics(masses, pressures, dis_time, filename, reagent, valve, time):

    cols = ("filename","time", "reagent", "valve", "mass 1", "mass 2", "mass 3", "mass 4", "mass 5", "pressure 1", "pressure 2", "pressure 3", 
            "pressure 4", "pressure 5", "L1", "L2", "L3", "L4", "L5", "Lavg", "Lstdev", "L_cv_abs", "pass/fail", "lowerbound", "upperbound", "ci_cf", "p-value")
    stats_df = pd.DataFrame(columns=cols)

    vol_flow = []

    # Convert mass and dispense time to volumetric flow rate of uL/s, assuming the calibration reagent is waster (i.e. specific gravity is ~1)
    # Converts pressure to psi using transfer function developed by pressure sensor manufacturer https://sensing.honeywell.com/index.php%3Fci_id%3D45841
    for i in range(len(masses)):
        vol_flow.append((masses[i] * 1000) / (dis_time / 1000.0)) # ul/s
        # pressures[i] = ((pressures[i] - 1638) / (14745 - 1638)) * 15 # psi
    # Compute Lohm for each dispense using equations developed by Lee Co https://www.theleeco.com/sites/leecompany/assets/efs-handbook/264/
    lohm = []
    for j in range(len(masses)):
        if vol_flow[j] != 0:
            lohm.append(scipy.sqrt(float(pressures[j])) / vol_flow[j])
        else:
            lohm.append(0)

    tolerance_lower, tolerance_upper = tolerance_interval(lohm)
    ci_cf = confint(lohm)
    # print("ci_cf: {}".format(ci_cf))
    slope, intercept, r_value, p_value, std_err = linregress(lohm, [0,1,2,3,4])
    # print("p_value: {}".format(p_value))

    lohm_avg = numpy.mean(lohm)
    lohm_stdev = numpy.std(lohm)

    if lohm_avg != 0:
        lohm_cv = numpy.abs((lohm_stdev / lohm_avg) * 100)
    else:
        lohm_cv = "NaN"

    if lohm_cv > 2.0:
        pass_fail = False
    else:
        pass_fail = True

    stats_df.loc[0] = (filename, time, reagent, valve, masses[0], masses[1], masses[2], masses[3], masses[4], pressures[0], pressures[1], pressures[2],
                       pressures[3], pressures[4], lohm[0], lohm[1], lohm[2], lohm[3], lohm[4], lohm_avg, lohm_stdev, lohm_cv, pass_fail, tolerance_lower, tolerance_upper, ci_cf, p_value)

    return stats_df

if __name__ == "__main__":

    df = []

    for file in os.listdir('.'):
        if file.endswith(".yaml"):
            filename = file
            stream = open(file, 'r')
            input_map = yaml.load(stream)
            # print(input_map)
            for j in range(1, 21):
                try:
                    masses = []
                    pressures = []
                    # reagent = input_map["reagents"]["valve_%d"%j]["short_name"]
                    reagent = "valve"
                    valve = j
                    timestamp = input_map['creation_ts']
                    timestamp_split = timestamp.split(sep='T', maxsplit=1)
                    date = timestamp_split[0]
                    time = timestamp_split[1].split(sep='.', maxsplit=1)[0]
                    date = date.replace('-', '/')
                    time = date + " " + time
                    # m/d/yyyy h:mm:ss
                    print(time)
                    # dis_time = (float(input_map['reagents']['valve_%d' % j]['dispenses']))
                    for i in range(0, 5):
                        # print(float(input_map['valves']['valve_%d' % j]['dispenses'][i]['grams']))
                        masses.append(float(input_map['valves']['valve_%d' % j]['dispenses'][i]['grams']))
                        pressures.append(float(input_map['valves']['valve_%d' % j]['dispenses'][i]['mean_gauge_pressure_psi']))
                    # print(masses)
                    # print(pressures)
                    df.append(cal_statistics(masses, pressures, 2000, filename, reagent, valve, time))
                except KeyError:
                    print("couldn't find valve %d in file %s" % (j, file))
                # except IndexError:
                #     print("list index out of range, valve %d in file %s" % (j, file))

    df_output = pd.concat(df)
    filename = "results_yaml.csv"
    df_output.to_csv(filename, sep=',', index=False)
    print("saved to file")
