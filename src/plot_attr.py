# plot_attr.py
""" Plotting attributes 
"""

class PlotAttr:
    ib_marker_def = '.'
    ib_label_def = 'ev_in'
    ib_color_def = 'purple'
    ob_marker_def = 'x'
    ob_label_def = 'ev_in'
    ob_color_def = 'red'
    
    def __init__(self, mtype,
            ib_marker=None, ib_label=None, ib_color=None,
            ob_marker=None, ob_label=None, ob_color=None,
            ms_high=None, ms_low=None
            ):
        """ Setup measurement plotting attributes
        :mtype: measurment type/id
        :ib_marker: inbounds marker default: ib_marker_def
        :ib_label: inbounds label default: ib_label_def
        :ib_color: inbounds color default: ib_color_def
        :ob_marker: outbounds marker default: ob_marker_def
        :ob_label: outbounds label default: ob_label_def
        :ob_color: outbounds color default: ob_color_def
        :ms_low: measurement lower bounds default: no checking
        :ms_high: measurement high bounds default: no checking
        """
        self.mtype = mtype
        self.ib_marker = ib_marker
        self.ib_label = ib_label
        self.ib_color = ib_color
        
        self.ob_marker = ob_marker
        self.ob_label = ob_label
        self.ob_color = ob_color
        self.ms_low = ms_low
        self.ms_high = ms_high
