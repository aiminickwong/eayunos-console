from login import *
from productInfo import *
from checkbox import *
import globalInput

go_trial = globalInput.fill

loop = urwid.MainLoop(None, None)

l = LogIn(loop)
p = Product(loop)
c = CheckBox(loop)

#go_trial = t.get_widget()
go_trial = [None, None]
go_login = l.get_widget()
go_product = p.get_widget()
go_checkbox = c.get_widget()

l.set_widgetList(go_trial, go_product)
p.set_widgetList(go_login, go_checkbox)
c.set_widgetList(go_product, go_login)

loop.widget = go_login[0]
loop.palette = go_login[1]

if __name__ == '__main__':
   loop.run()
