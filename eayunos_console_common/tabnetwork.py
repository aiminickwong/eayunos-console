#coding=utf-8
import os
import thread
import urwid
import socket
import inspect
import ifconfig
import subprocess
from configtab import SimplePopupLauncher, SimplePopupDialog

class TabNetwork(object):

    def __init__(self, main_loop):
        self.main_loop = main_loop
        self.name = u"NetWork"
        self.widget_list = []

        self.hostname = urwid.Edit(u"Hostname: ", socket.gethostname())
        self.hostname_popup = SimplePopupLauncher(
            urwid.Columns(([self.hostname, urwid.Button(u"Save", on_press=self.save_hostname)])),
            "Save success.")
        self.widget_list.extend([
            urwid.Divider("-"),
            self.hostname_popup,
        ])

        ifs_widgets = self.get_ifs_widgets()
        bridge_widgets = self.get_bridge_widgets()
        if ifs_widgets:
            self.widget_list.extend(ifs_widgets)
        if bridge_widgets:
            self.widget_list.extend(bridge_widgets)
        #上面两个判断多余，直接self.widget_list.extend，只要保证ifs_widgets和bridge_widgets类型始终上list
        self.widget = WidgetWithSaveNicPopup(urwid.Pile(self.widget_list))

    def save_hostname(self, button):
        os.system("hostname %s" % self.hostname.edit_text)
        os.system("echo 'hostname %s' > /etc/sysconfig/network" % self.hostname.edit_text)
        self.hostname_popup.open_pop_up()

    def get_bridge_widgets(self):
        bridge_info_widgets = []
        for bridge in ifconfig.iterifs(bridge=True):
            try:
                if_name = subprocess.check_output(
                    "brctl show %s|grep %s" % (bridge.name, bridge.name),
                    shell=True).split("\t")[-1].strip()
                bridge_info_widgets.append(urwid.Pile([
                    urwid.Divider("-"),
                    urwid.Columns([
                        ("weight", 1, urwid.Pile([
                            urwid.Text(u"Name: %s" % if_name),
                            urwid.Text(u"Status: %s" % ("up" if ifconfig.Interface(if_name).is_up() else "down")),
                        ])),
                        ("weight", 2, urwid.Pile([
                            urwid.Text(u"Bridge: %s" % bridge.name),
                            urwid.Text(u"Address: %s" % bridge.get_ip()),
                            urwid.Text(u"Netmask: %s" % bridge.get_netmask()),
                            urwid.Text(u"Gateway: %s" % self.config_gateway(bridge.name)),
                        ])),
                    ])
                ]))
            except subprocess.CalledProcessError:
                continue
        return bridge_info_widgets

    def get_ifs_widgets(self):
        ifs_info_widget = []
        for interface in ifconfig.iterifs(physical=True):
            try:
                subprocess.check_output("brctl show|grep %s" % interface.name, shell=True)
                continue
            except subprocess.CalledProcessError:
                pass
            address_edit = urwid.Edit(u"Adress: ", str(interface.get_ip()))
            netmask_edit = urwid.Edit(u"Netmask: ", str(interface.get_netmask()))
            gateway_edit = urwid.Edit(u"Gateway: ", self.config_gateway(interface.name))
            apply_button = urwid.Button(u"Apply")
            ifs_info_widget.append(urwid.Pile([
                urwid.Divider("-"),
                urwid.Text(u"Name: " + interface.name),
                address_edit,
                netmask_edit,
                gateway_edit,
                urwid.Text(u"Status: " + ("up" if interface.is_up() else "down")),
                apply_button,
            ]))
            urwid.connect_signal(
                apply_button,
                "click",
                self.on_if_apply,
                user_arg=(interface.name, address_edit, netmask_edit, gateway_edit))
        return ifs_info_widget

    def config_gateway(self, name):
        try:
            gateway = subprocess.check_output(
                "cat /etc/sysconfig/network-scripts/ifcfg-%s|grep -i gateway" % name,
                shell=True)
            gateway = gateway.split("=")[1].replace("\"", "").replace("'", "").strip()
        except subprocess.CalledProcessError:
            gateway = ""
        return gateway

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
                    + 'GATEWAY={}\n'.format(if_info[3].get_edit_text())
                    + 'ONBOOT=yes\n'
            )
        os.system('/etc/init.d/network restart &>/dev/null')
        self.widget.if_update_finish()
        self.main_loop.draw_screen()


class WidgetWithSaveNicPopup(urwid.PopUpLauncher):

    def __init__(self, widget):
        urwid.PopUpLauncher.__init__(self, widget)
        # self.__super.__init__(widget)

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
        urwid.WidgetWrap.__init__(self, pop_up_info)
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
