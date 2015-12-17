# _*_ coding:utf-8 _*_

from login import *
from productInfo import *
from checkbox import *
import globalInput

palette = [
       ('I say', 'yellow', 'light gray', 'bold'),
       ('btn', 'yellow', 'light gray', 'bold'),
       ('banner', 'yellow', 'light gray'),
       ('streak', 'yellow', 'light gray'),
       ('buttnf','white','dark blue','bold'),
       ]

loop = urwid.MainLoop(None, palette)

l = LogIn(loop)
p = Product(loop)
c = CheckBox(loop)

go_trial = None
go_login = l.get_widget()
go_product = p.get_widget()
go_checkbox = c.get_widget()

l.set_widgetList_other(go_trial, go_product)
p.set_widgetList_other(go_login, go_checkbox)
c.set_widgetList_other(go_product, go_login)

loop.widget = go_login

# 获取 login 中的登录信息
username = l.get_username()
password = l.get_password()
key = l.get_key()

# 将登录信息传给 product 类中
p.set_username(username)
p.set_password(password)
p.set_key(key)

if __name__ == '__main__':
   #urwid.MainLoop(loop.widget, loop.palette).run()
   print username
   print password
   print type(username)
   print type(password)
   print '-------------------'
   loop.run() 
