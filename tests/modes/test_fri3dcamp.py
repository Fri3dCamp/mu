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
    pm = Fri3dCampMode(editor, view)
    assert pm.name == 'Fri3dCamp badge'
    assert pm.description is not None
    assert pm.icon == 'fri3dcamp'
    assert pm.is_debugger is False
    assert pm.editor == editor
    assert pm.view == view

    actions = pm.actions()
    assert len(actions) == 0


def test_fri3dcamp_api():
    """
    Make sure the API definition is as expected.
    """
    editor = mock.MagicMock()
    view = mock.MagicMock()
    pm = Fri3dCampMode(editor, view)
    result = pm.api()
    assert result == SHARED_APIS + FRI3DCAMP_APIS
