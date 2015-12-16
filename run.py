from login import *
from productInfo import *
from checkbox import *
import globalInput

go_trial = globalInput.fill

loop = urwid.MainLoop(None, palette)

l = LogIn(loop, go_trial, tiral_palette, go_product, product_palette)
p = Product(loop, go_login, go_checkout)
c = CheckBox(loop, go_product, go_login)

go_login = l.get_top()
go_product = p.get_top()
go_checkout = c.get_frame()

loop.widget = go_login

if __main__ == __name__:
   loop.run()
