# _*_ coding: utf-8 _*_

import urwid
import globalInput
import ProductInfo

palette = [('I say', 'yellow', 'light gray', 'bold'),
           ('btn', 'yellow', 'light gray', 'bold'),
          ]
ask_username = urwid.Edit(('I say', u"用户名： "))
ask_password = urwid.Edit(('I say', u"\n密码： "))
ask_key = urwid.Edit(('I say', u"\nkey: "))
username = ''
password = ''
key = ''

reply = urwid.Text(u"")

button_tryout = urwid.Button(u'  试用')
button_next = urwid.Button(u' 下一步')
button_list = [button_tryout, button_next]

#button = urwid.GridFlow([urwid.AttrWrap(button_tryout, button_next], 12, 5, 0, 'left')

button = urwid.GridFlow([urwid.AttrWrap(button, 'btn', 'btn') for button in button_list], 12, 5, 0, 'left')

div = urwid.Divider()

pile = urwid.Pile([ask_username, div, ask_password, div, ask_key, div, reply, button])

top = urwid.Filler(pile, valign='top')

def set_username(username):
   username = username

def get_username():
   return username

def set_password(password):
   password = password

def get_password():
   return password

def set_key(key):
   key = key

def get_key():
   return key

def on_ask_username_change(edit, new_edit_text):
   set_username(str(new_edit_text))
   reply.set_text(('I say', u"Nice to meet you, %s" % new_edit_text))

def on_ask_password_change(edit, new_edit_text):
   set_password(str(new_edit_text))
   reply.set_text(('I say', u"pwd is %s" % password))

def on_ask_key_change(edit, new_edit_text):
   set_key(str(new_edit_text))
   reply.set_text(('I say', u"key is %s" % key))

def go_to_try_out(button):
   globalInput.loop.run()
   
def on_next_clicked(button):
#  raise urwid.ExitMainLoop()
   ProductInfo.run_productInfo()

urwid.connect_signal(ask_username, 'change', on_ask_username_change)
urwid.connect_signal(ask_password, 'change', on_ask_password_change)
urwid.connect_signal(ask_key, 'change', on_ask_key_change)
urwid.connect_signal(button_tryout, 'click', go_to_try_out)
urwid.connect_signal(button_next, 'click', on_next_clicked)

loop = urwid.MainLoop(top, palette)
# loop.run()
