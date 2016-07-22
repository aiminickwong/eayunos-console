#coding=utf-8

import os
import urwid
from eayunos_console_common.configtab import SimplePopupLauncher, SimplePopupDialog, Tab


class TabNotifier(Tab):

    def __init__(self, main_loop):
        self.main_loop = main_loop
        self.name = u"Notifier"
        self.notifier_conf_file = "/etc/ovirt-engine/notifier/notifier.conf.d/20-notifier.conf"
        self.mail_server_key = "MAIL_SERVER"
        self.mail_user_key = "MAIL_USER"
        self.mail_pass_key = "MAIL_PASSWORD"
        self.encryption_key = "MAIL_SMTP_ENCRYPTION"
        self.mail_from_key = "MAIL_FROM"
        self.widget = SimplePopupLauncher(self.load_entries(), "Configuration finished.")

    def load_entries(self):
        notifier_conf = {}
        try:
            with open(self.notifier_conf_file) as f:
                for line in f.readlines():
                    if not line.strip():
                        continue
                    if line.startswith("#"):
                        continue
                    items = line.split("=")
                    if len(items) != 2:
                        continue
                    notifier_conf[items[0]] = items[1].rstrip()
        except IOError:
            pass
        self.w_mail_server = urwid.Edit("Mail SMTP server: ", notifier_conf.get(self.mail_server_key, ""))
        self.w_mail_user = urwid.Edit("Authentication user account: ", notifier_conf.get(self.mail_user_key, ""))
        self.w_mail_pass = urwid.Edit("Authentication user password: ", notifier_conf.get(self.mail_pass_key, ""), mask="*")
        self.w_mail_from = urwid.Edit("Mail sender account: ", notifier_conf.get(self.mail_from_key, ""))
        self.encryption_option_list = []
        self.w_encryption = self.genRadioButton(
            "Mail server encryption: ",
            [("none", None), ("ssl", None), ("tls", None)],
            self.encryption_option_list)
        self.set_radio_option(self.encryption_option_list, notifier_conf.get(self.encryption_key, ""))
        return urwid.Pile([
            self.w_mail_server,
            self.w_mail_user,
            self.w_mail_pass,
            self.w_mail_from,
            self.w_encryption,
            urwid.Divider(),
            urwid.Button("Save", on_press=self.save),
        ])

    def save(self, button):
        with open(self.notifier_conf_file,"w") as f:
            f.write("MAIL_SERVER=%s\n" % self.w_mail_server.edit_text.strip())
            f.write("MAIL_USER=%s\n" % self.w_mail_user.edit_text.strip())
            f.write("SENSITIVE_KEYS=\"${SENSITIVE_KEYS},MAIL_PASSWORD\"\n")
            f.write("MAIL_PASSWORD=%s\n" % self.w_mail_pass.edit_text.strip())
            f.write("MAIL_SMTP_ENCRYPTION=%s\n" % self.get_radio_option(self.encryption_option_list))
            f.write("MAIL_FROM=%s\n" % self.w_mail_from.edit_text.strip())
            f.write("HTML_MESSAGE_FORMAT=true\n")
        os.system("service ovirt-engine-notifier restart")
        self.widget.open_pop_up()
