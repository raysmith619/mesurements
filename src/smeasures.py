#smeasures.py    27Sep2020  crs, moved from measure_plotting.py
""" Colecting and processing measurements
"""
from select_trace import SlTrace
import statistics
from _datetime import date
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

from select_error import SelectError

from smeasure import Smeasure
from plot_attr import PlotAttr
        
class Smeasures:
    """ Measurement database
    """
    # measurement type for known groups
    sg_mtypes = ["sg_m", "sg_e"]
    bp_mtypes = ["bp_hi", "bp_low", "pl"]
    
    def __init__(self):
        self.plot_attrs = {}        # Plotting attributes
        self.measurements = []      # List of Smeasure
        self.horz_label = ""
        self.vert_label = ""
        myFmt = mdates.DateFormatter('%b %d')
        self.figure = plt.figure()
        subplot = self.figure.add_subplot(111)
        subplot.xaxis.set_major_formatter(myFmt)

        self.add_plot_attr(
            PlotAttr("DEFAULT", ib_marker='.', ib_label='in', ib_color='blue',
                    ob_marker='x', ob_label='out', ob_color='pink',
                    ms_low=80, ms_high=120))

    def add_datas(self, data_type, datas=None,
                   month_str=None, day_str=None, year_str=None):
        """ Add data line measurements
        :data_type: type of data: "sg" sugar meas, "bp" blood preasure,pulse
        :data: one or list of measurements strings ? - use previous meas
        :month_str: month string e.g. Jan, January, jan
        :day_str: day of month
        :year_str: year
        """
        meas_date = self.set_date(month_str=month_str,
                                 day_str=day_str, year_str=year_str)
        if not isinstance(datas,(list,set)):
            datas = [datas]     # List of one
        if data_type == "sg":
            for i,data in enumerate(datas):
                if data == "?":
                    continue            # No data
                sm = Smeasure(date=meas_date, mtype=self.sg_mtypes[i],
                              value=int(data))
                self.add_meas(sm)
        elif data_type == "bp":
            for i,data in enumerate(datas):
                if data == "?":
                    continue            # No data
                sm = Smeasure(date=meas_date, mtype=self.bp_mtypes[i],
                              value=int(data))
                self.add_meas(sm)
        else:
            raise SelectError(f"Unrecognized data type:{data_type}")

    def add_meas(self, meas):
        """ Add measurement
        :meas: measurement(Smeasure) to add
        """
        self.measurements.append(meas)
                    
    def add_plot_attr(self, plot_attr):
        """ Add / modify ploting attributes for mtype
        :mtype: measurement type/id
        :plot_attr: plotting attributes
        """
        mtype = plot_attr.mtype
        if mtype in self.plot_attrs:
            pattr = self.plot_attrs[mtype]
            for att in plot_attr:
                setattr(pattr, att)
        else:
            self.plot_attrs[mtype] = plot_attr

    def get_limit_high(self, mtype):
        """ Get high limit, for mtype, if any
        :mtype: measurement type
        :returns: limit None if no limit
        """
        if mtype in self.plot_attrs:
            return self.plot_attrs[mtype].ms_high

    def get_limit_low(self, mtype):
        """ Get low limit, for mtype, if any
        :mtype: measurement type
        :returns: limit None if no limit
        """
        if mtype in self.plot_attrs:
            return self.plot_attrs[mtype].ms_low

        return None     # No high limit


    def get_meas(self, mtypes=None, date_sorted=True):
        """ Return measurements for types
        :mtypes: one, list of mtypes
                :default: all types
        :date_sorted: True -->sorted by ascending date
        """
        if mtypes is None:
            mtypes is self.get_mtypes()
        if not isinstance(mtypes, (set,list)):
            mtypes = [mtypes]
        measurements = []
        for measurement in self.measurements:
            for mtype in mtypes:
                if mtype == measurement.mtype:
                    measurements.append(measurement)
        if date_sorted:
            measurements.sort(key=lambda meas : meas.date)
        return measurements

    def get_meas_vals(self, mtypes=None, date_sorted=True):
        """ Get list of measurement values
        :mtypes: one, list of types
                default: all types
        :returns: list of values
        :date_sorted: True -->sorted by ascending date
        """
        measurements = self.get_meas(mtypes=mtypes, date_sorted=date_sorted)
        vals = [meas.value for meas in measurements]
        return vals
    
    def get_mtypes(self):
        """ Return set of mtypes encountered in measurement list
        """
        mtypes = set()
        for measurement in self.measurements:
            mtypes.add(measurement.mtype)
        return mtypes
        
    def get_nday(self):
        """ Get number of days measured
        """
        days = set()
        for measurement in self.measurements:
            days.add(measurement.date)
        return len(days)

    def get_plot_attr(self, mtype):
        """ Get plotting attribute for this mtype
        If we don't have this type DEFAULT attribute
        is returned.
        :mtype: measurement type
        :returns: PlotAttr instance
        """
        if mtype not in self.plot_attrs:
            mtype = "DEFAULT"
        return self.plot_attrs[mtype]
    
    def get_ib_marker(self, mtype):
        plot_attr = self.get_plot_attr(mtype)
        return plot_attr.ib_marker
    
    def get_ib_label(self, mtype):
        plot_attr = self.get_plot_attr(mtype)
        return plot_attr.ib_label
    
    def get_ib_color(self, mtype):
        plot_attr = self.get_plot_attr(mtype)
        return plot_attr.ib_color
    
    def get_ob_marker(self, mtype):
        plot_attr = self.get_plot_attr(mtype)
        return plot_attr.ob_marker
    
    def get_ob_label(self, mtype):
        plot_attr = self.get_plot_attr(mtype)
        return plot_attr.ob_label
    
    def get_ob_color(self, mtype):
        plot_attr = self.get_plot_attr(mtype)
        return plot_attr.ob_color
            
    def list_stats(self):
        """ List stats for each measurement type (mtype)
        """
        nday = self.get_nday()
        SlTrace.lg(f"Number of days: {nday}")
        
        mtypes = self.get_mtypes()
        for mtype in mtypes:
            self.list_stat(mtype)
    
    def list_stat(self, mtype):
        """ List statistics for given measurement type
        :mtype: one measurement type
        """
        m_vals = self.get_meas_vals(mtype)
        nmeas = len(m_vals)
        if nmeas == 0:
            return          # No values
        
        m_low = min(m_vals)
        m_high = max(m_vals)
        m_avg = sum(m_vals)/nmeas
        m_median = statistics.median(m_vals)
        SlTrace.lg(f"{mtype:6} low: {m_low:3}   high: {m_high:3}"
                   f"   avg: {m_avg:5.1f}   median: {m_median:5.1f}")

    def add_plot(self, mtype, date_axis=False):
        """ add measurements of mtype to plot
        :mtype: type to add
        :date_axis: True -> show date on x axis
        """
        mes = self.get_meas(mtype)
        if date_axis:
            me_dates = self.get_meas_dates(mtype)
        else:
            me_dates = self.get_meas_days(mtype)
        ms_hi = self.get_limit_high(mtype)
        ms_low = self.get_limit_low(mtype)
        ms_ob = []  # values
        ms_ob_dates = []  # days/dates
        ms_ib = []  # values
        ms_ib_dates = []  # days/dates
        for me, me_date in zip(mes, me_dates):
            me_val = me.value
            if (ms_hi is not None and me_val > ms_hi 
                    or ms_low is not None and me_val < ms_low):
                ms_ob.append(me_val)
                ms_ob_dates.append(me_date)
            else:
                ms_ib.append(me_val)
                ms_ib_dates.append(me_date)
        if ms_low is not None:
            plt.plot(me_dates, len(me_dates)*[ms_low], c='gray')
        if ms_hi is not None:
            plt.plot(me_dates, len(me_dates)*[ms_hi], c='gray')
        plt.scatter(ms_ib_dates, ms_ib,
                    marker=self.get_ib_marker(mtype),
                    label=self.get_ib_label(mtype),
                     c=self.get_ib_color(mtype))
        if ms_low is not None or ms_hi is not None:
            plt.scatter(ms_ob_dates, ms_ob,
                        marker=self.get_ob_marker(mtype),
                        label=self.get_ob_label(mtype),
                         c=self.get_ob_color(mtype))
        
    def add_plots(self, mtypes=None, date_axis=False):
        """ Add plot for mtypes
           :mtypes: type/list of types to add
        """
        if mtypes is None:
            mtypes = self.get_mtypes()
        if not isinstance(mtypes, (list,set)):
            mtypes = [mtypes]
        for mtype in mtypes:
            self.add_plot(mtype, date_axis=date_axis)

    def show_plots(self, date_axis=False):
        """ Show plots added via add_plots
        """
        if self.horz_label is not None:
            plt.xlabel(self.horz_label)
        if self.vert_label is not None:
            plt.ylabel(self.vert_label)
        plt.legend()    
        plt.show()
        
    def get_meas_dates(self, mtypes):
        """ Returns list of dates of
        measurements for this mtype(s)
        :mtype: measurement type(s) single, list
                    defalt: all types
        """
        if mtypes is None:
            mtypes = self.get_mtypes()
        if not isinstance(mtypes, (list,set)):
            mtypes = [mtypes]
        m_type_dates = set()
        for measurement in self.measurements:
            for mtype in mtypes:
                if measurement.mtype == mtype:
                    m_type_dates.add(measurement.date)
        dates = list(m_type_dates)
        dates.sort()
        return dates    
        
    def get_meas_days(self, mtypes):
        """ Returns list of integers 1..number of days of
        measurements for this mtype(s)
        :mtype: measurement type(s) single, list
                    defalt: all types
        """
        if mtypes is None:
            mtypes = self.get_mtypes()
        if not isinstance(mtypes, (list,set)):
            mtypes = [mtypes]
        m_type_dates = set()
        for measurement in self.measurements:
            for mtype in mtypes:
                if measurement.mtype == mtype:
                    m_type_dates.add(measurement.date)
        dates = list(m_type_dates)
        dates.sort()
        day_nos = []
        date_start = dates[0]
        for date in dates:
            delta = date-date_start
            day_nos.append(delta.days+1)
        return day_nos    

    def set_date(self, month_str=None,
                    day_str=None, year_str=None):
        """ Convert date component strings to date
        :month_str: month string e.g jan, Jan, January
        :day_str: day string 1-31
        :year_str:  year string if < 20 add "2000"
        :returns: date object
        """
        month = self.set_date_month(month_str)
        day = int(day_str)
        year = int(year_str)
        if year <= 20:
            year += 2000
        return date(year=year, month=month, day=day)
    
    def set_date_month(self, month_str):
        """ Returns month number 1-12, guess
        :month_str: month string e.g jan, Jan, January
        """
        import calendar
        for n in range(1,12+1):
            abbr = calendar.month_abbr[n]
            if month_str[:len(abbr)].lower() == abbr.lower():
                return n 
        
        return 0    

    def set_horz_label(self, label):
        self.horz_label = label

    def set_vert_label(self, label):
        self.vert_label = label
        