import os
import thread
import urwid
import socket
import inspect
os.sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))
from common import ifconfig

class TabNetwork(object):

    def __init__(self, main_loop):
        self.main_loop = main_loop
        self.name = u"NetWork"
        self.widget_list = []

        hostname = urwid.Edit(u"Hostname: ", socket.gethostname())
        self.widget_list.extend([
            urwid.Divider("-"),
            hostname,
        ])

        self.widget_list.extend(self.get_ifs_widgets())

        self.widget = WidgetWithSaveNicPopup(urwid.Pile(self.widget_list))

    def get_ifs_widgets(self):
        ifs_info_widget = []
        for interface in ifconfig.iterifs(physical=True):
            address_edit = urwid.Edit(u"Adress: ", str(interface.get_ip()))
            netmask_edit = urwid.Edit(u"Netmask: ", str(interface.get_netmask()))
            apply_button = urwid.Button(u"Apply")
            ifs_info_widget.append(urwid.Pile([
                urwid.Divider("-"),
                urwid.Text(u"Name: " + interface.name),
                address_edit,
                netmask_edit,
                urwid.Text(u"Status: " + ("up" if interface.is_up() else "down")),
                apply_button,
            ]))
            urwid.connect_signal(
                apply_button,
                "click",
                self.on_if_apply,
                user_arg=(interface.name,
                address_edit,
                netmask_edit))
        return ifs_info_widget

    def on_if_apply(self, button, if_info):
        self.widget.set_if_info(if_info)
        self.widget.open_pop_up()
        thread.start_new_thread(self.post_on_if_apply, (if_info,))

    def post_on_if_apply(self, if_info):
        interface = ifconfig.findif(if_info[0])
        with open('/etc/sysconfig/network-scripts/ifcfg-' + if_info[0], 'w') as out:
            out.write('HWADDR={}\n'.format(interface.get_mac())
                    + 'BOOTPROTO=static\n'
                    + 'IPADDR={}\n'.format(if_info[1].get_edit_text())
                    + 'PREFIX={}\n'.format(int(if_info[2].get_edit_text()))
            )
        os.system('/etc/init.d/network restart &>/dev/null')
        self.widget.if_update_finish()
        self.main_loop.draw_screen()


class WidgetWithSaveNicPopup(urwid.PopUpLauncher):

    def __init__(self, widget):
        self.__super.__init__(widget)

    def create_pop_up(self):
        self.pop_up = NetworkSaveDialog(self.pop_up_info)
        urwid.connect_signal(self.pop_up, 'close',
            lambda button: self.close_pop_up())
        return self.pop_up

    def get_pop_up_parameters(self):
        return {'left':0, 'top':1, 'overlay_width':32, 'overlay_height':7}

    def set_if_info(self, pop_up_info):
        self.pop_up_info = pop_up_info

    def if_update_finish(self):
        self.pop_up.if_update_finish()


class NetworkSaveDialog(urwid.WidgetWrap):

    signals = ['close']

    def __init__(self, pop_up_info):
        self.pop_up_info = pop_up_info
        self.close_button = urwid.Button("OK")
        urwid.connect_signal(self.close_button, 'click',
            lambda button:self._emit("close"))
        self.__super.__init__(
            urwid.AttrWrap(
                urwid.Filler(
                    urwid.Pile([
                        urwid.Text("Updating settings of interface " + pop_up_info[0]),
                    ])), 'popbg'))

    def if_update_finish(self):
        self._set_w(
            urwid.AttrWrap(
                urwid.Filler(
                    urwid.Pile([
                        urwid.Text(self.pop_up_info[0] + " updated sucessfully!"),
                        self.close_button,
                    ])), 'popbg'))

