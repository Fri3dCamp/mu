# -*- coding: utf-8 -*-
"""
Tests for the Fri3dCamp mode.
"""
from mu.modes.fri3dcamp import Fri3dCampMode
from mu.modes.api import SHARED_APIS, FRI3DCAMP_APIS
from unittest import mock


def test_fri3dcamp_mode():
    """
    Sanity check for setting up of the mode.
    """
    editor = mock.MagicMock()
    view = mock.MagicMock()
    fm = Fri3dCampMode(editor, view)
    assert fm.name == 'Fri3dCamp badge'
    assert fm.description is not None
    assert fm.icon == 'fri3dcamp'
    assert fm.is_debugger is False
    assert fm.editor == editor
    assert fm.view == view

    actions = fm.actions()
    assert len(actions) == 2
    assert actions[0]['name'] == 'repl'
    assert actions[0]['handler'] == fm.toggle_repl
    assert actions[1]['name'] == 'firmware flash'
    assert actions[1]['handler'] == fm.flash_firmware


def test_fri3dcamp_api():
    """
    Make sure the API definition is as expected.
    """
    editor = mock.MagicMock()
    view = mock.MagicMock()
    pm = Fri3dCampMode(editor, view)
    result = pm.api()
    assert result == SHARED_APIS + FRI3DCAMP_APIS
