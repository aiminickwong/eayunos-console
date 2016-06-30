import os
import time
import urwid
from eayunos_console_common.configtab import SimplePopupLauncher, SimplePopupDialog

from ovirtsdk.api import API
from ovirtsdk.xml import params


class TabNeutron(object):

    def __init__(self, main_loop):
        self.main_loop = main_loop
        self.name = u"Neutron Deploy"
        self.vm_name = "NeutronAppliance"
        self.widget = SimplePopupLauncher(self.get_pass(),
            "Vm named '%s' exists, please remove or rename it and try again" % self.vm_name)

    def get_pass(self):
        self.w_password = urwid.Edit(u"Please enter admin@internal password to procceed: ", mask="*")
        return urwid.Columns([
            ('weight', 4, self.w_password),
            ('weight', 1, urwid.Button(u"GO", on_press=self.on_pass))
        ])

    def on_pass(self, button):
        self.api = API(url='https://127.0.0.1/api',
            username='admin@internal',
            password=self.w_password.edit_text.encode("ascii", "ignore"),
            insecure=True)
        if not self.api.vms.get(name=self.vm_name) == None:
            self.widget.open_pop_up()
            return
        divider = urwid.Divider("-")
        self.w_mgmt_profile = VnicProfileSelector(self.api, True, self.vnic_profile_changed_mgmt)
        self.w_int_profile = VnicProfileSelector(self.api, True, self.vnic_profile_changed_int)
        self.w_int_profile.set_ip_info(False)
        self.w_ext_profile = VnicProfileSelector(self.api, False, None)
        self.w_vm_pass = urwid.Edit(u"vm root password: ", mask="*")
        self.w_keystone_pass = urwid.Edit(u"keystone admin password: ", mask="*")
        self.widget.original_widget = urwid.Pile([
            urwid.Text(u"Deploying neutron appliance under datacenter 'Default'"),
            divider,
            urwid.Text("Choose profile for management network:"),
            self.w_mgmt_profile,
            divider,
            urwid.Text("Choose profile for internal network:"),
            self.w_int_profile,
            divider,
            urwid.Text("Choose profile for external network:"),
            self.w_ext_profile,
            divider,
            self.w_vm_pass,
            self.w_keystone_pass,
            divider,
            urwid.Button(u"OK", on_press=self.begin_deploy)
        ])

    def vnic_profile_changed_mgmt(self, button, selected):
        if selected:
            os.system("echo %s : %s >> /tmp/ply" % (self.w_mgmt_profile.get_vnic_profile_id_by_name(button.get_label()), self.w_int_profile.get_vnic_profile_id()))
            if self.w_mgmt_profile.get_vnic_profile_id_by_name(button.get_label()) == self.w_int_profile.get_vnic_profile_id():
                self.w_int_profile.set_ip_info(False)
            else:
                self.w_int_profile.set_ip_info(True)
            self.main_loop.draw_screen()

    def vnic_profile_changed_int(self, button, selected):
        if selected:
            os.system("echo %s : %s >> /tmp/ply" % (self.w_mgmt_profile.get_vnic_profile_id(), self.w_int_profile.get_vnic_profile_id_by_name(button.get_label())))
            if self.w_mgmt_profile.get_vnic_profile_id() == self.w_int_profile.get_vnic_profile_id_by_name(button.get_label()):
                self.w_int_profile.set_ip_info(False)
            else:
                self.w_int_profile.set_ip_info(True)

    def begin_deploy(self, button):
        self.output = urwid.Text("")
        widget = urwid.BoxAdapter(urwid.Frame(
            header=urwid.Text("Setup output:"),
            body=urwid.Filler(self.output, valign="bottom"),
            footer=urwid.Button("percentage"),
            focus_part="header"), 20)
        widget.set_focus("footer")
        self.widget.original_widget = widget
        self.log(u"Begin neutron appliance deploy")
        self.add_vm()
        self.add_external_provider()
        self.configure_uiplugin()
        self.configure_httpd()
        self.log(u"Neutron appliance deploy finished, please REFRESH your webadmin page")
        self.api.disconnect()

    def log(self, text):
        self.output.set_text(self.output.text + text + "\n")
        self.main_loop.draw_screen()

    def add_vm(self):
        mgmt_int_same = self.w_mgmt_profile.get_vnic_profile_id() == self.w_int_profile.get_vnic_profile_id()
        template_name = "Neutron_Appliance_Template"
        nics = []
        nics.append(params.NIC(
            name="eth0",
            boot_protocol="STATIC",
            on_boot=True,
            network=params.Network(
                ip=params.IP(
                    address=self.w_mgmt_profile.w_ip.edit_text,
                    netmask=self.w_mgmt_profile.w_netmask.edit_text,
                    gateway=self.w_mgmt_profile.w_gateway.edit_text,
                )
            )
        ))
        if not mgmt_int_same:
            nics.append(params.NIC(
                name="eth2",
                boot_protocol="STATIC",
                on_boot=True,
                network=params.Network(
                    ip=params.IP(
                        address=self.w_int_profile.w_ip.edit_text,
                        netmask=self.w_int_profile.w_netmask.edit_text,
                        gateway=self.w_int_profile.w_gateway.edit_text,
                    )
                )
            ))
        nics.append(params.NIC(
            name="eth1",
            boot_protocol="NONE",
            on_boot=True,
        ))
        vm=params.VM(
            name=self.vm_name,
            cluster=self.api.clusters.get(name="Default"),
            template=self.api.templates.get(name=template_name),
        )
        self.log(u"Adding neutron vm")
        self.api.vms.add(vm)
        self.log(u"Neutron vm added successflly")
        self.api.vms.get(self.vm_name).nics.add(params.NIC(
            name='eth0',
            vnic_profile=params.VnicProfile(id=self.w_mgmt_profile.get_vnic_profile_id()),
            interface='virtio'
        ))
        self.log("NIC 'eth0' added to neutron vm as management network")
        self.api.vms.get(self.vm_name).nics.add(params.NIC(
            name='eth1',
            vnic_profile=params.VnicProfile(id=self.w_ext_profile.get_vnic_profile_id()),
            interface='virtio'
        ))
        self.log("NIC 'eth1' added to neutron vm as external network")
        if not mgmt_int_same:
            self.api.vms.get(self.vm_name).nics.add(params.NIC(
                name='eth2',
                vnic_profile=params.VnicProfile(id=self.w_int_profile.get_vnic_profile_id()),
                interface='virtio'
            ))
            self.log("NIC 'eth2' added to neutron vm as internal network")

        cloud_init_content = """runcmd:
 - sed -i 's/ServerAlias 127.0.0.1/ServerAlias %s/' /etc/httpd/conf.d/15-horizon_vhost.conf
 - sed -i 's/local_ip =127.0.0.1/local_ip = %s/' /etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini
 - sed -i 's/#CSRF_COOKIE_SECURE/CSRF_COOKIE_SECURE/' /etc/openstack-dashboard/local_settings
 - sed -i 's/#SESSION_COOKIE_SECURE/SESSION_COOKIE_SECURE/' /etc/openstack-dashboard/local_settings
 - service httpd restart
 - service neutron-openvswitch-agent restart
 - source /root/keystonerc_admin
 - keystone user-password-update --pass %s admin
 - sed -i '/^export OS_PASSWORD/c\export OS_PASSWORD=%s' /root/keystonerc_admin""" % (
                self.w_mgmt_profile.w_ip.edit_text,
                self.w_mgmt_profile.w_ip.edit_text if mgmt_int_same else self.w_int_profile.w_ip.edit_text,
                self.w_keystone_pass.edit_text,
                self.w_keystone_pass.edit_text,
            )

        initialization=params.Initialization(
            cloud_init=params.CloudInit(
                host=params.Host(address="localhost"),
                regenerate_ssh_keys=True,
                users=params.Users(
                    user=[params.User(user_name="root", password=self.w_vm_pass.edit_text)]
                    ),
                network_configuration=params.NetworkConfiguration(
                    nics=params.Nics(nic=nics)
                ),
                files=params.Files(
                    file=[params.File(name="/tmp/setup", type_="PLAINTEXT", content=cloud_init_content,)]
                )
            )
        )
        self.log("Wait for vm to be created...")
        created = False
        while not created:
            time.sleep(10)
            if "down" == self.api.vms.get(name=self.vm_name).status.state:
                created = True
        self.log("Starting vm...")
        vm = self.api.vms.get(name=self.vm_name)
        vm.start(
            action=params.Action(
                use_cloud_init=True,
                vm=params.VM(
                    initialization=initialization
                )
            )
        )

    def add_external_provider(self):
        external_provider_name = "neutron-appliance"
        if not self.api.openstacknetworkproviders.get(name=external_provider_name) == None:
            self.log("Removing existing external provider: %s ..." % external_provider_name)
            self.api.openstacknetworkproviders.get(name=external_provider_name).delete()
        self.log(u"Adding external provider...")
        agent_configuration = params.AgentConfiguration(
            network_mappings='vmnet:br-tun',
            broker_type='rabbit_mq',
            address=self.w_mgmt_profile.w_ip.edit_text,
            port=5672,
            username='guest',
            password='guest',
        )
        self.api.openstacknetworkproviders.add(params.OpenStackNetworkProvider(
            name=external_provider_name,
            description='auto created by eayunos',
            url='http://%s:9696' % self.w_mgmt_profile.w_ip.edit_text,
            requires_authentication=True,
            username='admin',
            password=self.w_password.edit_text.encode("ascii", "ignore"),
            authentication_url='http://%s:5000/v2.0/' % self.w_mgmt_profile.w_ip.edit_text,
            tenant_name='admin',
            plugin_type='OPEN_VSWITCH',
            agent_configuration=agent_configuration,
        ))
        self.log(u"External provider added successfully")

    def configure_uiplugin(self):
        os.system("ln -nsf /usr/share/neutron-uiplugin/neutron-resources /usr/share/ovirt-engine/ui-plugins/neutron-resources")
        os.system("ln -nsf /usr/share/neutron-uiplugin/neutron.json /usr/share/ovirt-engine/ui-plugins/neutron.json")
        self.log("Neutron uiplugin configured")

    def configure_httpd(self):
        content = """ProxyPass "/dashboard" "http://{IP}/dashboard"
ProxyPassReverse "/dashboard" "http://{IP}/dashboard"
ProxyPass "/static" "http://{IP}/static"
ProxyPassReverse "/static" "http://{IP}/static"
""".replace("{IP}", self.w_mgmt_profile.w_ip.edit_text)
        with open("/etc/httpd/conf.d/z-neutron.conf", "w") as f:
            f.write(content)
        self.log("Restarting httpd service")
        os.system("service httpd restart")
        self.log("Httpd reverse proxy configured")


