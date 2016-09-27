"""
    main.py
"""

import re
import os
import sys
import cgi
import json

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass

from gi.repository import Gtk, GLib

from mainwindow import MainWindow

class Application(object):
    """
        The primary application state object.
    """

    main_window = None
    """
        The main window of the application.
    """

    aliases = None
    """
        Configurable data that should consist of only serializable data.
    """

    alias_states = None
    """
        Runtime relevant state data about each alias.
    """

    url_pattern = re.compile("http\://.+")

    selected_alias = None

    def main(self):
        """
            Main entry point of the application. This is called to perform initialization of the program
            state and start up the GUI.
        """

        self.aliases = {}
        self.alias_states = {}
        GLib.idle_add(self.update)

        self.main_window = MainWindow(self)

        # Before we finally launch, load the config
        try:
            with open("config.txt", "r") as handle:
                buffer = handle.read()

                aliases = json.loads(buffer)

                for alias in aliases:
                    self.add_alias(alias, aliases[alias]["address"], aliases[alias]["password"])
        except OSError:
            print("Failed to load config.")

        Gtk.main()

    def update(self):
        modified_current_alias = False

        for alias in self.aliases:
            if alias != "No Aliases." and self.alias_states[alias]["connection"] is not None:
                if self.alias_states[alias]["connection"].is_connected():
                    new_lines = self.alias_states[alias]["connection"].update()

                    # Once we're done updating the buffer, run formatters
                    if new_lines is not None and len(new_lines) != 0:
                        # Write to the logfile if enabled
                        if self.alias_states[alias]["logfile"] is not None:
                            """
                                This is an inefficient logging mechanism but given the nature of MUCK, this performance impact is negligable and allows
                                for log changes to appear in realtime as well as adding safety against crashes.
                            """
                            with open(self.alias_states[alias]["logfile"], "a") as handle:
                                handle.write("\n".join(new_lines))

                        for index, line in enumerate(new_lines):
                            # Escape incoming data so we don't break the markup
                            line = cgi.escape(line)

                            # TODO: Configurable formatters
                            line = line.replace("Ragora", "<span foreground=\"blue\">Ragora</span>")

                            # Replace things that look like URL's with the href tags
                            # FIXME: Try things that look like URL's, ie: www.*
                            for match in re.finditer(self.url_pattern, line):
                                match_text = match.group(0)

                                line = line.replace(match_text, "<a href=\"%s\">%s</a>" % (match_text, match_text))

                            new_lines[index] = line
                        # Feed the modified data back to the connection
                        self.alias_states[alias]["connection"].acknowledge_lines(new_lines)

                        if self.selected_alias == alias:
                            modified_current_alias = True
                else:
                    self.alias_states[alias]["icon"].set_from_stock("gtk-dialog-error", 2)

            if modified_current_alias is True:
                # FIXME: Auto scroll to the bottom
                self.main_window.label_output.set_markup(self.alias_states[self.selected_alias]["connection"].buffer)
                vertical = self.main_window.scroll_window.get_vadjustment()

                vertical.set_value(vertical.get_upper() - vertical.get_page_size())

        return True

    def add_alias(self, name, address, password):
        self.alias_states[name] = {
            "connection": None,
            "icon": self.main_window.add_alias(name),
            "logfile": None,
        }

        self.aliases[name] = {
            "address": address,
            "password": password,
        }

if __name__ == "__main__":
    Application().main()
