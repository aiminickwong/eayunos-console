import urwid

def show_or_exit(key):
   if key in ('q', 'Q'):
      raise urwid.ExitMainLoop()
   text.set_text(repr(key))

text = urwid.Text(u"Hello World")
fill = urwid.Filler(text, 'top')
loop = urwid.MainLoop(fill, unhandled_input=show_or_exit)
     
