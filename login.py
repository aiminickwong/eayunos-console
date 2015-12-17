# _*_ coding: utf-8 _*_

import urwid
import globalInput
import ProductInfo

class LogIn(object):

   def __init__(self, loop):
       self.loop = loop
       self.ask_username = urwid.Edit(('I say', u"用户名： "))
       self.ask_password = urwid.Edit(('I say', u"\n密码： "))
       self.ask_key = urwid.Edit(('I say', u"\nkey: "))
       self.reply = urwid.Text(u"")
       self.div = urwid.Divider()
       self.button_tryout = urwid.Button(u'  试用')
       self.button_next = urwid.Button(u' 下一步')
       self.button_list = [self.button_tryout, self.button_next]

       urwid.connect_signal(self.ask_username, 'change', self.on_ask_username_change)
       urwid.connect_signal(self.ask_password, 'change', self.on_ask_password_change)
       urwid.connect_signal(self.ask_key, 'change', self.on_ask_key_change)
       urwid.connect_signal(self.button_tryout, 'click', self.go_to_try_out)
       urwid.connect_signal(self.button_next, 'click', self.on_next_clicked)
       self.palette = [
       ('I say', 'yellow', 'light gray', 'bold'),
       ('btn', 'yellow', 'light gray', 'bold'),
       ]
       self.button = urwid.GridFlow([urwid.AttrWrap(button, 'btn', 'btn') for button in self.button_list], 12, 5, 0, 'left')
       
       self.pile = urwid.Pile([self.ask_username, self.div, self.ask_password, self.div, self.ask_key, self.div, self.reply, self.button])
       self.top = urwid.Filler(self.pile, valign='top')

       self.widgetList = []
       self.widgetList.append(self.top)
       self.widgetList.append(self.palette)

   def set_widgetList(self, go_trial = [' ', ' '], go_product = [' ', ' ']):
       self.go_trial_widget = go_trial[0]
       self.go_trial_palette = go_trial[1]
       self.go_product_widget = go_product[0]
       self.go_product_palette = go_product[1]

   def set_username(self, username):
      self.username = username

   def get_username(self):
      return username

   def set_password(self, password):
      self.password = password

   def get_password(self):
      return password

   def set_key(self, key):
      self.key = key

   def get_key():
      return key

   def on_ask_username_change(self, edit, new_edit_text):
      self.set_username(str(new_edit_text))
      self.reply.set_text(('I say', u"Nice to meet you, %s" % self.username))

   def on_ask_password_change(self, edit, new_edit_text):
      self.set_password(str(new_edit_text))
      self.reply.set_text(('I say', u"pwd is %s" % self.password))

   def on_ask_key_change(self, edit, new_edit_text):
      self.set_key(str(new_edit_text))
      self.reply.set_text(('I say', u"key is %s" % self.key))

   def go_to_try_out(self, button):
      self.loop.widget = self.go_trial_widget
      self.loop.palette = self.go_trial_palette

   def on_next_clicked(self, button):
      self.loop.widget = self.go_product_widget
      self.loop.palette = self.go_product_palette


   def get_widget(self):
      return self.widgetList
