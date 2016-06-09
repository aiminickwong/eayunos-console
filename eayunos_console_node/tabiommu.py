import os
import urwid
from eayunos_console_common.configtab import SimplePopupLauncher, SimplePopupDialog


class TabIOMMU(object):

    def __init__(self, main_loop):
        self.main_loop = main_loop
        self.name = u"IOMMU Config"
        self.widget = SimplePopupLauncher(self.get_widget(), "Config success! Please reboot the system to let the config take effect.")

    def get_widget(self):
        if os.system("cat /etc/default/grub|grep iommu &>/dev/null"):
            return urwid.Pile([
                urwid.Text(u"IOMMU is disabled."),
                urwid.Button(u"Enable IOMMU", on_press=self.enable_iommu)
            ])
        else:
            return urwid.Pile([
                urwid.Text(u"IOMMU is enabled."),
                urwid.Button(u"Disable IOMMU", on_press=self.disable_iommu)
            ])

    def disable_iommu(self, button):
        os.system("sed -i 's/intel_iommu=on//g' /etc/default/grub")
        os.system("sed -i 's/amd_iommu=on//g' /etc/default/grub")
        os.system("sed -i 's/[ \t]*$//' /etc/default/grub")
        os.system("sed -i 's/[ \t]*\"$/\"/' /etc/default/grub")
        self.apply_grub_config()

    def enable_iommu(self, button):
        if os.system("cat /etc/default/grub|grep iommu &>/dev/null"):
            os.system("sed -i 's/[ \t]*$//' /etc/default/grub")
            os.system("sed -i '/^GRUB_CMDLINE_LINUX/ s/\"$/ intel_iommu=on\"/' /etc/default/grub")
            os.system("sed -i '/^GRUB_CMDLINE_LINUX/ s/\"$/ amd_iommu=on\"/' /etc/default/grub")
        self.apply_grub_config()

    def apply_grub_config(self):
        os.system("grub2-mkconfig -o /boot/grub2/grub.cfg")
        self.widget.open_pop_up()
