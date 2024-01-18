#!/usr/bin/python3
import os
import argparse
import pandas
from statistics import mean, stdev

#NTHREADS = [1]
NTHREADS = [1, 2]
LOHAR = [50, 500, 700, 800, 900, 999]
#LOHAR = [-1]
#DSA_CONFIG = ["1-1", "1-2", "1-4", "2-1", "2-2", "2-4"]
DSA_CONFIG = ["2-1"]
LOWR = 90000
HIGHR = 2000000
NRUNS = 5
NDISCARD = 0

def detect(data):
  dev = stdev(data)
  m = mean(data)
  low = m - (dev * 2.5)
  high = m + (dev * 2.5)
  return filter(lambda x: x >= low and x <= high, data)

def read_run(path):
  with open(path, "r") as f:
    l = f.readline()
    l = f.readline().split(" ")[1][:-3]
    return float(l)/1000.0

def analyze_case(filename, nthreads, lor, lowr, highr, dsa_config, markdown, speedup):
  path = ""
  if lowr == -1:
    path = os.path.join(filename, f"with-dml-small-{nthreads}-{dsa_config}")
  else:
    if lor == -1:
      path = os.path.join(filename, f"with-dml-{lowr}-{highr}-{nthreads}-{dsa_config}")
    else:
      path = os.path.join(filename, f"with-dml-{lor}-{lowr}-{highr}-{nthreads}-{dsa_config}")

  with_dml = 0.0
  with_dmls = []
  for i in range(NDISCARD+1, NRUNS+1):
    fpath = os.path.join(path, f"run-{i}.txt")
    e = read_run(fpath)
    with_dmls.append(e)

  path = ""
  if lowr == -1:
    path = os.path.join(filename, f"no-dml-small-{nthreads}-{dsa_config}")
  else:
    if lor == -1:
      path = os.path.join(filename, f"no-dml-{lowr}-{highr}-{nthreads}-{dsa_config}")
    else:
      path = os.path.join(filename, f"no-dml-{lor}-{lowr}-{highr}-{nthreads}-{dsa_config}")

  no_dml = 0.0
  no_dmls = []
  for i in range(NDISCARD+1, NRUNS+1):
    fpath = os.path.join(path, f"run-{i}.txt")
    e = read_run(fpath)
    no_dmls.append(e)

  no_dml = mean(no_dmls)
  with_dml = mean(with_dmls)

  diff = no_dml - with_dml
  ratio = no_dml / with_dml

  if markdown:
    print(f"|{nthreads}|{lor}|{mean(no_dmls):.2f}|{stdev(no_dmls):.2f}|{mean(with_dmls):.2f}|{stdev(with_dmls):.2f}|{diff:.2f}|{ratio:.3f}|")
  elif speedup:
    print(f"{lowr}-{highr},{nthreads},{ratio:.3f}")
  else:
    print(f"{nthreads},{lor},{mean(no_dmls):.2f},{stdev(no_dmls):.2f},{mean(with_dmls):.2f},{stdev(with_dmls):.2f},{diff:.2f},{ratio:.3f}")

def analyze(filename, markdown, speedup):
  for d in DSA_CONFIG:
    dt = d.split("-")
    print(f"\"DSA Config -- {dt[0]} node {dt[1]} dsa each\"")

    if markdown:
      print("|threads|lohar|no-dml (s)|no-dml (stddev)|with-dml (s)|with-dml (stddev)|diff (s)|speedup|")
      print("|-------|-----|----------|---------------|------------|-----------------|--------|-------|")
    elif speedup:
      print("cat,threads,speedup")
    else:
      print("threads,lohar,no-dml (s),no-dml (stddev),with-dml (s),with-dml (stddev),diff (s),speedup")



    for n in NTHREADS:
      for lor in LOHAR:
        analyze_case(filename, n, lor, LOWR, HIGHR, d, markdown, speedup)
    print("")

def graph(filename):
  pd = pandas.read_csv(filename, sep=",")
  pd = pd[["threads", "lohar", "speedup"]]
  pd = pd.pivot(index="lohar", columns="threads", values="speedup")
  plt = pd.plot(style='.-', figsize=(6, 4))
  plt.set_xlabel("LOHAR Ratio (Out of 1000)")
  plt.set_ylabel("Speedup (No DSA vs DSA)")
  fig = plt.get_figure()
  fig.savefig('plot.png')

def graph2(filename):
  df = pandas.read_csv(filename, sep=",")
  df_no_dml = df[["threads", "lohar", "no-dml"]].copy()
  df_with_dml = df[["threads", "lohar", "with-dml"]].copy()

  df_no_dml['threads'] = df_no_dml['threads'].apply(lambda x: "{}{}".format(x, '-no-dml'))
  df_with_dml['threads'] = df_with_dml['threads'].apply(lambda x: "{}{}".format(x, '-with-dml'))
  df_no_dml = df_no_dml.rename(columns={"no-dml": "time"})
  df_with_dml = df_with_dml.rename(columns={"with-dml": "time"})

  full_df = pandas.concat([df_no_dml, df_with_dml])

  full_df = full_df.pivot(index="lohar", columns="threads", values="time")
  plt = full_df.plot(style='.-', figsize=(6, 4))
  plt.set_xlabel("LOHAR Ratio (Out of 1000)")
  plt.set_ylabel("Time (No DSA vs DSA)")
  fig = plt.get_figure()
  fig.savefig('plot-2.png')

def main(args):
  if not args.filename:
    print("error: supply path of dir to analyze")
    exit(1)

  if args.graph:
    graph(args.filename)
  elif args.graph2:
    graph2(args.filename)
  else:
    analyze(args.filename, args.markdown, args.speedup)




if __name__ == "__main__":
  parser = argparse.ArgumentParser()

  parser.add_argument("-f", '--filename', action='store')
  parser.add_argument("-m", '--markdown', action='store_true')
  parser.add_argument("-g", '--graph', action='store_true')
  parser.add_argument("-g2", '--graph2', action='store_true')
  parser.add_argument("-s", '--speedup', action='store_true')

  args = parser.parse_args()

  main(args)
