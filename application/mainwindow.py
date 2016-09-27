"""
    mainwindow.py

    Python programming for the primary MUCK window.
"""

import json

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass

import gobject
from gi.repository import Gtk, GLib

from aboutwindow import AboutWindow
from newaliaswindow import NewAliasWindow
from newlogwindow import NewLogWindow
from connection import Connection

class MainWindow(object):
    """
        Main window of the application.
    """

    application = None
    """
        Primary application state.
    """

    output_buffer = None
    """
        The text buffer used for the output.
    """

    def __init__(self, application):
        builder = Gtk.Builder()
        builder.add_from_file("ui/Main.glade")

        self.window = builder.get_object("MainWindow")

        self.label_output = builder.get_object("LabelOutput")
        self.label_output.set_use_markup(True)

        self.alias_list = builder.get_object("ListBoxAliases")
        self.scroll_window = builder.get_object("ViewPortContent")
        self.logging_enable = builder.get_object("CheckItemLoggingEnable")

        self.entry_input = builder.get_object("EntryInput")

        self.application = application

        self.add_alias("No Aliases.")

        builder.connect_signals(self)
        self.window.set_visible(True)

    def add_alias(self, name):
        # Build the new row
        row = Gtk.ListBoxRow()
        row.set_visible(True)

        text = Gtk.Label(name)

        icon = None
        # If its just the "No Aliases" text, don't use a grid.
        if name == "No Aliases.":
            row.add(text)
        else:
            icon = Gtk.Image()
            icon.set_from_stock("gtk-dialog-error", 2)
            icon.set_visible(True)

            grid = Gtk.Grid()
            grid.insert_row(0)
            grid.insert_column(0)
            grid.add(icon)
            grid.insert_column(1)
            grid.add(text)
            grid.set_visible(True)

            row.add(grid)

        text.set_visible(True)

        self.alias_list.add(row)
        return icon

    def save_text_buffer(self, element):
        # FIXME: Write the unmodified buffer
        if self.application.selected_alias is not None:
            with open("%s-log.txt" % self.application.selected_alias, "w") as handle:
                handle.write(self.application.aliases[self.application.selected_alias]["connection"].buffer)

    def toggle_logging(self, element):
        """
            Signal that's called when the user clicks the File->Logging Enable.
        """
        if self.application.selected_alias is not None:
            activated = element.get_active()
            self.application.aliases[self.application.selected_alias]["logging"] = activated

            if activated is True:
                window = NewLogWindow(self.application, self.application.selected_alias)
            else:
                self.application.alias_states[self.application.selected_alias]["logfile"] = None

    def key_pressed(self, element, event):
        """
            Signal that's called when the user presses any key on the input text box.
        """

        state, code = event.get_keycode()

        # We only want to send the current input when enter is struck
        if code == 36:
            self.send_text(self.entry_input)

    def show_about_window(self, element):
        """
            Signal that's called when the user clicks the Help->About.
        """
        window = AboutWindow(self.application)

    def show_new_alias_window(self, element):
        """
            Signal that's called when the user clicks the File->New Alias.
        """
        window = NewAliasWindow(self.application)

    def alias_selected(self, element, row):
        """
            Signal that's called when an alias is selected.
        """

        # FIXME: Why is this signal raised at application exit?
        if row is None:
            return

        children = row.get_children()

        if type(children[0]) is Gtk.Grid:
            name = children[0].get_child_at(1, 0).get_text()
            icon = children[0].get_child_at(0, 0)
            icon.set_from_stock("gtk-yes", 2)

            self.application.selected_alias = name

            if self.application.alias_states[name]["logfile"] is None:
                self.logging_enable.set_active(False)
            else:
                self.logging_enable.set_active(True)

            if self.application.alias_states[name]["connection"] is None or self.application.alias_states[name]["connection"].is_connected() is False:
                self.application.alias_states[name]["connection"] = Connection(self.application.aliases[name]["address"])

            self.label_output.set_markup(self.application.alias_states[name]["connection"].buffer)
            self.scroll_window.get_vadjustment().set_value(1.0)

    def send_text(self, element):
        """
            Signal that's called when the user presses "Send" or presses "Enter" when entering text.
        """
        text = self.entry_input.get_text()
        self.entry_input.set_text("")

        if self.application.selected_alias is not None:
            self.application.alias_states[self.application.selected_alias]["connection"].send(text)

    def close(self, element):
        """
            Signal that's called when the user clicks the X for the window or uses File->Quit.
        """

        config_string = json.dumps(self.application.aliases, sort_keys=True, indent=4, separators=(',', ': '))

        with open("config.txt", "w") as handle:
            handle.write(config_string)

        Gtk.main_quit()
