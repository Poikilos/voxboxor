
from __future__ import print_function
from __future__ import division
import os
import sys

if sys.version_info.major >= 3:
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter import messagebox
else:
    import Tkinter as tk  # type: ignore
    import ttk  # type: ignore
    import tkMessageBox as messagebox

from logging import getLogger

if __name__ == '__main__':
    MAINMENU_DIR = os.path.dirname(os.path.realpath(__file__))
    BAKEDIN_DIR = os.path.dirname(MAINMENU_DIR)
    REPO_DIR = os.path.dirname(BAKEDIN_DIR)
    sys.path.insert(0, REPO_DIR)

from bakedin.mainmenu.serverlistmgr import serverlistmgr

# Based on "Chain of Responsibility" example
#   by martineau on https://stackoverflow.com/a/26373337/4541104

logger = getLogger(__name__)


class Message(object):
    def __init__(self, kind, data):
        self.kind = kind
        self.data = data


class TabOnline(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        self.root = root
        self.widgets = []
        # do widget declarations

        self.row = 0

        self.urlLabel = ttk.Label(root, text="List server:")
        self.urlLabel.grid(row=self.row, column=0)

        self.urlVar = tk.StringVar(root)
        self.urlEntry = ttk.Entry(textvariable=self.urlVar)
        self.urlEntry.grid(row=self.row, column=1)
        # self.urlVar.trace("w", lambda name, index, mode, sv=self.urlVar: callback(sv))
        if sys.version_info.major >= 3:
            self.urlVar.trace_add("write", lambda name, index, mode, sv=self.urlVar: self.on_load(quiet=True))
        else:
            self.urlVar.trace("w", lambda name, index, mode, sv=self.urlVar: self.on_load(quiet=True))

        self.refreshBtn = ttk.Button(root, text="Refresh",
                                     command=self.refresh)
        self.refreshBtn.grid(row=self.row, column=2)
        self.server_widgets = []
        self.row += 1

        self.servers_row = self.row

        self.root.after(100, self.on_load)

    def on_load(self, quiet=False):
        serverlistmgr.set_masterserver_domain(self.urlVar.get(), quiet=quiet)
        if serverlistmgr.servers:
            self._load_list({
                'status': "done",
                'used_cache': True,
            })
        else:
            if not quiet:
                logger.warning("No servers were loaded.")

    def clear(self):
        for widget in self.server_widgets:
            widget.grid_forget()
        self.server_widgets.clear()
        self.row = self.servers_row

    def refresh(self):
        domain = self.urlVar.get().strip()
        if not domain:
            messagebox.showerror(
                "VoxBoxor",
                "Enter a list server domain first."
            )
            return
        serverlistmgr.set_masterserver_domain(domain)
        serverlistmgr.downloaded_cb = self._load_list
        serverlistmgr.sync()
        # ^ Calls self._load_list automatically
        #   (as self.downloaded_cb in that context)

    def _load_list(self, event):
        root = self.root
        self.clear()

        fields = ['address', 'clients', 'version', 'ping']
        column = -1
        for field in fields:
            column += 1
            text = field
            label = ttk.Label(root, text=text)
            label.grid(row=self.row, column=column)
            self.server_widgets.append(label)

        self.row += 1
        count = 0
        for server in serverlistmgr.servers:
            # TODO: Add symbols for booleans: 'creative', 'pvp', 'damage'
            # TODO: Add 'description', 'uptime', 'lag' (seconds apparently)
            column = -1
            for field in fields:
                column += 1
                text = str(server[field])
                if field == "clients":
                    text += "/" + str(server['clients_max'])
                elif field == "ping":
                    # Apparently it is in seconds
                    text = str(round(server[field]*1000)) + "ms"
                label = ttk.Label(root, text=text)
                label.grid(row=self.row, column=column)
                self.server_widgets.append(label)
            self.row += 1
            count += 1
        logger.warning("Loaded {} servers.".format(count))

    def message_downstream(self, message):
        for widget in self.widgets:
            widget.receive_message(message)

    def message_upstream(self, message):
        # do some logic based on the message
        pass


class Widget(tk.Button):
    def __init__(self, master, name, *args, **kwargs):
        tk.Button.__init__(self, master, *args, **kwargs)
        self.master = master
        # perhaps set command event to send a message
        self['command'] = lambda: self.message_upstream(Message(self.name, "I Got Clicked"))

    def message_downstream(self, message):
        # similar to above
        pass

    def message_upstream(self, message):
        self.master.message_upstream(self, message)


def main():
    root = tk.Tk()
    root.title("VoxBoxor")
    app = TabOnline(root)
    root.mainloop()
    return 0


if __name__ == '__main__':
    sys.exit(main())
