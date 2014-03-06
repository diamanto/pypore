#!/usr/bin/env python
# -*- coding: utf8 -*-

"""

This program is for finding events in files and displaying the results.
"""
import sys
import os

from PySide import QtCore, QtGui  # Must import PySide stuff before pyqtgraph so pyqtgraph knows
# to use PySide instead of PyQt

# The rest of the imports can be found below in _longImports


def _long_imports(**kwargs):
    """
    Loads imports and updates the splash screen with information.
    """
    # append the src directory to the PYTHONPATH, i.e. '../../' = 'src/'
    src_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if not src_dir in sys.path:
        sys.path.append(src_dir)

    global AnalyzeDataThread, PlotThread, pg, pgc, LayoutWidget, linspace, np, \
            EventAnalysisWidget, ed, EventFindingTab, EventViewingTab, EventAnalysisTab

    update_splash = False
    if 'splash' in kwargs and 'app' in kwargs:
        update_splash = True
        splash = kwargs['splash']
        app = kwargs['app']

    if update_splash:
        splash.showMessage("Importing PyQtGraph...", alignment=QtCore.Qt.AlignBottom)
        app.processEvents()
    import pyqtgraph as pg
    import pyqtgraph.console as pgc
    from pyqtgraph.widgets.LayoutWidget import LayoutWidget

    if update_splash:
        splash.showMessage("Importing SciPy...", alignment=QtCore.Qt.AlignBottom)
        app.processEvents()
    from scipy import linspace

    if update_splash:
        splash.showMessage("Importing NumPy...", alignment=QtCore.Qt.AlignBottom)
        app.processEvents()
    import numpy as np

    # My stuff
    if update_splash:
        splash.showMessage("Setting up Cython imports...", alignment=QtCore.Qt.AlignBottom)
        app.processEvents()
    from pypore import cythonsetup

    if update_splash:
        splash.showMessage("Compiling Cython imports... DataFileOpener", alignment=QtCore.Qt.AlignBottom)
        app.processEvents()
    from widgets.event_viewing_tab import EventViewingTab
    from widgets.event_analysis_tab import EventAnalysisTab
    from widgets.event_finding_tab import EventFindingTab

    if update_splash:
        splash.showMessage("Compiling Cython imports... EventFinder", alignment=QtCore.Qt.AlignBottom)
        app.processEvents()
    from my_threads import AnalyzeDataThread, PlotThread

    if update_splash:
        splash.showMessage("Importing Event Database", alignment=QtCore.Qt.AlignBottom)
        app.processEvents()
    import pypore.filetypes.event_database as ed


