# _*_ coding:utf-8 _*_

import urwid
from common import ConfigTab
from manager_console import Product, LogIn, CheckBox, TabEngineSetup, TabNetwork

palette = [
       ('I say', 'yellow', 'light gray', 'bold'),
       ('btn', 'yellow', 'light gray', 'bold'),
       ('banner', 'yellow', 'light gray'),
       ('streak', 'yellow', 'light gray'),
       ('buttnf','white','dark blue','bold'),
       ]

loop = urwid.MainLoop(None, palette, pop_ups=True)

#l = LogIn(loop)
p = Product(loop)
l = LogIn(loop, p)
c = CheckBox(loop)
config_tab_list = [
    TabNetwork(loop),
    TabEngineSetup(),
]


go_trial = ConfigTab(config_tab_list)
go_login = l.get_widget()
go_product = p.get_widget()
go_checkbox = c.get_widget()

l.set_widgetList_other(go_trial, go_product)
p.set_widgetList_other(go_login, go_checkbox)
c.set_widgetList_other(go_product, go_login)

loop.widget = go_login

if __name__ == '__main__':
   loop.run()
