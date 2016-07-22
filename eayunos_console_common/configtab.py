#coding=utf-8

import urwid


class ConfigTab(urwid.Filler):

    def __init__(self, tabs):
        self.tab_index = 0
        self.tab_index_max = len(tabs)
        self.tab_names = [None] * (self.tab_index_max+1)
        self.tab_map = {}
        self.tab_list_widget = self.menu(tabs)
        self.column = urwid.Columns([
            ("weight", 1, self.tab_list_widget),
            ("weight", 6, self.tab_content),
        ])
        urwid.Filler.__init__(self, self.column, valign='top')

    def menu(self, tabs):
        body = []
        for tab in tabs:
            self.tab_index += 1
            self.tab_names[self.tab_index] = tab.name
            # 这里的self.tab_names可以在__init__时直接初始化成[None]，然后这句直接用self.tab_names.append(tab.name)
            self.tab_map[tab.name] = tab.widget
            button = urwid.Button(tab.name)
            urwid.connect_signal(button, 'click', self.tab_mouse_chosen)
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))
        self.tab_content = urwid.Padding(tabs[0].widget, left=3)
        self.tab_index = 1
        return urwid.BoxAdapter(urwid.ListBox(urwid.SimpleFocusListWalker(body)), self.tab_index_max)

    def tab_mouse_chosen(self, button):
        tab_name = button.get_label()
        self.tab_index = self.tab_names.index(tab_name)
        # 上面这句是否多余？
        self.tab_content.original_widget = self.tab_map[tab_name]

    def keypress(self, size, key):
        # 这个方法没有被调用过，是还没做完吗？
        if self.tab_list_widget == self.column.focus:
            if key == 'up' and self.tab_index > 1:
                self.tab_index -= 1
                self.tab_content.original_widget = self.tab_map[self.tab_names[self.tab_index]]
            elif key == 'down' and self.tab_index < self.tab_index_max:
                self.tab_index += 1
                self.tab_content.original_widget = self.tab_map[self.tab_names[self.tab_index]]
        urwid.Filler.keypress(self, size, key)


class Tab(object):
    def genRadioButton(self, caption_text, options, radiobutton_group):
        return urwid.Columns([
            ('pack', urwid.Text(caption_text)),
            urwid.GridFlow([
                urwid.RadioButton(radiobutton_group, option[0], on_state_change=option[1])
                for option in options], 30, 2, 0, 'left'),
        ])

    def get_radio_option(self, radiobutton_group):
        for button in radiobutton_group:
            if button.get_state():
                return button.get_label()

    def set_radio_option(self, radiobutton_group, option):
        for button in radiobutton_group:
            if button.get_label() == option:
                button.set_state(True)
                return


class SimplePopupDialog(urwid.WidgetWrap):

    signals = ["close"]
    def __init__(self, text):
        close_button = urwid.Button("OK")
        urwid.connect_signal(close_button, "click",
            lambda button: self._emit("close"))
        pile = urwid.Pile([urwid.Text(text), close_button])
        fill = urwid.Filler(pile)
        self.__super.__init__(urwid.AttrWrap(fill, ""))


class SimplePopupLauncher(urwid.PopUpLauncher):

    def __init__(self, w, text):
        self.text = text
        self.__super.__init__(w)
        # 这个w参数有用吗？

    def create_pop_up(self):
        pop_up = SimplePopupDialog(self.text)
        urwid.connect_signal(pop_up, 'close',
            lambda button: self.close_pop_up())
        return pop_up

    def get_pop_up_parameters(self):
        return {'left': 0, 'top': 1, 'overlay_width': 32, 'overlay_height': 7}
