#!/usr/bin/python3

import seaborn as sns
import pandas as pd

large = pd.read_csv('speedup.csv')

lg = sns.catplot(
    data=large, kind="bar",
    x="cat", y="speedup", hue="threads",
    palette="dark", alpha=.6, height=6
)
lg.despine(left=True)
lg.set_axis_labels("Allocation Range", "Speedup")
lg.legend.set_title("# Threads")

lg.savefig("speedup-summary.png")