class MyMainWindow(QtGui.QMainWindow):
    def __init__(self, app, parent=None):
        super(MyMainWindow, self).__init__()

        self.events = []  # holds the events from the most recent analysis run
        self.app = app

        pg.setConfigOption('leftButtonPan', False)

        self.open_dir = '../../data'

        self.thread_pool = []

        self.setWindowTitle('Translocation Event Analysis')

        self.create_menu()
        self._create_main_frame()
        self.create_status_bar()

    def open_files(self):
        """
        Opens file dialog box, adds names of files to open to list
        """
        file_names = QtGui.QFileDialog.getOpenFileNames(self,
                                                        'Open data file',
                                                        self.open_dir,
                                                        "All types(*.h5 *.hkd *.log *.mat);;"
                                                        "Pypore data files *.h5(*.h5);;"
                                                        "Heka files *.hkd(*.hkd);;"
                                                        "Chimera files *.log(*.log);;"
                                                        "Gabys files *.mat(*.mat)")[0]
        if len(file_names) > 0:
            self.event_finding_tab.open_files(file_names)

    def open_event_database(self):
        """
        Opens file dialog box, add names of event database files to open list
        """
        file_names = QtGui.QFileDialog.getOpenFileNames(self, 'Open event database', self.open_dir, '*.h5')[0]

        if len(file_names) > 0:
            self.event_viewer_tab.open_event_database(file_names)
            self.event_analysis_tab.open_event_database(file_names)

    def set_status(self, text):
        """
        Sets the status text.

        :param StringType text: Text to display in the status bar.
        """
        self.status_text.setText(text)

    def _process_events(self):
        self.app.processEvents()

    def _create_main_frame(self):
        """
        Helper to initialize the main gui frame.
        """
        self.event_finding_tab = EventFindingTab(self)
        self.event_finding_tab.set_on_status_update_callback(self.set_status)
        self.event_finding_tab.set_process_events_callback(self._process_events)

        self.event_viewer_tab = EventViewingTab(self)

        self.event_analysis_tab = EventAnalysisTab(self)

        # Layout holding everything        
        self.main_tabwig = QtGui.QTabWidget()
        self.main_tabwig.addTab(self.event_finding_tab, 'Event Finding')
        self.main_tabwig.addTab(self.event_viewer_tab, 'Event View')
        self.main_tabwig.addTab(self.event_analysis_tab, 'Event Analysis')
        self.main_tabwig.setMinimumSize(1000, 550)

        text = """*********************
Welcome to pyporegui!

If you are unfamiliar with the python console, feel free to ignore this console.

However, you can use this console to interact with your data and the gui!
Type globals() to see globally defined variabels.
Type locals() to see application-specific variables.

The current namespace should include:
    np        -    numpy
    pg        -    pyqtgraph
    ed        -    pypore.eventDatabase
    currentPlot -  Top plot in the event finding tab.
*********************"""

        namespace = {'np': np, 'pg': pg, 'ed': ed, 'currentPlot': self.event_finding_tab.plot_widget}
        self.console = pgc.ConsoleWidget(namespace=namespace, text=text)

        frame = QtGui.QSplitter()
        frame.setOrientation(QtCore.Qt.Vertical)
        frame.addWidget(self.main_tabwig)
        frame.addWidget(self.console)

        self.setCentralWidget(frame)

    def create_status_bar(self):
        """
        Creates filter_parameter status bar with filter_parameter text widget.
        """
        self.status_text = QtGui.QLabel("")
        self.statusBar().addWidget(self.status_text, 1)

    def create_menu(self):
        """
        Creates File menu with Open
        """
        self.file_menu = self.menuBar().addMenu("&File")

        load_data_file_action = self.create_action("&Open Data File",
                                                   shortcut="Ctrl+O", slot=self.open_files,
                                                   tip="Open data Files")
        load_events_database_action = self.create_action("&Open Events Database",
                                                         shortcut="Ctrl+E", slot=self.open_event_database,
                                                         tip="Open Events Database")
        quit_action = self.create_action("&Quit", slot=self.close,
                                         shortcut="Ctrl+Q", tip="Close the application")

        self.add_actions(self.file_menu,
                         (load_data_file_action, load_events_database_action, None, quit_action))

    #         self.help_menu = self.menuBar().addMenu("&Help")
    #         about_action = self.create_action("&About",
    #             shortcut='F1', slot=self.on_about,
    #             tip='About the demo')
    #
    #         self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(self, text, slot=None, shortcut=None,
                      icon=None, tip=None, checkable=False,
                      signal="triggered()"):
        action = QtGui.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, QtCore.SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def plotData(self, plot_options):
        '''
        Plots waveform in datadict
        Pass in plot_options, filter_parameter dictionary with 'plot_range', 'axes', and 'datadict'
        pass in Data dictionary, with data at 'data' and sample rate at 'SETUP_ADCSAMPLERATE'
        Can pass in range as [start,stop], or 'all' for 0:n
        '''
        axes = plot_options['axes']
        if axes is None:
            axes = self.plot
        # Read the first file, store data in dictionary
        data = plot_options['datadict']['data'][0]
        sample_rate = plot_options['datadict']['sample_rate']
        plot_range = plot_options['plot_range']

        n = len(data)
        # If problem with input, just plot all the data
        if plot_range == 'all' or len(plot_range) != 2 or plot_range[1] <= plot_range[0]:
            plot_range = [0, n]
        else:  # no problems!
            n = plot_range[1] - plot_range[0] + 1

        Ts = 1 / sample_rate

        times = linspace(Ts * plot_range[0], Ts * plot_range[1], n)
        yData = data[plot_range[0]:(plot_range[1] + 1)]

        self.plotwid.clear_event_items()
        self.p1.setData(x=times, y=yData)
        self.plotwid.autoRange()
        self.app.processEvents()

    # def addEventsToConcatEventPlot(self, events):
    #     if len(events) < 1:
    #         return
    #     size = 0
    #     for event in events:
    #         size += event['raw_data'].size
    #     data = np.empty(size)
    #     sample_rate = events[0]['sample_rate']
    #     ts = 1 / sample_rate
    #     times = np.linspace(0., (size - 1) * ts, size) + self.prev_concat_time
    #     self.prev_concat_time += size * ts
    #     index = 0
    #     for event in events:
    #         d = event['raw_data'].size
    #         baseline = event['baseline']
    #         data[index:index + d] = (event['raw_data'] - baseline)
    #         index += d
    #
    #     item = PathItem(times, data)
    #     item.setPen(pg.mkPen('w'))
    #     self.plot_concatevents.addItem(item)

    def getEventAndLevelsData(self, event):
        data = event['raw_data']
        levels_index = event['cusum_indexes']
        levels_values = event['cusum_values']
        sample_rate = event['sample_rate']
        event_start = event['event_start']
        event_end = event['event_end']
        baseline = event['baseline']
        raw_points_per_side = event['raw_points_per_side']

        Ts = 1 / sample_rate

        n = data.size

        times = linspace(Ts * (event_start - raw_points_per_side), Ts * (event_start - raw_points_per_side + n - 1), n)
        times2 = [(event_start - raw_points_per_side) * Ts, (event_start - 1) * Ts]
        levels2 = [baseline, baseline]
        for i, level_value in enumerate(levels_values):
            times2.append(levels_index[i] * Ts)
            levels2.append(level_value)
            if i < len(levels_values) - 1:
                times2.append((levels_index[i + 1] - 1) * Ts)
                levels2.append(level_value)
        times2.append(event_end * Ts)
        levels2.append(levels_values[len(levels_values) - 1])
        times2.append((event_end + 1) * Ts)
        levels2.append(baseline)
        times2.append((event_end + raw_points_per_side) * Ts)
        levels2.append(baseline)
        return times, data, times2, levels2

    # def plotEventsOnMainPlot(self, events):
    #     if len(events) < 1:
    #         return
    #     size = 0
    #     for event in events:
    #         size += event['raw_data'].size
    #     data = np.empty(size)
    #     sample_rate = events[0]['sample_rate']
    #     raw_points_per_side = events[0]['raw_points_per_side']
    #     ts = 1 / sample_rate
    #     times = np.empty(size)
    #     conn = np.ones(size)
    #     index = 0
    #     for event in events:
    #         event_start = event['event_start']
    #         event_data = event['raw_data']
    #         d = event_data.size
    #         times[index:index + d] = linspace(ts * (event_start - raw_points_per_side),
    #                                           ts * (event_start - raw_points_per_side + d - 1), d)
    #         data[index:index + d] = event_data
    #         conn[index - 1] = False  # disconnect separate events
    #         index += d
    #
    #     item = PathItem(times, data, conn)
    #     item.setPen(pg.mkPen('y'))
    #     self.plotwid.add_event_item(item)

    def get_current_analysis_parameters(self):
        '''
        Returns filter_parameter dictionary holding the current analysis parameters set by the user.  Returns an entry 'error' if there were
        invalid inputs.
        '''
        parameters = {}
        # Get Min_event length in microseconds
        try:
            parameters['min_event_length'] = float(self.min_event_length_edit.text())
        except ValueError:
            parameters['error'] = 'Could not read float from Min Event Length text box.  Please fix.'
            return parameters
        # Get Max Event Length in microseconds
        try:
            parameters['max_event_length'] = float(self.max_event_length_edit.text())
        except ValueError:
            parameters['error'] = 'Could not read float from Max Event Length text box.  Please fix.'
            return parameters
        if parameters['min_event_length'] >= parameters['max_event_length']:
            parameters['max_event_length'] = 'Min Event Length is greater than Max Event Length.  Please fix.'
            return parameters

        parameters['baseline_type'] = str(self.baseline_type_combo.currentText())
        if parameters['baseline_type'] == 'Adaptive':
            try:
                parameters['filter_parameter'] = float(self.filter_parameter_edit.text())
            except ValueError:
                parameters['error'] = 'Could not read float from Filter Parameter text box.  Please fix.'
                return
        elif parameters['baseline_type'] == 'Fixed':
            try:
                parameters['baseline_current'] = float(self.baseline_current_edit.text())
            except ValueError:
                parameters['error'] = 'Could not read float from Baseline Current text box.  Please fix.'

        parameters['threshold_direction'] = str(self.threshold_direction_combo.currentText())
        parameters['threshold_type'] = str(self.threshold_type_combo.currentText())
        if parameters['threshold_type'] == 'Noise Based':
            try:
                parameters['start_stddev'] = float(self.threshold_stdev_start.text())
            except ValueError:
                parameters['error'] = 'Could not read float from Start StdDev text box.  Please fix.'
            try:
                parameters['end_stddev'] = float(self.threshold_stdev_end.text())
            except ValueError:
                parameters['error'] = 'Could not read float from End StdDev text box.  Please fix.'
        elif parameters['threshold_type'] == 'Absolute Change':
            try:
                parameters['absolute_change_start'] = float(self.absolute_change_start_edit.text())
            except ValueError:
                parameters['error'] = 'Could not read float from Absolute Change Start.  Please fix.'
            try:
                parameters['absolute_change_end'] = float(self.absolute_change_end_edit.text())
            except ValueError:
                parameters['error'] = 'Could not read float from Absolute Change End.  Please fix.'
        elif parameters['threshold_type'] == 'Percent Change':
            try:
                parameters['percent_change_start'] = float(self.percentage_change_start_edit.text())
            except ValueError:
                parameters['error'] = 'Could not read float from Percent Change Start text box.  Please fix.'
            try:
                parameters['percent_change_end'] = float(self.percentage_change_end_edit.text())
            except ValueError:
                parameters['error'] = 'Could not read float from Percent Change End text box.  Please fix.'

        return parameters

    def clean_threads(self):
        for w in self.thread_pool:
            w.cancel()
            #             w.wait()
            self.thread_pool.remove(w)


def main():
    app = QtGui.QApplication(sys.argv)
    pixmap = QtGui.QPixmap('splash.png')
    splash = QtGui.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)
    splash.show()
    _long_imports(splash=splash, app=app)
    splash.showMessage("Creating main window...", alignment=QtCore.Qt.AlignBottom)
    app.processEvents()
    ex = MyMainWindow(app)
    ex.show()
    splash.finish(ex)
    app.exec_()
    ex.clean_threads()


if __name__ == '__main__':
    main()
else:
    # If we are running from a tests, name != main, and we'll need to import the long imports now.
    _long_imports()


