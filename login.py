# _*_ coding: utf-8 _*_

import urwid
import globalInput
import ProductInfo

class LogIn(object):

   def __init__(self, loop):
       self.widgetList = []
       self.widgetList.append(self.top)
       self.widgetList.append(self.palette)
       self.loop = loop
       urwid.connect_signal(self.ask_username, 'change', self.on_ask_username_change)
       urwid.connect_signal(self.ask_password, 'change', self.on_ask_password_change)
       urwid.connect_signal(self.ask_key, 'change', self.on_ask_key_change)
       urwid.connect_signal(self.button_tryout, 'click', self.go_to_try_out)
       urwid.connect_signal(self.button_next, 'click', self.on_next_clicked)

   def set_widgetList(self, go_trial = [' ', ' '], go_product = [' ', ' ']):
       self.go_trial_widget = go_trial[0]
       self.go_trial_palette = go_trial[1]
       self.go_product_widget = go_product[0]
       self.go_product_palette = go_product[1]
   

   ask_username = urwid.Edit(('I say', u"用户名： "))
   ask_password = urwid.Edit(('I say', u"\n密码： "))
   ask_key = urwid.Edit(('I say', u"\nkey: "))
   username = ''
   password = ''
   key = ''

   palette = [
   ('I say', 'yellow', 'light gray', 'bold'),
   ('btn', 'yellow', 'light gray', 'bold'),
   ]

   reply = urwid.Text(u"")

   button_tryout = urwid.Button(u'  试用')
   button_next = urwid.Button(u' 下一步')
   button_list = [button_tryout, button_next]

   #button = urwid.GridFlow([urwid.AttrWrap(button_tryout, button_next], 12, 5, 0, 'left')

   button = urwid.GridFlow([urwid.AttrWrap(button, 'btn', 'btn') for button in button_list], 12, 5, 0, 'left')

   div = urwid.Divider()

   pile = urwid.Pile([ask_username, div, ask_password, div, ask_key, div, reply, button])

   top = urwid.Filler(pile, valign='top')

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
      set_username(str(new_edit_text))
      reply.set_text(('I say', u"Nice to meet you, %s" % new_edit_text))

   def on_ask_password_change(self, edit, new_edit_text):
      set_password(str(new_edit_text))
      reply.set_text(('I say', u"pwd is %s" % password))

   def on_ask_key_change(self, edit, new_edit_text):
      set_key(str(new_edit_text))
      reply.set_text(('I say', u"key is %s" % key))

   def go_to_try_out(self, button):
      self.loop.widget = self.go_trial_widget
      self.loop.palette = self.go_trial_palette

   def on_next_clicked(self, button):
      self.loop.widget = self.go_product_widget
      self.loop.palette = self.go_product_palette


   def get_widget(self):
      return self.widgetList
