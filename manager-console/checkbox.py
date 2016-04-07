# _*_ coding:utf-8 _*_
import urwid
import globalInput

class CheckBox(object):

    def __init__(self, loop):
        self.loop = loop
        urwid.connect_signal(self.button_back, 'click', self.go_back)
        urwid.connect_signal(self.button_next, 'click', self.go_next)

    def set_widgetList_other(self, go_product, go_login):
        self.go_product_widget = go_product
        self.go_login_widget = go_login

    #palette = [
    #('btn','yellow','light gray'),
    #('buttnf','white','dark blue','bold'),
    #]

    button_back = urwid.Button(u'  返回')
    button_next = urwid.Button(u' 下一步')
    button_list = [button_back, button_next]
    button = urwid.GridFlow([urwid.AttrWrap(button, 'btn', 'btn') for button in button_list], 12, 5, 0, 'left')

    text_cb_list = [u"Wax", u"导入 ISO 域", u"智能调度", u"虚拟机备份", u"显卡穿透", u"报表"]

    div = urwid.Divider()

    checkbox = urwid.Pile([urwid.AttrWrap(urwid.CheckBox(txt), 'btn', 'buttnf') for txt in text_cb_list])

    listbox_content = [urwid.Padding(checkbox, left = 0, right = 2, min_width = 7), div, urwid.Padding(button, left = 0, right = 2, min_width = 7)]

    listbox = urwid.ListBox(urwid.SimpleListWalker(listbox_content))
    frame = urwid.Frame(urwid.AttrWrap(listbox, 'body'))

    def go_back(self, button):
       self.loop.widget = self.go_product_widget

    def go_next(self, button):
       self.loop.widget = self.go_login_widget


    def get_widget(self):
       return self.frame
