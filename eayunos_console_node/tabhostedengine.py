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

    def get_pre_setup_widget(self):
        blank = urwid.Divider()
        self.w_gateway = urwid.Edit(u"Gateway: ", self.get_default_gw())
        self.w_bridge_if = []
        self.w_engine_hostname = urwid.Edit(u"Engine hostname: ")
        self.w_engine_static_cidr = urwid.Edit(u"Engine static CIDR: ")
        self.w_engine_mac_addr = urwid.Edit(u"Engine MAC address: ", self.random_MAC())
        self.w_engine_root_password = urwid.Edit(u"Engine root user password: ", mask="*")
        self.w_engine_admin_password = urwid.Edit(u"Engine admin@internal password: ", mask="*")
        self.w_storage_type = []
        self.w_storage_connection = urwid.Edit(u"Storage connection: ")
        return urwid.Pile([
            urwid.Text("Setup configuration: "),
            urwid.Divider("-"),
            blank,
            self.w_gateway,
            self.genRadioButton(u"Interface to set eayunos bridge on: ",
                [nic.name for nic in ifconfig.iterifs()], self.w_bridge_if),
            blank,
            self.w_engine_hostname,
            self.w_engine_static_cidr,
            self.w_engine_mac_addr,
            self.w_engine_root_password,
            self.w_engine_admin_password,
            blank,
            self.genRadioButton(u"Storage type: ", ["nfs3", "iscsi", "fc"], self.w_storage_type),
            self.w_storage_connection,
            blank,
            urwid.Button("Begin setup", on_press=self.begin_setup),
        ])

    def genRadioButton(self, caption_text, options, selected_value):
        return urwid.Columns([
                ('pack', urwid.Text(caption_text)),
                urwid.GridFlow([
                    urwid.RadioButton(selected_value, txt) for txt in options
                    ], 13, 2, 0, 'left'),
            ])

    def begin_setup(self, button):
        if self.validate_setup_input():
            script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
            os.system("cp /etc/eayunos-console-node/answers.conf %s" % self.answers_path)
            self.update_answers_file("HEN_GATEWAY", self.w_gateway.get_edit_text())
            self.update_answers_file("HEN_BRIDGE_IF", self.get_radio_option(self.w_bridge_if))
            self.update_answers_file("HEE_ADMIN_PASSWORD", self.w_engine_admin_password.get_edit_text())
            self.update_answers_file("HEE_APP_HOSTNAME", self.w_engine_hostname.get_edit_text())
            self.update_answers_file("HES_DOMAIN_TYPE", self.get_radio_option(self.w_storage_type))
            self.update_answers_file("HES_STORAGE_DOMAIN_CONNECTION", self.w_storage_connection.get_edit_text())
            self.update_answers_file("HEV_CLOUDINIT_ROOT_PWD", self.w_engine_root_password.get_edit_text())
            self.update_answers_file("HEV_VM_MAC_ADDR", self.w_engine_mac_addr.get_edit_text())
            self.update_answers_file("HEV_OVF_ARCHIVE", self.get_ova_file("/usr/share/ovirt-engine-appliance/"))
            self.update_answers_file("HEV_CLOUDINIT_INSTANCE_DOMAIN_NAME",
                '.'.join(self.w_engine_hostname.get_edit_text().split('.')[-2:]))
            self.update_answers_file("HEV_CLOUDINIT_INSTANCE_HOSTNAME", self.w_engine_hostname.get_edit_text())
            self.update_answers_file("HEV_CLOUDINIT_VM_STATIC_CIDR", self.w_engine_static_cidr.get_edit_text())
            host_hostname = socket.gethostname()
            self.update_answers_file("HEVD_SPICE_PKI_SUBJECT_O", '.'.join(host_hostname.split('.')[-2:]))
            self.update_answers_file("HEVD_SPICE_PKI_SUBJECT_CN", host_hostname)
            host_vcpu_count = psutil.cpu_count(logical=True)
            self.update_answers_file("HEV_VM_VCPUS", str(min(max(min(2, host_vcpu_count), host_vcpu_count/2), 4)))
            os.system("screen -X -S hosted_engine_setup quit")
            os.system("screen -dmS hosted_engine_setup")
            os.system("rm -f %s" % self.setup_log_path)
            os.system("touch %s" % self.setup_log_path)
            os.system("screen -S hosted_engine_setup -X stuff 'ovirt-hosted-engine-setup --config-append=%s &>%s\n'" % (self.answers_path, self.setup_log_path))
            self.widget.original_widget = self.get_setup_widget()

    def get_radio_option(self, radiobutton_widget):
        for button in radiobutton_widget:
            if button.get_state():
                return button.get_label()

    def update_answers_file(self, key, value):
        os.system("sed -i s/{%s}/%s/ %s" % (key, value.replace("/","\\\/"), self.answers_path))

    def get_ova_file(self, ovs_dir):
        for f in os.listdir(ovs_dir):
            if f.endswith('.ova'):
                return ovs_dir + f

    def validate_setup_input(self):
        # TODO
        return True

    def get_setup_widget(self):
        widget = urwid.BoxAdapter(urwid.Frame(
            header=urwid.Text("Setup output:"),
            body=urwid.Filler(self.output, valign="bottom"),
            footer=urwid.Button("percentage"),
            focus_part="header"), 30)
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
        return gateway

