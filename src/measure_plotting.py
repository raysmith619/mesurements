# measure_plotting.py   26Sep2020, from sugar_plotting.py
"""
Measurement Tracking / Plotting program
Data file format:
    Comment: # to end of line
    Year: ^\s*\d\d\d\d
    Date: ^\s*(\w+)\s+(\d+),?\s+(\d+) ==> month, day,  year
          ^\s*(\d+)\s*([a-z]\w+)  => day, mth
    sugar data: (\?|\d+)\s+(\?|\d+)
    blood pessure, pulse: (\d+)/(\d+)/(\d+)
            With preprocessing: \s*;?\s*Pulse:?\s* ==> /
Examples:
26 July 109 231
17 Aug 110 149
--
Jen's BP
September 16, 2020
145/95 pulse: 80
46/96/85

month day_of_month, year
high_bp/low_bp pulse: pulse
high_bp/low_bp/pulse

day of month: \d{1,2}
month: [a-z]{3,}
morning value: \d{2,3}
eavining: \d{2,3}
comments: #....
Ignore anything else
"""
import os
import glob
import re
from datetime import date
import argparse

import statistics
from matplotlib import pyplot as plt

from select_trace import SlTrace
from select_error import SelectError
from crs_funs import str2bool, str2val
from smeasure import Smeasure
from smeasures import Smeasures, PlotAttr

data_files = ["sugar_01.data", "sugar_02.data"]
morning_low = None      # low moring value
morning_high = None     # high morning value
morning_sum = 0         # Sum of morning values
evening_low = None      # low evening value
evening_high = None     # high evening value
evening_sum = 0         # Sum of evening values
data_count = 0          # Count of measured days

who = "dad"

list_input = False
list_data = False
data_dir = "../data"
date_axis=True
trace = ""
parser = argparse.ArgumentParser()
parser.add_argument('--list_data', type=str2bool, dest='list_data', default=list_data)
parser.add_argument('--list_input', type=str2bool, dest='list_input', default=list_input)
parser.add_argument('--date_axis', type=str2bool, dest='date_axis', default=date_axis)
parser.add_argument('--trace', dest='trace', default=trace)
parser.add_argument('--data_dir', dest='data_dir', default=data_dir)
parser.add_argument('--who', dest='who', default=who)
args = parser.parse_args()             # or die "Illegal options"
SlTrace.lg("args: %s\n" % args)
data_dir = args.data_dir
date_axis = args.date_axis
list_input= args.list_input
list_data = args.list_data
trace = args.trace
who = args.who
if trace:
    SlTrace.setFlags(trace)

if who.lower() == "jenifer"[:len(who)]:
    data_dir = "../data/jen"
    data_files = [
        "bp_1.data",
        "bp_2.data"]
else:
    data_dir = "..\\data"
    data_files = []
    data_path = os.path.join(data_dir, "*.data")
    for file in glob.glob(data_path):
        data_files.append(file)
    data_files_str = '\n\t'.join(data_files)
SlTrace.lg(f"Data files:\n\t{data_files_str}")    
        
smeas = Smeasures()
year_str = None
smeas.set_vert_label("Measurements")
if date_axis:
    smeas.set_horz_label("Measurement Date")
else:
    smeas.set_horz_label("Day Number")

"""
Setup default measurement plotting attributes
"""
smeas.add_plot_attr(
            PlotAttr("sg_m", ib_marker='*', ib_label='morning in', ib_color='green',
                    ob_marker='^', ob_label='morning out', ob_color='pink',
                    ms_low=80, ms_high=120))
smeas.add_plot_attr( 
            PlotAttr("sg_e",ib_marker='.', ib_label='evening in', ib_color='blue',
                    ob_marker='x', ob_label='evening out', ob_color='red',
                    ms_low=80, ms_high=150))

smeas.add_plot_attr(
            PlotAttr("bp_low", ib_marker='v', ib_label='BP low', ib_color='blue',
                    ob_marker='x', ob_label='bp_low out', ob_color='pink',
                    ms_low=None, ms_high=None))

