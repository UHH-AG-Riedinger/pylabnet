""" Script that launches and continuously runs a GUI window

Normally, this is meant to be invoked from within a Launcher object (see launcher.py).
However, you can also call this directly, with command-line arguments:
:arg --logport: port number of log server
:arg --guiport: (optional) port number to use for GUI server. Notes:
    (1) if not provided, the user will be prompted to enter a port number in the commandline
    (2) will raise a ConnectionRefusedError if port fails
:arg --ui: (optional) the name of the server module. Notes:
    (1) should be a valid .ui file (with .ui extension removed) within pylabnet/gui/pyqt/templates,
        otherwise, FileNotFound error will be raised
    (2) if not provided, _default_template will be used
"""

from PyQt5 import QtWidgets, QtCore

from pylabnet.gui.pyqt.external_gui import Window, Service
from pylabnet.core.generic_server import GenericServer
from pylabnet.utils.logging.logger import LogClient
from pylabnet.utils.helper_methods import parse_args, show_console, hide_console

import sys
import socket
import numpy as np

# Should help with scaling issues on monitors of differing resolution
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


def main():

    # parse command line arguments
    args = parse_args()
    try:
        log_port = int(args['logport'])
    except IndexError:
        raise IndexError('logport not provided. Please provide command line arguments in the form\n"'
                         'python launch_gui.py --logip 000.000.000.000 --logport 1234 --guiport 5678 --ui uifilename')
    if 'logip' in args:
        log_ip = args['logip']
    else:
        log_ip = 'localhost'
    if 'ui' in args:
        gui_template = args['ui']
    else:
        show_console()
        gui_template = input('Please enter a GUI template to use: ')
        hide_console()
    if 'guiport' in args:
        gui_port = int(args['guiport'])
    else:
        show_console()
        gui_port = int(input('Please enter a GUI port value: '))
        hide_console()

    # Instantiate logger
    gui_logger = LogClient(
        host=log_ip,
        port=log_port,
        module_tag=gui_template+'_GUI',
        ui=gui_template,
        server_port=gui_port
    )

    gui_logger.info('Logging for gui template: {}'.format(gui_template))

    # Create app and instantiate main window
    app = QtWidgets.QApplication(sys.argv)
    try:
        main_window = Window(app, gui_template=gui_template)
    except FileNotFoundError:
        gui_logger.warn('Could not find .ui file, '
                        'please check that it is in the pylabnet/gui/pyqt/gui_templates directory')
        raise

    # Instantiate GUI server
    gui_service = Service()
    gui_service.assign_module(module=main_window)
    gui_service.assign_logger(logger=gui_logger)

    # Make connection
    try:
        gui_server = GenericServer(
            service=gui_service,
            host=socket.gethostbyname(socket.gethostname()),
            port=gui_port
        )
    except ConnectionRefusedError:
        gui_logger.warn('Tried and failed to create GUI server with \nIP:{}\nPort:{}'.format(
            socket.gethostbyname(socket.gethostname()),
            gui_port
        ))
        raise
    gui_server.start()

    # Update GUI with server-specific details
    main_window.ip_label.setText('IP Address: {}'.format(
        socket.gethostbyname(socket.gethostname())
    ))
    main_window.port_label.setText('Port: {}'.format(gui_port))

    # Run the GUI until the stop button is clicked
    while not main_window.stop_button.isChecked():
        main_window.configure_widgets()
        main_window.update_widgets()
        main_window.force_update()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
