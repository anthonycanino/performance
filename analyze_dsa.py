#!/usr/bin/python3
import os

NTHREADS = [1, 2, 4, 8]
DSA_CONFIG = ["1-1", "1-2", "1-4", "2-1", "2-2", "2-4"]
LOWR = 2000000
HIGHR = 2000000
NRUNS = 1

def read_run(path):
  with open(path, "r") as f:
    l = f.readline()
    l = f.readline().split(" ")[1][:-3]
    return float(l)/1000.0

def analyze_case(nthreads, lowr, highr, dsa_config):
  path = os.path.join("dml", f"with-dml-{lowr}-{highr}-{nthreads}-{dsa_config}")
  with_dml = 0.0
  for i in range(1, NRUNS+1):
    fpath = os.path.join(path, f"run-{i}.txt")
    with_dml += read_run(fpath)

  with_dml /= NRUNS 

  path = os.path.join("dml", f"no-dml-{lowr}-{highr}-{nthreads}-{dsa_config}")
  no_dml = 0.0
  for i in range(1, NRUNS+1):
    fpath = os.path.join(path, f"run-{i}.txt")
    no_dml += read_run(fpath)

  no_dml /= NRUNS 
  diff = no_dml - with_dml
  ratio = no_dml / with_dml

  print(f"{nthreads},{no_dml:.2f},{with_dml:.2f},{diff:.2f},{ratio:.3f}")

def analyze():
  for d in DSA_CONFIG:
    dt = d.split("-")
    print(f"\"DSA Config -- {dt[0]} node {dt[1]} dsa each\"")
    print("threads,no-dml (s),with-dml (s),diff (s),speedup")
    for n in NTHREADS:
      analyze_case(n, LOWR, HIGHR, d)
    print("")

def main():
  analyze()




if __name__ == "__main__":
  main()
