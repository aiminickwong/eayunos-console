# _*_ coding:utf-8 _*_

import urwid
from common import ConfigTab, TabNetwork
from node_console import TabEngineSetup

palette = []
loop = urwid.MainLoop(None, palette, pop_ups=True)
config_tab_list = [
    TabNetwork(loop),
    TabEngineSetup(),
]
loop.widget = ConfigTab(config_tab_list)

if __name__ == '__main__':
   loop.run()
