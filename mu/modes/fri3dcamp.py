"""
The mode for working with the BBC micro:bit. Conatains most of the origial
functionality from Mu when it was only a micro:bit related editor.

Copyright (c) 2015-2017 Nicholas H.Tollervey and others (see the AUTHORS file).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import sys
import os.path
import logging
from mu.logic import HOME_DIRECTORY
from mu.contrib import uflash, microfs
from mu.modes.api import FRI3DCAMP_APIS, SHARED_APIS
from mu.modes.base import MicroPythonMode
from mu.interface.panes import CHARTS
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer


logger = logging.getLogger(__name__)


#class DeviceFlasher(QThread):
#    """
#    Used to flash the micro:bit in a non-blocking manner.
#    """
#    # Emitted when flashing the micro:bit fails for any reason.
#    on_flash_fail = pyqtSignal(str)
#
#    def __init__(self, paths_to_microbits, python_script, minify,
#                 path_to_runtime):
#        """
#        The paths_to_microbits should be a list containing filesystem paths to
#        attached micro:bits to flash. The python_script should be the text of
#        the script to flash onto the device. Minify should be a boolean to
#        indicate if the Python code is to be minified before flashing. The
#        path_to_runtime should be the path of the hex file for the MicroPython
#        runtime to use. If the path_to_runtime is None, the default MicroPython
#        runtime is used by default.
#        """
#        QThread.__init__(self)
#        self.paths_to_microbits = paths_to_microbits
#        self.python_script = python_script
#        self.minify = minify
#        self.path_to_runtime = path_to_runtime
#
#    def run(self):
#        """
#        Flash the device.
#        """
#        try:
#            uflash.flash(paths_to_microbits=self.paths_to_microbits,
#                         python_script=self.python_script,
#                         minify=self.minify,
#                         path_to_runtime=self.path_to_runtime)
#        except Exception as ex:
#            # Catch everything so Mu can recover from all of the wide variety
#            # of possible exceptions that could happen at this point.
#            self.on_flash_fail.emit(str(ex))
#

#class FileManager(QObject):
#    """
#    Used to manage micro:bit filesystem operations in a manner such that the
#    UI remains responsive.
#
#    Provides an FTP-ish API. Emits signals on success or failure of different
#    operations.
#    """
#
#    # Emitted when the tuple of files on the micro:bit is known.
#    on_list_files = pyqtSignal(tuple)
#    # Emitted when the file with referenced filename is got from the micro:bit.
#    on_get_file = pyqtSignal(str)
#    # Emitted when the file with referenced filename is put onto the micro:bit.
#    on_put_file = pyqtSignal(str)
#    # Emitted when the file with referenced filename is deleted from the
#    # micro:bit.
#    on_delete_file = pyqtSignal(str)
#    # Emitted when Mu is unable to list the files on the micro:bit.
#    on_list_fail = pyqtSignal()
#    # Emitted when the referenced file fails to be got from the micro:bit.
#    on_get_fail = pyqtSignal(str)
#    # Emitted when the referenced file fails to be put onto the micro:bit.
#    on_put_fail = pyqtSignal(str)
#    # Emitted when the referenced file fails to be deleted from the micro:bit.
#    on_delete_fail = pyqtSignal(str)
#
#    def on_start(self):
#        """
#        Run when the thread containing this object's instance is started so
#        it can emit the list of files found on the connected micro:bit.
#        """
#        self.ls()
#
#    def ls(self):
#        """
#        List the files on the micro:bit. Emit the resulting tuple of filenames
#        or emit a failure signal.
#        """
#        try:
#            result = tuple(microfs.ls(microfs.get_serial()))
#            self.on_list_files.emit(result)
#        except Exception as ex:
#            logger.exception(ex)
#            self.on_list_fail.emit()
#
#    def get(self, microbit_filename, local_filename):
#        """
#        Get the referenced micro:bit filename and save it to the local
#        filename. Emit the name of the filename when complete or emit a
#        failure signal.
#        """
#        try:
#            with microfs.get_serial() as serial:
#                microfs.get(microbit_filename, local_filename, serial)
#            self.on_get_file.emit(microbit_filename)
#        except Exception as ex:
#            logger.error(ex)
#            self.on_get_fail.emit(microbit_filename)
#
#    def put(self, local_filename):
#        """
#        Put the referenced local file onto the filesystem on the micro:bit.
#        Emit the name of the file on the micro:bit when complete, or emit
#        a failure signal.
#        """
#        try:
#            with microfs.get_serial() as serial:
#                microfs.put(local_filename, serial)
#            self.on_put_file.emit(os.path.basename(local_filename))
#        except Exception as ex:
#            logger.error(ex)
#            self.on_put_fail.emit(local_filename)
#
#    def delete(self, microbit_filename):
#        """
#        Delete the referenced file on the micro:bit's filesystem. Emit the name
#        of the file when complete, or emit a failure signal.
#        """
#        try:
#            with microfs.get_serial() as serial:
#                microfs.rm(microbit_filename, serial)
#            self.on_delete_file.emit(microbit_filename)
#        except Exception as ex:
#            logger.error(ex)
#            self.on_delete_fail.emit(microbit_filename)
#

class Fri3dCampMode(MicroPythonMode):
    """
    Represents the functionality required by the fri3dcamp mode.
    """
    name = _('Fri3dCamp badge')
    description = _("Write MicroPython for the Fri3dCamp badge.")
    icon = 'fri3dcamp'
    fs = None  #: Reference to filesystem navigator.
    flash_thread = None
    flash_timer = None

    valid_boards = [
        (0x10C4, 0xEA60),  # usb vid and pid for the cp2102n used in the fri3dcamp badge
    ]

    #user_defined_microbit_path = None

    def actions(self):
        """
        Return an ordered list of actions provided by this module. An action
        is a name (also used to identify the icon) , description, and handler.
        """
        buttons = []
#            {
#                'name': 'flash',
#                'display_name': _('Flash'),
#                'description': _('Flash your code onto the micro:bit.'),
#                'handler': self.flash,
#                'shortcut': 'F3',
#            },
#            {
#                'name': 'files',
#                'display_name': _('Files'),
#                'description': _('Access the file system on the micro:bit.'),
#                'handler': self.toggle_files,
#                'shortcut': 'F4',
#            },
#            {
#                'name': 'repl',
#                'display_name': _('REPL'),
#                'description': _('Use the REPL to live-code on the '
#                                 'micro:bit.'),
#                'handler': self.toggle_repl,
#                'shortcut': 'Ctrl+Shift+I',
#            }, ]
#        if CHARTS:
#            buttons.append({
#                'name': 'plotter',
#                'display_name': _('Plotter'),
#                'description': _('Plot incoming REPL data.'),
#                'handler': self.toggle_plotter,
#                'shortcut': 'CTRL+Shift+P',
#            })
        return buttons

    def api(self):
        """
        Return a list of API specifications to be used by auto-suggest and call
        tips.
        """
        return SHARED_APIS + FRI3DCAMP_APIS

