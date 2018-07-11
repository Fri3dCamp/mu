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
import logging
from mu.modes.api import FRI3DCAMP_APIS, SHARED_APIS
from mu.modes.base import MicroPythonMode


logger = logging.getLogger(__name__)


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
        # usb vid and pid for the cp2102n used in the fri3dcamp badge
        (0x10C4, 0xEA60),
    ]

    def actions(self):
        """
        Return an ordered list of actions provided by this module. An action
        is a name (also used to identify the icon) , description, and handler.
        """
        buttons = [
            {
                'name': 'flash',
                'display_name': _('Flash'),
                'description': _('Flash the firmware (not your program) '
                                 'on the Fri3dCamp badge'),
                'handler': self.flash_firmware,
                'shortcut': 'Ctrl+Shift+F',
            },
            {
                'name': 'repl',
                'display_name': _('REPL'),
                'description': _('Use the REPL to live-code on the '
                                 'micro:bit.'),
                'handler': self.toggle_repl,
                'shortcut': 'Ctrl+Shift+I',
            }, ]
        return buttons

    def api(self):
        """
        Return a list of API specifications to be used by auto-suggest and call
        tips.
        """
        return SHARED_APIS + FRI3DCAMP_APIS

    def flash_firmware(self):
        """
        Updates the firmware of the Fri3dCamp badge
        see https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo
        for the firmware and instructions
        """

        self.view.status_bar.set_message("test")

        import pkg_resources

        # find absolute locations of the files to flash
        file_loc_prefix = pkg_resources.resource_filename(
            'mu.resources', 'firmware/MicroPython_LoBo_esp32/esp32/')
        file_loc_bootloader = file_loc_prefix + 'bootloader/bootloader.bin'
        file_loc_phy_init_data = file_loc_prefix + 'phy_init_data.bin'
        file_loc_micropython = file_loc_prefix + 'MicroPython.bin'
        file_loc_partitions_mpy = file_loc_prefix + 'partitions_mpy.bin'

        # find the firmware flashing tool
        file_loc_esptool = pkg_resources.resource_filename(
            'mu.resources', 'firmware/esptool.py')

        # device_port should be something like "/dev/cu.SLAB_USBtoUART"
        device_port = self.find_device()
        print(device_port)

        if device_port is None:
            error_message = _("Couldn't find the Fri3dCamp Badge")
            logger.exception(error_message)
            information = _("Please check your cable")
            self.view.show_message(error_message, information, 'Warning')

        else:
            # we run the command esptool in a subprocess
            import subprocess
            cmd_to_run = "%s --chip esp32 --port /dev/cu.SLAB_USBtoUART " \
                         "--baud 921600 --before default_reset " \
                         "--after no_reset write_flash -z --flash_mode dio " \
                         "--flash_freq 40m --flash_size detect " \
                         "0x1000 %s 0xf000 %s 0x10000 %s 0x8000 %s" % (
                             file_loc_esptool, file_loc_bootloader,
                             file_loc_phy_init_data, file_loc_micropython,
                             file_loc_partitions_mpy)
            print("Running the command:\n", cmd_to_run)

            # completed_process = subprocess.run(cmd_to_run.split(" "),
            #                                    stdout=subprocess.PIPE,
            #                                    stderr=subprocess.STDOUT)

            from fcntl import fcntl, F_GETFL, F_SETFL
            from os import O_NONBLOCK, read

            proc = subprocess.Popen(cmd_to_run.split(" "),
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    #universal_newlines=True
                                    )
            flags = fcntl(proc.stdout, F_GETFL)  # get current p.stdout flags
            fcntl(proc.stdout, F_SETFL, flags | O_NONBLOCK)

            output = ""
            while proc.returncode is None:
                try:
                    proc.poll()
                    byte = proc.stdout.read(1)
                    if byte is not None:
                        output += byte.decode("utf-8")
                        #print(byte)

                except OSError:
                    # the os throws an exception if there is no data
                    continue
            print(output)

            if proc.returncode == 0:
                message_title = _("Flashed successfully")
                output = ""
            else:
                message_title = _("Error returned during firmware flashing")
                logger.exception(message_title)

                if "Timed out waiting for packet header" in output:
                    output += """
                    
                    Please click on the Flash icon, and then: 
                      + press and hold boot button
                      + press and hold rst button
                      + release rst button
                      + release boot button
                    """

            self.view.show_message(message_title, output)
