import urwid
import socket
import ifconfig

class TabNetwork(object):

    def __init__(self):
        self.name = u"NetWork"
        self.widget_list = []

        hostname = urwid.Edit(u"Hostname: ", socket.gethostname())
        self.widget_list.extend([
            urwid.Divider("-"),
            hostname,
        ])

        self.widget_list.extend(self.get_ifs_widgets())

        self.widget_list.extend([
            urwid.Divider("-"),
            urwid.Divider(" "),
        ])
        save = urwid.Button(u"Save")
        urwid.connect_signal(save, 'click', self.on_save)
        self.widget_list.append(save)

        self.widget = urwid.Pile(self.widget_list)

    def get_ifs_widgets(self):
        ifs_info_widget = []
        for interface in ifconfig.iterifs(physical=True):
            ifs_info_widget.append(urwid.Pile([
                urwid.Divider("-"),
                urwid.Text(u"Name: " + interface.name),
                urwid.Edit(u"Adress: ", str(interface.get_ip())),
                urwid.Edit(u"Netmask: ", str(interface.get_netmask())),
                urwid.Text(u"Status: " + ("up" if interface.is_up() else "down"))
            ]))
        return ifs_info_widget

    def on_save(self):
        return

