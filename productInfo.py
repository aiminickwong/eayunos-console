# _*_ coding:utf-8 _*_

import os
import urwid

class Product(object):

   def __init__(self, loop):
      self.widgetList = []
      self.widgetList.append(self.top)
      self.widgetList.append(self.palette)
      self.loop = loop
      urwid.connect_signal(self.button_product, 'click', self.on_product_clicked)
      urwid.connect_signal(self.button_next, 'click', self.on_next_clicked)
      urwid.connect_signal(self.button_exit, 'click', self.on_exit_clicked)
   
   def set_widgetList_other(self, go_login = [None, None], go_checkbox = [None, None]):
      self.go_login_widget = go_login[0]
      self.go_login_palette = go_login[1]
      self.go_checkbox_widget = go_checkbox[0]
      self.go_checkbox_palette = go_checkbox[1]

   palette = [
         ('banner', 'yellow', 'light gray'),
         ('streak', 'yellow', 'light gray'),
         ('btn', 'yellow', 'light gray', 'bold'),
         ]

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

   product_list = [button_product, txtInfo]
   button_list = [button_exit, button_next]

   # 架构信息
   product_div = urwid.GridFlow([urwid.AttrWrap(txt, 'streak')], 38, 5, 0, 'center')
   # 产品信息按钮
   button_product_div = urwid.GridFlow([urwid.AttrWrap(button_product, 'btn')], 15, 5, 0, 'center')
   # 显示信息
   product_info_div = urwid.GridFlow([urwid.AttrWrap(txtInfo, 'streak')], 50, 5, 0, 'left')
   # 返回按钮 & 下一步按钮
   button_div = urwid.GridFlow([urwid.AttrWrap(button, 'btn', 'btn') for button in button_list], 10, 5, 0, 'center')
   div = urwid.Divider()

   pile = urwid.Pile([product_div, div, button_product_div, div, div, button_div])


   def on_product_clicked(self, button):
      pile = urwid.Pile([self.product_div, self.div, self.product_info_div, self.div, self.button_div])
      new_top = urwid.Filler(pile, valign='top')
      self.loop.widget = new_top

   def on_exit_clicked(self, button):
      self.loop.widget = self.go_login_widget
      self.loop.palette = self.go_login_palette
   
   def on_next_clicked(self, button):
      self.loop.widget = self.go_checkbox_widget
      self.loop.palette = self.go_checkbox_palette


   top = urwid.Filler(pile, valign='top')
   
   def get_widget(self):
      return self.widgetList 
