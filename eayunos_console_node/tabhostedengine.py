# coding=utf-8

import os
import sys
import re
import random
import urwid
import subprocess
import socket
import struct
import inspect
import threading
import time
import psutil
os.sys.path.insert(
    0, os.path.dirname(
        os.path.dirname(
            os.path.abspath(
                inspect.getfile(inspect.currentframe())))))
from eayunos_console_common import ifconfig
from vdsm import vdscli
import errno
from socket import error as socket_error


class TabHostedEngine(object):

    def __init__(self, main_loop):
        self.main_loop = main_loop
        self.name = u"Hosted engine"
        self.output = urwid.Text("")
        hosted_engine_status = self.get_hosted_engine_status()
        self.widget = urwid.AttrMap("", "")
        self.setup_log_path = "/tmp/.hosted-engine-setup.log"
        self.answers_path = "/tmp/.answers.conf"
        if hosted_engine_status == "stopped":
            self.widget.original_widget = self.get_pre_setup_widget()
        elif hosted_engine_status == "setting_up":
            self.widget.original_widget = self.get_setup_widget()
        elif hosted_engine_status == "running":
            self.widget.original_widget = self.get_status_widget()

    def update_pre_setup_widget(self, button, selected):
        if selected:
            self.pre_setup_widget.original_widget = self.get_new_setup_widget()
        else:
            self.pre_setup_widget.original_widget = self.get_existing_setup_widget()

    def get_pre_setup_widget(self):
        self.pre_setup_option = []
        self.pre_setup_widget = urwid.AttrMap(self.get_new_setup_widget(), "")
        #self.pre_setup_widget.original_widget=self.get_new_setup_widget()
        return WidgetWithPopup(urwid.Pile([
            urwid.Button(u"Clean up setup failures before setup", on_press=self.cleanup_before_setup),
            urwid.Divider(),
            urwid.Text(u"Choose an option to setup:"),
            urwid.Divider(),
            urwid.GridFlow([
                urwid.RadioButton(self.pre_setup_option, u"New hosted engine setup",
                    on_state_change=self.update_pre_setup_widget),
                urwid.RadioButton(self.pre_setup_option, u"Existing hosted engine setup"),
            ], 33, 2, 0, 'left'),
            urwid.Divider(),
            self.pre_setup_widget,
        ]))

    def cleanup_before_setup(self, button):
        self.widget.original_widget.open_pop_up()
        self.main_loop.draw_screen()
        os.system("service ovirt-ha-agent stop")
        os.system("chkconfig ovirt-ha-agent off")
        os.system("kill `ps aux |grep HostedEngin[e]|tr -s ' '|cut -d' ' -f2`")
        os.system("service ovirt-ha-broker stop")
        os.system("rm -f /etc/ovirt-hosted-engine/hosted-engine.conf")
        os.system("rm -f /var/run/vdsm/*.recovery")
        os.system("service vdsmd restart")
        self.widget.original_widget.cleanup_finish()
        self.main_loop.draw_screen()

    def get_new_setup_widget(self):
        blank = urwid.Divider()
        self.w_gateway = urwid.Edit(u"Gateway: ", self.get_default_gw())
        self.w_bridge_if = []
        self.w_engine_hostname = urwid.Edit(u"Engine hostname: ")
        self.w_engine_static_cidr = urwid.Edit(u"Engine static CIDR: ")
        self.w_engine_mac_addr = urwid.Edit(u"Engine MAC address: ", self.random_MAC())
        self.w_engine_root_password = urwid.Edit(u"Engine root user password: ", mask="*")
        self.w_engine_admin_password = urwid.Edit(u"Engine admin@internal password: ", mask="*")
        self.w_storage_type = []
        self.w_lun_list = []
        self.w_storage_connection_nfs = urwid.Edit(u"Storage connection: ")
        self.w_storage_connection_iscsi = urwid.Text(u"To be implemented.")
        self.w_storage_connection_fc = self.genRadioButton(u"Storage LUN: ", self.get_fc_lun_tuple_list(), self.w_lun_list)
        self.w_storage_connection = urwid.Pile([self.w_storage_connection_nfs])
        return urwid.Pile([
            urwid.Divider("-"),
            urwid.Text("Setup configuration: "),
            urwid.Divider("-"),
            blank,
            self.w_gateway,
            self.genRadioButton(u"Interface to set eayunos bridge on: ",
                [(nic.name, None) for nic in ifconfig.iterifs()], self.w_bridge_if),
            blank,
            self.w_engine_hostname,
            self.w_engine_static_cidr,
            self.w_engine_mac_addr,
            self.w_engine_root_password,
            self.w_engine_admin_password,
            blank,
            self.get_storage_type_options(),
            self.w_storage_connection,
            blank,
            urwid.Button("Begin setup", on_press=self.begin_setup),
        ])

    def get_existing_setup_widget(self):
        blank = urwid.Divider()
        self.w_engine_admin_password = urwid.Edit(u"Engine admin@internal password: ", mask="*")
        self.w_host_id = urwid.IntEdit(u"Host Id: ", "")
        self.w_bridge_if = []
        self.w_storage_type = []
        self.w_lun_list = []
        self.w_storage_connection_nfs = urwid.Edit(u"Storage connection: ")
        self.w_storage_connection_iscsi = urwid.Text(u"To be implemented.")
        self.w_storage_connection_fc = self.genRadioButton(u"Storage LUN: ", self.get_fc_lun_tuple_list(), self.w_lun_list)
        self.w_storage_connection = urwid.Pile([self.w_storage_connection_nfs])
        return urwid.Pile([
            urwid.Divider("-"),
            urwid.Text("Setup configuration: "),
            urwid.Divider("-"),
            blank,
            self.genRadioButton(u"Interface to set eayunos bridge on: ",
                [(nic.name, None) for nic in ifconfig.iterifs()], self.w_bridge_if),
            blank,
            self.w_engine_admin_password,
            blank,
            self.w_host_id,
            blank,
            self.get_storage_type_options(),
            self.w_storage_connection,
            blank,
            urwid.Button("Begin setup", on_press=self.begin_setup_existing),
        ])

    def get_storage_type_options(self):
        return self.genRadioButton(u"Storage type: ", [
                ("nfs3", self.update_storage_domain_nfs),
                ("iscsi", self.update_storage_domain_iscsi),
                ("fc", self.update_storage_domain_fc)
            ], self.w_storage_type)

    def genRadioButton(self, caption_text, options, radiobutton_group):
        return urwid.Columns([
                ('pack', urwid.Text(caption_text)),
                urwid.GridFlow([
                    urwid.RadioButton(radiobutton_group, option[0], on_state_change=option[1])
                    for option in options], 30, 2, 0, 'left'),
            ])

    def begin_setup(self, button):
        if self.validate_setup_input():
            os.system("cp /etc/eayunos-console-node/answers.conf %s" % self.answers_path)
            self.update_answers_file("HEN_GATEWAY", self.w_gateway.get_edit_text())
            self.update_answers_file("HEN_BRIDGE_IF", self.get_radio_option(self.w_bridge_if))
            self.update_answers_file("HEE_ADMIN_PASSWORD", self.w_engine_admin_password.get_edit_text())
            host_hostname = socket.gethostname()
            self.update_answers_file("HEE_APP_HOSTNAME", host_hostname)
            self.update_answers_file("HES_DOMAIN_TYPE", self.get_radio_option(self.w_storage_type))
            self.update_storage_domain_config()
            self.update_answers_file("HEV_CLOUDINIT_ROOT_PWD", self.w_engine_root_password.get_edit_text())
            self.update_answers_file("HEV_VM_MAC_ADDR", self.w_engine_mac_addr.get_edit_text())
            self.update_answers_file("HEV_OVF_ARCHIVE", self.get_ova_file("/usr/share/ovirt-engine-appliance/"))
            self.update_answers_file("HEV_CLOUDINIT_INSTANCE_DOMAIN_NAME",
                '.'.join(self.w_engine_hostname.get_edit_text().split('.')[-2:]))
            self.update_answers_file("HEV_CLOUDINIT_INSTANCE_HOSTNAME", self.w_engine_hostname.get_edit_text())
            self.update_answers_file("HEV_CLOUDINIT_VM_STATIC_CIDR", self.w_engine_static_cidr.get_edit_text())
            self.update_answers_file("HEVD_SPICE_PKI_SUBJECT_O", '.'.join(host_hostname.split('.')[-2:]))
            self.update_answers_file("HEVD_SPICE_PKI_SUBJECT_CN", host_hostname)
            host_vcpu_count = psutil.cpu_count(logical=True)
            self.update_answers_file("HEV_VM_VCPUS", str(min(max(min(2, host_vcpu_count), host_vcpu_count/2), 4)))
            self.begin_setup_screen()

    def begin_setup_existing(self, button):
        if self.validate_setup_input_existing():
            os.system("cp /etc/eayunos-console-node/answers_add.conf %s" % self.answers_path)
            self.update_answers_file("HEE_ADMIN_PASSWORD", self.w_engine_admin_password.get_edit_text())
            self.update_answers_file("HEE_APP_HOSTNAME", socket.gethostname())
            self.update_answers_file("HES_DOMAIN_TYPE", self.get_radio_option(self.w_storage_type))
            self.update_storage_domain_config()
            self.update_answers_file("HEN_BRIDGE_IF", self.get_radio_option(self.w_bridge_if))
            self.update_answers_file("HES_HOST_ID", self.w_host_id.get_edit_text())
            self.begin_setup_screen()

    def begin_setup_screen(self):
        os.system("screen -X -S hosted_engine_setup quit")
        os.system("screen -dmS hosted_engine_setup")
        os.system("rm -f %s" % self.setup_log_path)
        os.system("touch %s" % self.setup_log_path)
        os.system("screen -S hosted_engine_setup -X stuff 'ovirt-hosted-engine-setup --config-append=%s |tee %s\n'" % (self.answers_path, self.setup_log_path))
        self.widget.original_widget = self.get_setup_widget()

    def get_radio_option(self, radiobutton_group):
        for button in radiobutton_group:
            if button.get_state():
                return button.get_label()

    def update_storage_domain_nfs(self, button, selected):
        if selected:
            self.w_storage_connection._set_widget_list([self.w_storage_connection_nfs])

    def update_storage_domain_iscsi(self, button, selected):
        if selected:
            self.w_storage_connection._set_widget_list([self.w_storage_connection_iscsi])

    def update_storage_domain_fc(self, button, selected):
        if selected:
            self.w_storage_connection._set_widget_list([self.w_storage_connection_fc])

    def get_fc_lun_tuple_list(self):
        # workaround for vdsm check before use vdscli:
        if os.system("service vdsmd status|grep 'active (running)' &>/dev/null"):
            os.system("service sanlock stop")
            os.system("service libvirtd stop")
            os.system("service supervdsmd stop")
            os.system("vdsm-tool configure")
            os.system("service vdsmd restart")
            # workaround for imageio-daemon start success
            os.system("service ovirt-imageio-daemon restart")
        connecting = True
        fc_lun_list = []
        FC_DOMAIN = 2
        while connecting:
            try:
                cli = vdscli.connect(timeout=900)
                devices = cli.getDeviceList(FC_DOMAIN)
                connecting = False
            except socket_error as serr:
                if serr.errno == errno.ECONNREFUSED:
                    time.sleep(2)
                else:
                    raise serr
        if devices['status']['code']:
            raise RuntimeError(devices['status']['message'])
        for device in devices['devList']:
            device_info = "%s  %sGiB\n%s %s  status: %s" % (
                    device["GUID"], int(device['capacity']) / pow(2, 30),
                    device['vendorID'], device['productID'], device["status"],
                )
            fc_lun_list.append((device_info, None))
        return fc_lun_list

    def update_answers_file(self, key, value):
        os.system("sed -i s/{%s}/%s/ %s" % (key, value.replace("/","\\\/"), self.answers_path))

    def update_storage_domain_config(self):
        if self.get_radio_option(self.w_storage_type) == "nfs3":
            self.update_answers_file("HES_STORAGE_DOMAIN_CONNECTION", self.w_storage_connection_nfs.get_edit_text())
            self.update_answers_file("HES_LUN_ID", "none:None")
        elif self.get_radio_option(self.w_storage_type) == "fc":
            self.update_answers_file("HES_LUN_ID", self.get_radio_option(self.w_lun_list).split("  ")[0])
            self.update_answers_file("HES_STORAGE_DOMAIN_CONNECTION", "none:None")

    def get_ova_file(self, ovs_dir):
        for f in os.listdir(ovs_dir):
            if f.endswith('.ova'):
                return ovs_dir + f

    def validate_setup_input(self):
        # TODO
        return True

    def validate_setup_input_existing(self):
        # TODO
        return True

    def get_setup_widget(self):
        widget = urwid.BoxAdapter(urwid.Frame(
            header=urwid.Text("Setup output:"),
            body=urwid.Filler(self.output, valign="bottom"),
            footer=urwid.Button("percentage"),
            focus_part="header"), 50)
        widget.set_focus("footer")
        poll_thread = threading.Thread(target=self.poll_setup_status)
        poll_thread.setDaemon(True)
        poll_thread.start()
        return widget

    def poll_setup_status(self):
        while True:
            time.sleep(2)
            if "running" == self.get_hosted_engine_status():
                # TODO
                self.widget.original_widget = self.get_status_widget()
                self.main_loop.draw_screen()
                return
            if "stopped" == self.get_hosted_engine_status():
                os.system("echo '\n\n\n' >> %s" % self.setup_log_path)
            self.output.set_text(subprocess.check_output(["tail", "-n", "30", self.setup_log_path]))
            self.main_loop.draw_screen()
            if "stopped" == self.get_hosted_engine_status():
                return

    def get_status_widget(self):
        return urwid.Button(u"Hosted engine is running.")

    def get_hosted_engine_status(self):
        s = subprocess.Popen(["ps", "axw"],stdout=subprocess.PIPE)
        for x in s.stdout:
            if re.search("ovirt-hosted-engine-setup", x):
                return "setting_up"
        if os.path.exists("/var/run/ovirt-hosted-engine-ha/agent.pid"):
            return "running"
        else:
            return "stopped"

    def random_MAC(self):
        mac = [
            '00',
            '16',
            '3e',
            '%02x' % random.randint(0x00, 0x7f),
            '%02x' % random.randint(0x00, 0xff),
            '%02x' % random.randint(0x00, 0xff),
        ]
        return ':'.join(mac)

    def get_default_gw(self):
        ROUTE_DESTINATION = 1
        ROUTE_GW = 2
        gateway = None
        with open('/proc/net/route', 'r') as f:
            lines = f.read().splitlines()
            for line in lines:
                data = line.split()
                if data[ROUTE_DESTINATION] == '00000000':
                    gateway = socket.inet_ntoa(
                        struct.pack(
                            'I',
                            int(data[ROUTE_GW], 16)
                        )
                    )
                    break
        return str(gateway)

class WidgetWithPopup(urwid.PopUpLauncher):

    def __init__(self, widget):
        urwid.PopUpLauncher.__init__(self, widget)

    def create_pop_up(self):
        self.pop_up = CleanupDialog()
        urwid.connect_signal(self.pop_up, 'close',
            lambda button: self.close_pop_up())
        return self.pop_up

    def get_pop_up_parameters(self):
        return {'left':0, 'top':1, 'overlay_width':32, 'overlay_height':7}

    def cleanup_finish(self):
        self.pop_up.cleanup_finish()


class CleanupDialog(urwid.WidgetWrap):

    signals = ['close']

    def __init__(self):
        urwid.WidgetWrap.__init__(self, None)
        self.close_button = urwid.Button("OK")
        urwid.connect_signal(self.close_button, 'click',
            lambda button:self._emit("close"))
        self.__super.__init__(
            urwid.AttrWrap(
                urwid.Filler(
                    urwid.Pile([
                        urwid.Text("Cleaning up..."),
                    ])), 'popbg'))

    def cleanup_finish(self):
        self._set_w(
            urwid.AttrWrap(
                urwid.Filler(
                    urwid.Pile([
                        urwid.Text("Cleanup sucess"),
                        self.close_button,
                    ])), 'popbg'))

