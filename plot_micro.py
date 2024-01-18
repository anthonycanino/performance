#!/usr/bin/python3

import seaborn as sns
import pandas as pd

large = pd.read_csv('large.csv')

lg = sns.catplot(
    data=large, kind="bar",
    x="page_faults", y="time", hue="clear_type",
    palette="dark", alpha=.6, height=6
)
lg.despine(left=True)
lg.set_axis_labels("", "Time (ms)")
lg.legend.set_title("")

lg.savefig("large-micro.png")

mixed = pd.read_csv('mixed.csv')

mg = sns.catplot(
    data=mixed, kind="bar",
    x="page_faults", y="time", hue="clear_type",
    palette="dark", alpha=.6, height=6
)
mg.despine(left=True)
mg.set_axis_labels("", "Time (ms)")
mg.legend.set_title("")

mg.savefig("mixed-micro.png")