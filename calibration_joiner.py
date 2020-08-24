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
    # print(data)
    m = numpy.mean(data)
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
    data_mean = numpy.mean(data)
    data_std = numpy.std(data)
    lower, upper = data_mean-(k_2*data_std), data_mean+(k_2*data_std)
    return (lower, upper)

def cal_statistics(masses, pressures, dis_time, filename, reagent, valve, time, replicate):
    # print(masses)

    cols = ("filename", "time", "replicate", "reagent", "valve", "mass 1", "mass 2", "mass 3", "mass 4", "mass 5", "pressure 1", "pressure 2", "pressure 3", 
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

    stats_df.loc[0] = (filename, time, replicate, reagent, valve, masses[0], masses[1], masses[2], masses[3], masses[4], pressures[0], pressures[1], pressures[2],
                       pressures[3], pressures[4], lohm[0], lohm[1], lohm[2], lohm[3], lohm[4], lohm_avg, lohm_stdev, lohm_cv, pass_fail, tolerance_lower, tolerance_upper, ci_cf, p_value)

    return stats_df
    

if __name__ == "__main__":
    # results_cols = ('valve', 'ci_cf', 'corr', 'dis_1', 'dis_2', 'dis_3', 'dis_4', 'mean', 'stdev', 'delta')
    # results = pd.DataFrame(columns=results_cols)
    final = []

    csv_dirs = os.listdir("C:\\Users\\ericevje\\Documents\\github\\work_scratch\\cal_files")
    index = 0
    for file in csv_dirs:
        if file.endswith(".csv"):
            try:
                filename = "C:\\Users\\ericevje\\Documents\\github\\work_scratch\\cal_files\\" + file
                df = pd.read_csv(filename)

                replicate = file.split('_')[1]
                # print(replicate)

                means = []
                for i in range(1, 21):
                    results_cols = ('replicate', 'valve', 'prime', 'flush',
                                'dis_1', 'dis_2', 'dis_3', 'dis_4', 'mean', 'stdev', 'delta', 'abs_delta', 'error_max')
                    results = pd.DataFrame(columns=results_cols)

                    dispense_df = df[(df['valve_num']==i) & (df['dispense_type'] == 'reagent')]
                    prime_df = df[(df['valve_num']==i) & (df['dispense_type'] == 'prime')]
                    flush_df = df[(df['valve_num']==i) & (df['dispense_type'] == 'flush')]
                    mean = numpy.mean(dispense_df['weight_mg'])
                    stdev = numpy.std(dispense_df['weight_mg'])
                    delta = mean - 200
                    abs_delta = abs(delta)

                    valve = i
                    dispenses = len(dispense_df.index)
                    dis = []
                    error = []
                    for j in range(0, dispenses):
                        dis.append(dispense_df['weight_mg'].iloc[j])
                        error.append(abs(dis[j] - 200))
                    err_max = max(error)

                    results.loc[0] = (replicate, valve, prime_df['weight_mg'].iloc[0], flush_df['weight_mg'].iloc[0], 
                                        dis[0], dis[1], dis[2], dis[3], mean, stdev, delta, abs_delta, err_max) 
                    final.append(results)
            finally:
                print("placeholder")
    
    df_dis = pd.concat(final)
    # means = calc_means(df_output)
    df_dis.to_csv("dispense_results.csv", sep=',', index=False)


    final_cal = []
    for file in os.listdir('.'):
        if file.endswith(".yaml"):
            filename = file
            stream = open(file, 'r')
            input_map = yaml.load(stream)

            replicate = filename.split('_')[1]

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
                    # print(time)
                    # dis_time = (float(input_map['reagents']['valve_%d' % j]['dispenses']))
                    for i in range(0, 5):
                        # print(float(input_map['valves']['valve_%d' % j]['dispenses'][i]['grams']))
                        masses.append(float(input_map['valves']['valve_%d' % j]['dispenses'][i]['grams']))
                        pressures.append(float(input_map['valves']['valve_%d' % j]['dispenses'][i]['mean_gauge_pressure_psi']))
                    # print(masses)
                    # print(pressures)
                    final_cal.append(cal_statistics(masses, pressures, 2000, filename, reagent, valve, time, replicate))
                except KeyError:
                    print("couldn't find valve %d in file %s" % (j, file))
                # except IndexError:
                #     print("list index out of range, valve %d in file %s" % (j, file))

    df_cal = pd.concat(final_cal)
    filename = "results_yaml.csv"
    df_cal.to_csv(filename, sep=',', index=False)
    print("saved to file")


    df_cal, df_dis

    df_outer = pd.merge(df_cal, df_dis, on=['valve', 'replicate'], how='outer')
    df_outer.to_csv("joined.csv", sep=',', index=False)





