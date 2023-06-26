import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def trace_progress(infile="SS.out"):
    with open(infile,"r") as file:
        log = file.readlines()

    entry_lst = ''.join(log).replace('\n','').replace('\t','').split('SolarSim started at ')
    # 2022-04-06T17:37:14SolarSim read in completed at 2022-04-06T17:37:15SolarSim finished at 599 seconds started at 2022-04-06T17:37:14[-4.28674123 -5.82008034 -0.20770926  1.41072099  5.74435594]:Min:-0.01809End:39.71Max:100.0CostFunction:62.2968
    entry_template = re.compile("([0-9-T:]*)SolarSim read in completed at ([0-9-T:]*)SolarSim finished at [0-9]* seconds started at ([0-9-T:]*)(\[[0-9\s\.\,-]*\]):Min:([0-9\-\.]*)End:([0-9\-\.]*)Max:([0-9\-\.]*)CostFunction:([0-9\-\.]*)Driving Time:([0-9\-\.]*)Average Velocity:([0-9\-\.]*)Vstd:([0-9\-\.]*).*")

    columns = ["start","readin","duration","x_array","SoCMin","SoC","SoCMax","CostFun","Duration","AvgVel","Vstd"]
    df = pd.DataFrame(columns=columns,index=[1])

    for i,entry in enumerate(entry_lst):
        mtch = entry_template.match(entry)

        if mtch is not None:
            arraymtch = re.match('\[\s*([0-9\-\.]*),\s*([0-9\-\.]*),\s*([0-9\-\.]*),\s*([0-9\-\.]*),\s*([0-9\-\.]*)\s*\]', mtch.group(4))
            ary = np.array([float(arraymtch.group(1)),
                            float(arraymtch.group(2)),
                            float(arraymtch.group(3)),
                            float(arraymtch.group(4)),
                            float(arraymtch.group(5))])
            df.loc[i,:] = [np.datetime64(mtch.group(1)),np.datetime64(mtch.group(2)),np.datetime64(mtch.group(3)),ary,
                           float(mtch.group(5)),float(mtch.group(6)),float(mtch.group(7)),float(mtch.group(8)),
                           float(mtch.group(9)),float(mtch.group(10)),float(mtch.group(11))]
        else:
            print(entry)
    lst = df.CostFun.copy()
    for i, x in enumerate(lst):
        lst[i] = min(lst[:i + 1])
    df.loc[:,"Optimal"] = -lst
    return df

if __name__ == '__main__':
    df = trace_progress("SS-coldstart.out")
    df1 = trace_progress("SS-warmstart.out")
    fig,ax = plt.subplots(1)
    ax.plot(df)