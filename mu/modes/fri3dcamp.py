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
        buttons = []

        buttons.append({
            'name': 'serial',
            'display_name': _('Serial'),
            'description': _('Open a serial connection to your device.'),
            'handler': self.toggle_repl,
            'shortcut': 'CTRL+Shift+S',
        })

        return buttons

    def api(self):
        """
        Return a list of API specifications to be used by auto-suggest and call
        tips.
        """
        return SHARED_APIS + FRI3DCAMP_APIS
