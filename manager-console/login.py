# _*_ coding: utf-8 _*_

import urwid
import globalInput

class LogIn(object):

   def __init__(self, loop, p):
       self.loop = loop
       self.p = p
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
       self.button = urwid.GridFlow([urwid.AttrWrap(button, 'btn', 'btn') for button in self.button_list], 12, 5, 0, 'center')
       
       self.pile = urwid.Pile([self.ask_username, self.div, self.ask_password, self.div, self.ask_key, self.div, self.button])
       self.top = urwid.Filler(self.pile, valign='top')

   def set_widgetList_other(self, go_trial, go_product):
       self.go_trial_widget = go_trial
       self.go_product_widget = go_product
# ---------------------------------------------------------
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
# --------------------------------------------------------
   def on_ask_username_change(self, edit, new_edit_text):
      self.set_username(str(new_edit_text))
      self.reply.set_text(('I say', u"Nice to meet you, %s" % self.get_username()))

   def on_ask_password_change(self, edit, new_edit_text):
      self.set_password(str(new_edit_text))
      self.reply.set_text(('I say', u"pwd is %s" % self.get_password()))

   def on_ask_key_change(self, edit, new_edit_text):
      self.set_key(str(new_edit_text))
      self.reply.set_text(('I say', u"key is %s" % self.get_key()))

   def go_to_try_out(self, button):
      self.loop.widget = self.go_trial_widget

   def on_next_clicked(self, button):
      self.p.set_username(self.get_username())
      self.p.set_password(self.get_password())
      self.p.set_key(self.get_key())
      self.loop.widget = self.go_product_widget

   def get_widget(self):
      return self.top
