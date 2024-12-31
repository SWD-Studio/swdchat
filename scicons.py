# -*- encoding=utf-8 -*-
#    Copyright (C) 2020-2024  SWD Studio

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#     any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#    You can contact us on <http://swdstudio.github.com>.

import json
import scwidgets

class IconMap(dict):
    '''The main list of icon'''
    def __init__(self,iconpath='./icons/')->None:
        dict.__init__(self)
        self.iconpath=iconpath
        with open(iconpath+'index.json', encoding='utf-8') as jsonfile:
            self.iconlist=json.loads(jsonfile.read())

    def __missing__(self,key):
        '''when new icons were attend'''
        try:
            newfilename=self.iconlist[key]
        except (KeyError,TypeError):
            raise KeyError("Key %s not found"%str(key))
        newicon=scwidgets.pt16(self.iconpath+newfilename)
        self[key]=newicon
        return self[key]

if __name__ == '__main__' :
    aaa=IconMap()
    import tkinter
    aa=tkinter.Tk()
    b=tkinter.Label(master=aa,image=aaa['ADD'])
    b.pack()
    aa.mainloop()
else:
    iconmap=IconMap()
    