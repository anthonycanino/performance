#!/usr/bin/python3
import os
import argparse

# Crude mapping of event/event category to stat

EVENTS={
  "/event=0x2,event_category=0x1/": "writes_bytes",

  "/event=0x1,event_category=0x2/": "address_translations_no_page_fault",
  "/event=0x2,event_category=0x2/": "address_translations_with_page_fault",

  "/event=0x10,event_category=0x3/": "memory_clear_operations",
  "/event=0x10,event_category=0x4/": "successful_descriptor_completions",
  "/event=0x8,event_category=0x4/": "error_descriptor_completions",
}

ACTIVE_DSAS=[
  "dsa0",
  "dsa8"
]

def print_perf_events():
  perf_string = ""
  for d in ACTIVE_DSAS:
    for e in EVENTS:
      perf_string += f"{d}{e},"
  print(perf_string[:-1])

GB1 = 1024 * 1024 * 1024

class DSAInfo:

  def __init__(self, active_dsas, event_list):
    self.dsas = {}

    for d in active_dsas:
      self.dsas[d] = {}

    for dsa in self.dsas:
      for eid, ename in event_list.items():
        self.dsas[dsa][ename] = EventInfo(eid, ename)

  def add_event(self, event):
    self.dsas[event.dsa][event.name].add_event(event)

  def to_csv(self):
    print(f"dsa,event,peak,total,average,count")
    for dsa, einfos in self.dsas.items():
      for name, einfo in einfos.items():
        print(f"{dsa},{einfo.to_csv()}")

class EventInfo:

  def __init__(self, id, name):
    self.id    = id
    self.name  = name
    self.peak_samples  = 0
    self.sum_samples   = 0
    self.event_count   = 0

  def add_event(self, event):
    assert(self.name == event.name)

    if event.samples > self.peak_samples:
      self.peak_samples = event.samples
    self.sum_samples += event.samples
    self.event_count += 1

  def to_csv(self):
    self.average_samples = 0
    if self.event_count:
      self.average_samples = self.sum_samples / self.event_count
    return f"{self.name},{self.peak_samples},{self.sum_samples},{self.average_samples},{self.event_count}"

class Event:
  def __init__(self, toks):
    self.samples = int(toks[1].replace(",",""))
    ind = toks[2].find("/")
    self.dsa  = toks[2][:ind]
    self.id = toks[2][ind:]

    self.name = EVENTS[self.id]

    # Special case, write_32bytes needs to be expanded
    if self.name == "writes_bytes":
      self.samples *= 32
      self.samples /= GB1


def parse_events(filename):
  dsa_info = DSAInfo(ACTIVE_DSAS, EVENTS)

  with open(filename, "r") as f:
    for _ in range(3):
      next(f)

    for line in f:
      toks = line.split()
      if toks[0] == '#':
        continue

      event = Event(toks)
      if event.samples == 0:
        continue

      dsa_info.add_event(event)

  return dsa_info

def main(args):
  if args.perf:
    print_perf_events()
    return

  dsa_info = parse_events(args.filename)

  dsa_info.to_csv()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()

  parser.add_argument("-p", '--perf', action='store_true')
  parser.add_argument("-f", '--filename', action='store')

  args = parser.parse_args()

  main(args)