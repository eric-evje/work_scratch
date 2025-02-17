import os
# import yaml
import pandas as pd
import scipy
import numpy
from numpy.random import seed
from numpy.random import randn
from numpy import mean
from numpy import sqrt
from scipy.stats import chi2
from scipy.stats import norm



# def tolerance_interval(data, con=0.95, cov=0.95):
#     """
#     From https://machinelearningmastery.com/statistical-tolerance-intervals-in-machine-learning/
#     From https://www.itl.nist.gov/div898/handbook/prc/section2/prc263.htm
#     Calculates the 2-sided tolerance interval using Howe's method. Does not use Guenther's k2 correction.

#     params: 
#             data: array-like. normally distributed continuous data
#             con: level of confidence to achieve. Defaults to 0.95
#             cov: percent of population covered by the interval. Defaults to 0.95
#     Returns:
#             lower bound, upper bound
#     """

#     # specify degrees of freedom
#     n = len(data)
#     dof = n - 1
#     # specify data coverage
#     cov_inv = (1.0 - cov) / 2.0
#     gauss_critical = norm.isf(cov_inv)
#     #specify confidence
#     chi_critical = chi2.isf(q=con, df=dof)
#     # k_2
#     k_2 = gauss_critical * sqrt((dof * (1 + (1/n))) / chi_critical)
#     # summarize
#     data_mean = mean(data)
#     data_std = numpy.std(data)
#     lower, upper = data_mean-(k_2*data_std), data_mean+(k_2*data_std)
#     return (lower, upper)

# def cal_statistics(masses, pressures, dis_time, filename, reagent, valve):

#     cols = ("filename", "reagent", "valve", "mass 1", "mass 2", "mass 3", "mass 4", "mass 5", "pressure 1", "pressure 2", "pressure 3", 
#             "pressure 4", "pressure 5", "L1", "L2", "L3", "L4", "L5", "Lavg", "Lstdev", "L_cv_abs", "pass/fail", "lowerbound", "upperbound")
#     stats_df = pd.DataFrame(columns=cols)

#     vol_flow = []

#     # Convert mass and dispense time to volumetric flow rate of uL/s, assuming the calibration reagent is waster (i.e. specific gravity is ~1)
#     # Converts pressure to psi using transfer function developed by pressure sensor manufacturer https://sensing.honeywell.com/index.php%3Fci_id%3D45841
#     for i in range(len(masses)):
#         vol_flow.append(masses[i] / (dis_time / 1000.0)) # ul/s
#         pressures[i] = ((pressures[i] - 1638) / (14745 - 1638)) * 14.5 # psi

#     # Compute Lohm for each dispense using equations developed by Lee Co https://www.theleeco.com/sites/leecompany/assets/efs-handbook/264/
#     lohm = []
#     for j in range(len(masses)):
#         if vol_flow[j] != 0:
#             lohm.append(scipy.sqrt(float(pressures[j])) / vol_flow[j])
#         else:
#             lohm.append(0)

#     tolerance_lower, tolerance_upper = tolerance_interval(lohm)

#     lohm_avg = numpy.mean(lohm)
#     lohm_stdev = numpy.std(lohm)

#     if lohm_avg != 0:
#         lohm_cv = numpy.abs((lohm_stdev / lohm_avg) * 100)
#     else:
#         lohm_cv = "NaN"

#     if lohm_cv > 2.0:
#         pass_fail = False
#     else:
#         pass_fail = True

#     stats_df.loc[0] = (filename, reagent, valve, masses[0], masses[1], masses[2], masses[3], masses[4], pressures[0], pressures[1], pressures[2],
#                        pressures[3], pressures[4], lohm[0], lohm[1], lohm[2], lohm[3], lohm[4], lohm_avg, lohm_stdev, lohm_cv, pass_fail, tolerance_lower, tolerance_upper)

#     return stats_df

def calc_means(df):
    

if __name__ == "__main__":
    # results_cols = ('valve', 'ci_cf', 'corr', 'dis_1', 'dis_2', 'dis_3', 'dis_4', 'mean', 'stdev', 'delta')
    # results = pd.DataFrame(columns=results_cols)
    final = []

    dirs = os.listdir("/Users/ericevje/gitrepos/work_scratch/cal_files")
    index = 0
    for file in dirs:
        if file.endswith(".csv"):
            try:
                results_cols = ('valve', 'ci_cf', 'corr', 'dis_1', 'dis_2', 'dis_3', 'dis_4', 'mean', 'stdev', 'delta', 'abs_delta')
                results = pd.DataFrame(columns=results_cols)
                filename = "/Users/ericevje/gitrepos/work_scratch/cal_files/" + file
                df = pd.read_csv(filename)
                valve = df['valve_num'].iloc[0]
                ci_cf = df['ci_cf'].iloc[0]
                corr = df['corr'].iloc[0]
                dispenses = len(df.index)
                dis = []
                for i in range(0, dispenses):
                    dis.append(df['weight_mg'].iloc[i])
                mean = numpy.mean(dis)
                stdev = numpy.std(dis)
                delta = mean - 200
                abs_delta = abs(delta)

                # results_line = (valve, ci_cf, corr, dis[0], dis[1], dis[2], dis[3], mean, stdev, delta)
                results.loc[0] = (valve, ci_cf, corr, dis[0], dis[1], dis[2], dis[3], mean, stdev, delta, abs_delta)
                # print(results) 
                final.append(results)
                # print(final)
            # except:
            #     print("some kind of error")
            finally:
                print("placeholder")
    
    df_output = pd.concat(final)
    means = calc_means(df_output)
    df_output.to_csv("cal_results.csv", sep=',', index=False)





