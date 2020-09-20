""" Module for 1D scanning experiments with convenient GUI interface """

import socket
import os
import sys
from PyQt5 import QtWidgets
import importlib
import pyqtgraph as pg
import numpy as np

from pylabnet.scripts.sweeper.sweeper import MultiChSweep1D
from pylabnet.gui.pyqt.external_gui import Window
from pylabnet.utils.helper_methods import (get_gui_widgets, load_config,
    get_legend_from_graphics_view, add_to_legend, fill_2dlist)


class Controller(MultiChSweep1D):

    def __init__(self, logger=None, channels=['Channel 1'], clients={}, exp_path=None):
        """ Instantiates controller

        :param logger: instance of LogClient
        :param channels: (list) list of channel names
        :param exp_path: (str) path to experiment directory containing experiment functions
        """

        super().__init__(logger, channels)
        self.module = None

        # Instantiate GUI
        self.gui = Window(
            gui_template='scan_1d',
            host=socket.gethostbyname(socket.gethostname())
        )
        self.widgets = get_gui_widgets(self.gui, p_min=1, p_max=1, pts=1,
            graph=2, hmap=2, legend=2, clients=1, exp=1, exp_preview=1, configure=1, run=1)

        # Configure default parameters
        self.min = self.widgets['p_min'].value()
        self.max = self.widgets['p_max'].value()
        self.pts = self.widgets['pts'].value()

        self.data_fwd = []
        self.data_bwd = []
        self.x_fwd = self._generate_x_axis()
        self.x_bwd = self._generate_x_axis(backward=True)

        # Configure list of experiments
        self.exp_path = exp_path
        if self.exp_path is None:
            self.exp_path = os.getcwd()
        sys.path.insert(1, self.exp_path)
        for filename in os.listdir(exp_path):
            if filename.endswith('.py'):
                self.widgets['exp'].addItem(filename[:-3])
        self.widgets['exp'].itemClicked.connect(self.display_experiment)

        # Configure list of clients
        self.clients = clients
        for client_name, client_obj in self.clients.items():
            client_item = QtWidgets.QListWidgetItem(client_name)
            client_item.setToolTip(str(client_obj))
            self.widgets['clients'].addItem(client_item)

        # Configure button
        self.widgets['configure'].clicked.connect(self.configure_experiment)
        self.widgets['run'].clicked.connect(self.run)

    def display_experiment(self, item):
        """ Displays the currently clicked experiment in the text browser

        :param item: (QlistWidgetItem) with label of name of experiment to display
        """

        with open(os.path.join(self.exp_path, f'{item.text()}.py'), 'r') as exp_file:
            exp_content = exp_file.read()

        self.widgets['exp_preview'].setText(exp_content)

    def configure_experiment(self):
        """ Configures experiment to be the currently selected item """

        self.module = importlib.import_module(self.widgets['exp'].currentItem().text())
        self.module = importlib.reload(self.module)

        self.experiment = self.module.experiment
        self.min = self.widgets['p_min'].value()
        self.max = self.widgets['p_max'].value()
        self.pts = self.widgets['pts'].value()

        self.x_fwd = self._generate_x_axis()
        self.x_bwd = self._generate_x_axis(backward=True)


    def _configure_plots(self, plot=True):
        """ Configures the plots """

        self.widgets['curve'] = []
        for index, graph in enumerate(self.widgets['graph']):
            self.widgets['legend'][index] = get_legend_from_graphics_view(
                self.widgets['legend'][index]
            )
            self.widgets['curve'].append(graph.plot(
                pen=pg.mkPen(color=self.gui.COLOR_LIST[0])
            ))
            add_to_legend(
                self.widgets['legend'][index],
                self.widgets['curve'][index],
                'Single scan'
            )

    def _reset_plots(self):
        """ Resets things after a rep """
        self.data_bwd.append([])
        self.data_fwd.append([])


    def _run_and_plot(self, x_value, backward=False):

        if backward:
            # Single trace
            self.data_bwd[-1].append(self.experiment(x_value))
            self.widgets['curve'][1].setData(
                self.x_bwd[:len(self.data_bwd[-1])],
                self.data_bwd[-1]
            )

            # Heat map
            self.widgets['hmap'][1].setImage(np.transpose(
                fill_2dlist(self.data_bwd)
            ))
        else:
            self.data_fwd[-1].append(self.experiment(x_value))
            self.widgets['curve'][0].setData(
                self.x_fwd[:len(self.data_fwd[-1])],
                self.data_fwd[-1]
            )

            # Heat map
            self.widgets['hmap'][0].setImage(np.transpose(
                fill_2dlist(self.data_fwd)
            ))
        self.gui.force_update()

    def _update_hmaps(self, reps_done):
        pass

    def _update_integrated(self, reps_done):
        pass

def main():
    config = load_config('laser_scan')
    control=Controller(exp_path=config['path'])
    while True:
        control.gui.force_update()

if __name__ == '__main__':
    main()
