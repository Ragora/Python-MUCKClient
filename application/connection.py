"""
    connection.py


"""

import re
import socket
import select

class Connection(object):
    buffer = None

    line_buffer = None
    socket = None

    def __init__(self, address):
        self.line_buffer = ""
        self.buffer = "<b>Attempting to connect to '%s' ...</b>\n" % address

        self.socket = socket.socket()

        # FIXME: Properly validate this?
        address_data = address.split(":")
        address = address_data[0]
        if len(address_data) == 1:
            port = 8888
        else:
            port = int(address_data[1])

        try:
            self.socket.connect((address, port))
        except socket.gaierror as error:
            self.buffer += "<b>Failed to connect: %s</b>" % error
            self.socket = None
            return

        self.socket.setblocking(False)

    def send(self, text):
        """
            Sends some text to the connected server.

            Parameters--
                text: The text to send to the remote server.
        """
        if self.is_connected() is True:
            try:
                self.socket.send(text + "\n")
            except socket.error:
                self.socket = None

    def is_connected(self):
        """
            Returns whether or not this connection object is currently
            connected to a remote server.
        """
        return self.socket is not None

    def disconnect(self):
        """
            Disconnects the connection object from the remote server.
        """
        if self.is_connected() is False:
            return

        # FIXME: Configurable
        self.send("QUIT")
        
        self.socket.close()
        self.socket = None

    def update(self):
        """
            Update routine to read data from the server and return any lines written,
            if any.

            Returns: A list of lines written by the server this call. If no lines are written,
            an empty list is returned.
        """
        if self.is_connected() is False:
            return []

        new_lines = []

        ready_read, ready_write, exception_list = select.select((self.socket,), (), (), 0)

        if ready_read:
            buffer = self.socket.recv(8)

            if len(buffer) == 0:
                self.socket = None
                return

            self.line_buffer += buffer

            if "\n" in self.line_buffer:
                if self.line_buffer.find("\n") != -1:
                    lines = self.line_buffer.split("\n")

                    added_lines = lines[0:len(lines) - 1]
                    self.line_buffer = lines.pop()

                    new_lines = added_lines

        return new_lines

    def acknowledge_lines(self, lines):
        """
            Acknowledges lines that were written by the server. This is intended for
            code that is using the connection object to have a chance to modify newly received
            lines (such as formatters for text patterns) before being inserted into the buffer.

            Parameters--
                lines: A list of lines to write into the text buffer.
        """
        self.buffer += "\n".join(lines)
