import os
import yaml
import pandas as pd
import scipy
import numpy



def cal_statistics(masses, pressures, dis_time, filename, reagent, valve):

    cols = ("filename", "reagent", "valve", "mass 1", "mass 2", "mass 3", "pressure 1", "pressure 2", "pressure 3", "L1", "L2",
             "L3", "Lavg", "Lstdev", "L_cv_abs", "pass/fail")
    stats_df = pd.DataFrame(columns=cols)

    vol_flow = []
    for i in range(len(masses)):
        vol_flow.append(masses[i] / (dis_time / 1000.0)) # ul/s
        pressures[i] = ((pressures[i] - 1638) / (14745 - 1638)) * 14.5 # psi
    # print(vol_flow)
    # print(pressures)

    lohm = []
    for j in range(len(masses)):
        if vol_flow[j] != 0:
            lohm.append(scipy.sqrt(float(pressures[j])) / vol_flow[j])
        else:
            lohm.append(0)
    # print(lohm)

    lohm_avg = numpy.mean(lohm)
    lohm_stdev = numpy.std(lohm)
    if lohm_avg != 0:
        lohm_cv = numpy.abs((lohm_stdev / lohm_avg) * 100)
    else:
        lohm_cv = "NaN"
    # print("lohm average: %f" % lohm_avg)
    # print("stdev: %f" % lohm_stdev)
    # print("percent_cv: %f" % lohm_cv)

    if lohm_cv > 2.0:
        pass_fail = False
    else:
        pass_fail = True

    stats_df.loc[0] = (filename, reagent, valve, masses[0], masses[1], masses[2], pressures[0], pressures[1], pressures[2],
                       lohm[0], lohm[1], lohm[2], lohm_avg, lohm_stdev, lohm_cv, pass_fail)

    # print(stats_df)
    return stats_df

if __name__ == "__main__":

    # cols = ("filename", "reagent", "mass 1", "mass 2", "mass 3", "pressure 1", "pressure 2", "pressure 3", "L1", "L2",
    #          "L3", "Lavg", "Lstdev", "L_cv_abs", "pass/fail")
    df = []

    for file in os.listdir('.'):
        if file.endswith(".yaml"):
            filename = file
            # print("file: %s" % file)
            stream = open(file, 'r')
            input_map = yaml.load(stream)
            for j in range(1, 13):
                try:
                    masses = []
                    pressures = []
                    reagent = input_map["reagents"]["valve_%d"%j]["short_name"]
                    valve = j
                    # print("reagent: %s" % reagent)
                    dis_time = (float(input_map['reagents']['valve_%d' % j]['dispense_ms']))
                    # print("dispense time: %d" % dis_time)
                    for i in range(1, 4):
                        masses.append(float(input_map['reagents']['valve_%d' % j][i]['grams']))
                        pressures.append(float(input_map['reagents']['valve_%d' % j][i]['mean_static_pressure']))
                    df.append(cal_statistics(masses, pressures, dis_time, filename, reagent, valve))
                    # print(df)
                except KeyError:
                    print("couldn't find valve %d in file %s" % (j, file))

    print(df)
    df_output = pd.concat(df)
    filename = "results.csv"
    df_output.to_csv(filename, sep=',', index=False)
    print("saved to file")
