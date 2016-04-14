import os
import urwid
import socket
import inspect
os.sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))
from common import ifconfig

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

        self.widget = urwid.Pile(self.widget_list)

    def get_ifs_widgets(self):
        ifs_info_widget = []
        for interface in ifconfig.iterifs(physical=True):
            address_edit = urwid.Edit(u"Adress: ", str(interface.get_ip()))
            netmask_edit = urwid.Edit(u"Netmask: ", str(interface.get_netmask()))
            ifs_info_widget.append(urwid.Pile([
                urwid.Divider("-"),
                urwid.Text(u"Name: " + interface.name),
                address_edit,
                netmask_edit,
                urwid.Text(u"Status: " + ("up" if interface.is_up() else "down")),
                urwid.Button(u"Apply", on_press=self.on_apply_if, user_data=(interface.name, address_edit, netmask_edit)),
            ]))
        return ifs_info_widget

    def on_apply_if(self, button, if_info):
        interface = ifconfig.findif(if_info[0])
        with open('/etc/sysconfig/network-scripts/ifcfg-' + if_info[0], 'w') as out:
            out.write('HWADDR={}\n'.format(interface.get_mac())
                    + 'BOOTPROTO=static\n'
                    + 'IPADDR={}\n'.format(if_info[1].get_edit_text())
                    + 'PREFIX={}\n'.format(int(if_info[2].get_edit_text()))
            )
        os.system('/etc/init.d/network restart')

