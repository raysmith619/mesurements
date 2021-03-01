#smeasure.py
""" Generalized measurement
"""
from select_trace import SlTrace

class Smeasure:
    def __init__(self, date=None,
               mtype=None,
               value=None):
        self.date = date    # string ddmmmyyyy
        self.mtype = mtype    # 'm'- morning, 'e'-evening
        self.value = value
        SlTrace.lg(f"Smeasure: mtype: {mtype}  value: {value} date: {date}",
                   "meas")