smeas.add_plot_attr(
            PlotAttr("bp_hi", ib_marker='^', ib_label='BP high', ib_color='blue',
                    ob_marker='x', ob_label='bp_hi out', ob_color='pink',
                    ms_low=None, ms_high=None))

smeas.add_plot_attr(
            PlotAttr("pl", ib_marker='+', ib_label='pulse', ib_color='green',
                    ob_marker='x', ob_label='pl out', ob_color='pink',
                    ms_low=None, ms_high=None))

def collect_file(file_name, meas=None):
    """ Collect file and add to measures
    :file_name:  file to process
    :meas: measurement data base
            default: smeas
    """
    global year_str
    
    if meas is None:
        meas = smeas
        
    comment_pat = re.compile(r"^(.*)#.*")
    blank_line_pat = re.compile(r'\s*$')
    line_pat = re.compile(r"^\s*(\d\d)\s+([a-z]+)"
                          r"\s+(\S+)\s+(\d+)",
                          re.I)
    if year_str is None:
        year_str = "2020"   # TBD - current year
    line_no = 0
    with open(file_name) as finp:
        base_name = os.path.basename(file_name)
        for line in finp:
            line = line.rstrip()    # Remove white space esp newline
            line_no += 1
            if list_input:
                SlTrace.lg(f"{base_name}:{line_no:4}:  {line}")
            res = re.match(r"^(.*)#", line)
            if res:
                line = res.group(1)
            res = re.match(r"^(.*)\s+$", line)    # Remove trailing white space
            if res:
                line = res.group(1)
            res = re.match(r"^\s+(.*)$", line)    # Remove leading white space
            if res:
                line = res.group(1)
            res = re.match(r"^\s*$", line)
            if res:
                continue                            # Ignore blank lines

            # Check for date component
            res = re.match(r"^(\d+)$", line)   # year on line
            if res:
                year_str = res.group(1)
                continue
            
            res = re.match(r"^(\d+)\s*(\w+)", line) # day month beginning line
                                                    # dd mmm or ddmmm
            if res:
                month_str = res.group(2)
                day_str = res.group(1)
                line = line[len(res.group(0)):]     # rest of line
            else:
                res = re.match(r"^(\w+)\s+(\d+)\s*,\s*(\d+)\s*$", line)   # July 4, 1776
                if res:
                    month_str = res.group(1)
                    day_str = res.group(2)
                    year_str = res.group(3)
                    line = line[len(res.group(0)):]     # rest of line
            
            # Check for data on line    
            res = re.match(r"^\s*(\?|night|\d+)\s+(\?|\d+)", line) # sg_m, sg_e
            if res:
                sg_m_str = res.group(1)
                sg_e_str = res.group(2)
                if sg_m_str == "night":
                    sg_m_str = "?"
                meas.add_datas("sg", datas=[sg_m_str, sg_e_str], month_str=month_str,
                             day_str=day_str,
                             year_str=year_str)
                continue
            line = re.sub(r"\s*;?\s*Pulse:?\s*", "/", line,flags=re.I)
            res = re.match(r"^(\?|\d+)/(\?|\d+)/(\?|\d+)", line) # bp_h, bp_l, pl
            if res:
                bp_hi_str = res.group(1)
                bp_lo_str = res.group(2)
                pl_str = res.group(3)
                meas.add_datas("bp", datas=[bp_hi_str, bp_lo_str, pl_str],
                          month_str=month_str,
                          day_str=day_str,
                          year_str=year_str)
                continue

for file_name in data_files:
    if not os.path.isabs(file_name):
            fn = os.path.join(data_dir, file_name)
            if not os.path.exists(fn):
                abs_path = os.path.abspath(fn)
                raise SelectError(f"{fn} was not found"
                                  f" ({abs_path})")
                                
    collect_file(fn, smeas)

smeas.list_stats()
smeas.add_plots(date_axis=date_axis)
smeas.show_plots(date_axis=date_axis)

