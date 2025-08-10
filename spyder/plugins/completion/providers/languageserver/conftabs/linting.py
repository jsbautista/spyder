# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""
Language Server Protocol linting configuration tab.
"""

# Standard library imports
import re

# Third party imports
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QButtonGroup,
    QGroupBox,
    QGridLayout,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

# Local imports
from spyder.api.preferences import SpyderPreferencesTab
from spyder.api.translations import _
from spyder.utils.stylesheet import AppStyle


class LintingConfigTab(SpyderPreferencesTab):
    """Linting configuration tab."""

    TITLE = _('Linting')

    def __init__(self, parent):
        super().__init__(parent)
        newcb = self.create_checkbox

        linting_label = QLabel(
            _(
                "Spyder can highlight syntax errors and possible problems "
                "with your code in the editor by using one of the providers "
                "below"
            )
        )
        linting_label.setOpenExternalLinks(True)
        linting_label.setWordWrap(True)

        linting_select_group = QGroupBox(_("Provider"))

        linting_bg = QButtonGroup(linting_select_group)
        basic_linting_radio = self.create_radiobutton(
            _("Pyflakes (Basic)"),
            'pyflakes',
            button_group=linting_bg
        )
        flake_linting_radio = self.create_radiobutton(
            _("Flake8 (Intermediate)"),
            'flake8',
            button_group=linting_bg
        )
        
        disable_linting_radio = self.create_radiobutton(
            _("Disable linting"),
            'no_linting',
            button_group=linting_bg
        )
        
        linting_select_layout = QVBoxLayout()
        linting_select_layout.addSpacing(3 * AppStyle.MarginSize)
        linting_select_layout.addWidget(basic_linting_radio)
        linting_select_layout.addWidget(flake_linting_radio)
        linting_select_layout.addWidget(disable_linting_radio)
        linting_select_group.setLayout(linting_select_layout)

        additional_options_group = QGroupBox(_("Additional options"))

        underline_errors_box = newcb(
            _("Underline errors and warnings"),
            'underline_errors',
            section='editor')

        additional_options_layout = QVBoxLayout()
        additional_options_layout.addWidget(underline_errors_box)
        additional_options_group.setLayout(additional_options_layout)

        configuration_options_group = QGroupBox(_("Provider options"))
        configuration_options_layout = QVBoxLayout()

        self.flake8_filenames_match = self.create_lineedit(
            _("Only check these filenames:"),
            'flake8/filename',
            alignment=Qt.Horizontal,
            word_wrap=False,
            placeholder=_("Check test files: test_.*\.py"),
        )

        self.flake8_exclude = self.create_lineedit(
            _("Exclude these files or directories:"),
            'flake8/exclude',
            alignment=Qt.Horizontal,
            word_wrap=False,
            placeholder=_("Exclude test files: (?!test_).*\\.py"),
        )

        flake8_select = self.create_lineedit(
            _("Show these errors or warnings:"),
            'flake8/extendSelect',
            alignment=Qt.Horizontal,
            word_wrap=False,
            placeholder=_("Example codes: E113, W391"),
        )

        flake8_ignore = self.create_lineedit(
            _("Ignore these errors or warnings:"),
            'flake8/extendIgnore',
            alignment=Qt.Horizontal,
            word_wrap=False,
            placeholder=_("Default is: E,W,C90"),
        )

        flake8_layout = QGridLayout()
        flake8_layout.addWidget(self.flake8_filenames_match.label, 1, 0)
        flake8_layout.addWidget(self.flake8_filenames_match.textbox, 1, 1)
        flake8_layout.addWidget(self.flake8_exclude.label, 2, 0)
        flake8_layout.addWidget(self.flake8_exclude.textbox, 2, 1)
        flake8_layout.addWidget(flake8_select.label, 3, 0)
        flake8_layout.addWidget(flake8_select.textbox, 3, 1)
        flake8_layout.addWidget(flake8_ignore.label, 4, 0)
        flake8_layout.addWidget(flake8_ignore.textbox, 4, 1)

        pyflakes_conf_options = QLabel(
            _("There are no configuration options for Pyflakes")
        )
        not_select_conf_options = QLabel(_("Linting is disabled"))

        grid_widget = QWidget()
        grid_widget.setLayout(flake8_layout)

        configuration_options_layout.addWidget(grid_widget)
        configuration_options_layout.addWidget(pyflakes_conf_options)
        configuration_options_layout.addWidget(not_select_conf_options)

        flake_linting_radio.radiobutton.toggled.connect(
            lambda checked: (
                grid_widget.setVisible(checked),
                pyflakes_conf_options.setVisible(not checked),
                not_select_conf_options.setVisible(False)
            ) if checked else None
        )

        basic_linting_radio.radiobutton.toggled.connect(
            lambda checked: (
                grid_widget.setVisible(False),
                pyflakes_conf_options.setVisible(checked),
                not_select_conf_options.setVisible(False)
            ) if checked else None
        )

        disable_linting_radio.radiobutton.toggled.connect(
            lambda checked: (
                grid_widget.setVisible(False),
                pyflakes_conf_options.setVisible(False),
                not_select_conf_options.setVisible(checked)
            ) if checked else None
        )

        configuration_options_group.setLayout(configuration_options_layout)

        # Linting layout
        linting_layout = QVBoxLayout()
        linting_layout.addWidget(linting_label)
        linting_layout.addWidget(linting_select_group)
        linting_layout.addWidget(configuration_options_group)
        linting_layout.addWidget(additional_options_group)
        self.setLayout(linting_layout)

    def report_invalid_regex(self, files=True):
        """
        Report that excluded files/directories should be valid regular
        expressions.
        """
        msg = _(
            "Directory patterns listed for exclusion should be valid regular "
            "expressions"
        )
        if files:
            msg = _(
                "File patterns listed for inclusion should be valid regular "
                "expressions"
            )

        QMessageBox.critical(self, _("Error"), msg)

    def is_valid(self):
        # Check regexs
        try:
            flake8_filenames_matches = (
                self.flake8_filenames_match.textbox.text().split(",")
            )
            for match in flake8_filenames_matches:
                re.compile(match.strip())
        except re.error:
            self.report_invalid_regex()
            return False

        try:
            flake8_excludes = self.flake8_exclude.textbox.text().split(",")
            for match in flake8_excludes:
                re.compile(match.strip())
        except re.error:
            self.report_invalid_regex(files=False)
            return False

        return True