class VnicProfileSelector(urwid.Pile):

    def __init__(self, api, ip_info, vnic_callback):
        self.api = api
        self.ip_info = ip_info
        self.vnic_callback = vnic_callback
        self.vnic_profile_map = {}
        self.w_nets_opts = []
        self.w_profs_opts = []
        networks = self.api.networks.list(query="datacenter=Default")
        vnic_profiles = networks[0].vnicprofiles.list()
        for profile in vnic_profiles:
            self.vnic_profile_map[profile.name] = profile.id
        self.w_nets = urwid.AttrMap("", "")
        self.w_nets.original_widget = self.genRadioButton(
            u"Networks: ",
            [(net.name, self.network_changed) for net in networks],
            self.w_nets_opts)
        self.w_profs = urwid.AttrMap("", "")
        self.w_profs.original_widget = self.genRadioButton(
            u"Vnic Profiles: ",
            [(prof.name, None) for prof in vnic_profiles],
            self.w_profs_opts)

        widget_list = [
            self.w_nets,
            self.w_profs,
        ]
        if self.ip_info:
            self.w_ip = urwid.Edit(u"IP: ")
            self.w_netmask = urwid.Edit(u"Netmask(xxx.xxx.xxx.xxx): ")
            self.w_gateway = urwid.Edit(u"Gateway: ")
            widget_list.extend([
                self.w_ip,
                self.w_netmask,
                self.w_gateway,
            ])
        urwid.Pile.__init__(self, widget_list)

    def network_changed(self, button, selected):
        if selected:
            self.refresh_vnic_profiles(button.get_label())
            if self.ip_info:
                self.vnic_callback(self.w_profs_opts[0], True)

    def refresh_vnic_profiles(self, network_name):
        vnic_profiles = self.api.networks.list(query="datacenter=Default and name=%s" % network_name)[0].vnicprofiles.list()
        self.vnic_profile_map = {}
        for profile in vnic_profiles:
            self.vnic_profile_map[profile.name] = profile.id
        self.w_profs_opts = []
        self.w_profs.original_widget = self.genRadioButton(
            u"Vnic Profiles: ",
            [(prof.name, self.vnic_callback) for prof in vnic_profiles],
            self.w_profs_opts)

    def genRadioButton(self, caption_text, options, radiobutton_group):
        radio_button_liust = [
            urwid.RadioButton(radiobutton_group, option[0], on_state_change=option[1]) for option in options]
        return urwid.Columns([
                ('pack', urwid.Text(caption_text)),
                urwid.GridFlow(radio_button_liust, 30, 2, 0, 'left'),
            ])

    def get_radio_option(self, radiobutton_group):
        for button in radiobutton_group:
            if button.get_state():
                return button.get_label()

    def get_vnic_profile_id(self):
        try:
            id = self.vnic_profile_map[self.get_radio_option(self.w_profs_opts)]
        except KeyError:
            return ""
        return id

    def get_vnic_profile_id_by_name(self, profile_name):
        try:
            id = self.vnic_profile_map[profile_name]
        except KeyError:
            return ""
        return id

    def set_ip_info(self, ip_info):
        widget_list = [
            self.w_nets,
            self.w_profs,
        ]
        if ip_info:
            widget_list.extend([
                self.w_ip,
                self.w_netmask,
                self.w_gateway,
            ])
        self._set_widget_list(widget_list)

