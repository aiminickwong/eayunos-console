# _*_ coding:utf-8 _*_

import os
import urwid

class Product(object):

   def __init__(self, loop):
      self.loop = loop
      self.username = 'init'
      self.password = 'init'
      self.key = 'init'

      # 组件定义
      self.txt = urwid.Text(u"当前产品架构：非 HostedEngine", align = 'center')
      self.button_product = urwid.Button(u'查看产品信息')
      self.button_exit = urwid.Button(u'返回')
      self.button_next = urwid.Button(u'下一步')
      self.button_list = [self.button_exit, self.button_next]
      self.div = urwid.Divider()

      # 架构信息 Text
      self.product_div = urwid.GridFlow([urwid.AttrWrap(self.txt, 'streak')], 38, 5, 0, 'center')
      # 产品信息按钮 Button
      self.button_product_div = urwid.GridFlow([urwid.AttrWrap(self.button_product, 'btn')], 15, 5, 0, 'center')
      # 返回按钮 & 下一步按钮 Button
      self.button_div = urwid.GridFlow([urwid.AttrWrap(button, 'btn', 'btn') for button in self.button_list], 10, 5, 0, 'center')

      # 页面显示：txt + div + 产品信息 btn + div + div + 返回 btn & 下一步 btn
      self.pile = urwid.Pile([self.product_div, self.div, self.button_product_div, self.div, self.div, self.button_div])
      self.top = urwid.Filler(self.pile, valign='top')

      urwid.connect_signal(self.button_product, 'click', self.on_product_clicked)
      urwid.connect_signal(self.button_next, 'click', self.on_next_clicked)
      urwid.connect_signal(self.button_exit, 'click', self.on_exit_clicked)

   # 生成信息组件
   def generateInfo(self):
      valid = 'admin'
      if (self.get_username() == valid) and (self.get_password() == valid):
         # self.info 返回值类型是个列表
         #self.info = os.popen('subscription-manager orgs --username=admin --password=admin').readlines()
         self.info = os.popen('date').readlines()
         #info = os.popen('subscription-manager list --all --available').readlines()
         #info = os.popen('subscription-manager orgs --username=admin').readlines()

         # 目的：将返回的列表类型的信息转换成字符串类型
         self.info_txt = ''
         for i in range(len(self.info)):
            text = self.info[i]
            self.info_txt += text

         # 新的组件：显示的是产品信息
         self.txtInfo = urwid.Text(self.info_txt, align = 'center')

         # 显示信息 Text
         self.product_info_div = urwid.GridFlow([urwid.AttrWrap(self.txtInfo, 'streak')], 50, 5, 0, 'left')
         self.pile = urwid.Pile([self.product_div, self.div, self.product_info_div, self.div, self.button_div])
         new_top = urwid.Filler(self.pile, valign='top')
         self.loop.widget = new_top
      else:
         self.text = urwid.Text(self.get_password() + self.get_username())
         self.loop.widget = urwid.Filler(self.text)

   # 为了获取到 login 中的登录信息
   def set_username(self, username):
      self.username = username
   def get_username(self):
      return self.username
   def set_password(self, password):
      self.password = password
   def get_password(self):
      return self.password
   def set_key(self, key):
      self.key = key
   def get_key(self):
      return self.key

   # 设置 exit 和 next 页面的 widget
   def set_widgetList_other(self, go_login, go_checkbox):
      self.go_login_widget = go_login
      self.go_checkbox_widget = go_checkbox

   # 回调函数
   def on_product_clicked(self, button):
      self.generateInfo()

   def on_exit_clicked(self, button):
      self.loop.widget = self.go_login_widget

   def on_next_clicked(self, button):
      self.loop.widget = self.go_checkbox_widget

   # 获取到 product 页面的 widget
   def get_widget(self):
      return self.top
