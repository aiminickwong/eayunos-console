# _*_ coding:utf-8 _*_

import os
import urwid
import checkBox
import Login

palette = [
    ('banner', 'yellow', 'light gray'),
    ('streak', 'yellow', 'light gray'),
    ('btn', 'yellow', 'light gray', 'bold'),]

info = os.popen('date').readlines()
info_txt = ''

for i in range(len(info)):
    text = info[i]
    info_txt += text

txtInfo = urwid.Text(info_txt, align = 'center')

txt = urwid.Text(u"当前产品架构：非 HostedEngine", align = 'center')
#map1 = urwid.AttrMap(txt, 'streak')
#fill = urwid.Filler(map1)

button_product = urwid.Button(u'产品信息')
button_exit = urwid.Button(u'返回')
button_next = urwid.Button(u'下一步')

product_list = [txt, button_product]
button_list = [button_exit, button_next]

product_div = urwid.GridFlow([urwid.AttrWrap(txt, 'streak')], 38, 5, 0, 'center')
button_product_div = urwid.GridFlow([urwid.AttrWrap(button_product, 'btn')], 15, 5, 0, 'center')
product_info_div = urwid.GridFlow([urwid.AttrWrap(txtInfo, 'streak')], 38, 5, 0, 'center')
button_div = urwid.GridFlow([urwid.AttrWrap(button, 'btn', 'btn') for button in button_list], 10, 5, 0, 'center')
div = urwid.Divider()

pile = urwid.Pile([product_div, div, button_product_div, div, div, button_div])

def on_product_clicked(button):
#    pile = urwid.Pile([product_div, div, product_info_div, div, button_div])
#    pile = urwid.Pile([])

def on_next_clicked(button):
    checkBox.run_checkbox()    

def on_exit_clicked(button):
    Login.run_login()
    raise urwid.ExitMainLoop()


urwid.connect_signal(button_product, 'click', on_product_clicked)
urwid.connect_signal(button_next, 'click', on_next_clicked)
urwid.connect_signal(button_exit, 'click', on_exit_clicked)

top = urwid.Filler(pile, valign='top')
loop = urwid.MainLoop(top, palette)
#loop.run()
