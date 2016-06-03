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
        self.tab_content.original_widget = self.tab_map[tab_name]

    def keypress(self, size, key):
        if self.tab_list_widget == self.column.focus:
            if key == 'up' and self.tab_index > 1:
                self.tab_index -= 1
                self.tab_content.original_widget = self.tab_map[self.tab_names[self.tab_index]]
            elif key == 'down' and self.tab_index < self.tab_index_max:
                self.tab_index += 1
                self.tab_content.original_widget = self.tab_map[self.tab_names[self.tab_index]]
        urwid.Filler.keypress(self, size, key)


class SimplePopupDialog(urwid.WidgetWrap):

    signals = ["close"]
    def __init__(self, text):
        close_button = urwid.Button("OK")
        urwid.connect_signal(close_button, "click",
            lambda button:self._emit("close"))
        pile = urwid.Pile([urwid.Text(text), close_button])
        fill = urwid.Filler(pile)
        self.__super.__init__(urwid.AttrWrap(fill, ""))
