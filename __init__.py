# -*- mode: Python ; coding: utf-8 -*-
# Copyright © 2012–2013 Roland Sieker <ospalh@gmail.com>
# Based in part on code by Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

"""Add-on for Anki 2.1 to mouse in or out."""

from types import MethodType

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction, QMenu

from aqt import mw
from aqt.webview import AnkiWebView, QWebEngineView
from anki.hooks import addHook, runHook, wrap
from anki.lang import _

__version__ = "1.1.0"

# Before you change the review_standard_mouse size, maybe you should
# use larger fonts in your decks.


# How much to increase or decrease the mouse factor with each step. The
# a little odd looking number is the fourth root of two. That means
# with four clicks you double or half the size, as precisely as
# possible.
mouse_action = QAction(mw)
mouse_action.setText(u'Mouse Wheel')
mouse_action.setCheckable(True)
mouse_action.setChecked(False)


def add_action(submenu, label, callback, shortcut=None):
    """Add action to menu"""
    action = QAction(_(label), mw)
    action.triggered.connect(callback)
    if shortcut:
        action.setShortcut(QKeySequence(shortcut))
    submenu.addAction(action)


def setup_menu():
    """Set up the mouse menu."""
    try:
        mw.addon_view_menu
    except AttributeError:
        mw.addon_view_menu = QMenu(_('&View'), mw)
        mw.form.menubar.insertMenu(
            mw.form.menuTools.menuAction(),
            mw.addon_view_menu
        )

    mw.mouse_submenu = QMenu(_('&mouse'), mw)
    mw.addon_view_menu.addMenu(mw.mouse_submenu)

    mw.mouse_submenu.addAction(mouse_action)


def handle_wheel_event(event):

    if mouse_action.isChecked():
        step = event.angleDelta().y()
        if step > 0:
            if mw.state == "review":
                if mw.reviewer.state == 'answer' or mw.reviewer.state == 'question':
                    if mw.form.actionUndo.isEnabled():
                        mw.onUndo()
        else:
            if mw.state == "review":
                if mw.reviewer.state == 'question':
                    mw.reviewer._showAnswer()  # ._showAnswerHack()
                elif mw.reviewer.state == 'answer':
                    mw.reviewer._onAnswerButton("2")  # good
    else:
        original_mw_web_wheelEvent(event)


def run_move_to_state_hook(state, *args):
    """Run a hook whenever we have changed the state."""
    runHook("movedToState", state)


mw.moveToState = MethodType(
    wrap(mw.moveToState.__func__, run_move_to_state_hook), mw)
original_mw_web_wheelEvent = mw.web.wheelEvent
mw.web.wheelEvent = handle_wheel_event
setup_menu()
