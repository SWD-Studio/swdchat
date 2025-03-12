#    Copyright (C) 2020-2025  SWD Studio

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
#    You can contact us on swd-go.ysepan.com.

# 20250224
# UI:语音输入

from tkinter import *  # @UnusedWildImport
from tkinter import scrolledtext
from tkinter.ttk import *  # @UnusedWildImport
# import logging

from scicons import iconmap
import swdra


class VoiceRecToplevel(Toplevel):
    '''
    Toplevel when need to identify the voice
    Note:It can't be destroyed, use VoiceRecToplevel.withdraw instead
    '''

    def __init__(self, target: scrolledtext.ScrolledText, *args, **kwargs)->None:
        Toplevel.__init__(self, *args, **kwargs)
        self.target = target
        self._main_st = scrolledtext.ScrolledText(master=self)
        self._button_f = Frame(master=self)
        self._state_l = Label(master=self, text='单击按钮以输入...')
        self._insert_b = Button(master=self._button_f,
                                image=iconmap["CONFIRM"], command=self._insert)
        self._main_b = Button(master=self._button_f,
                              image=iconmap["MIC"], command=self._mainb)
        self._delete_b = Button(master=self._button_f,
                                image=iconmap["DELETE"], command=self._delete)
        swdra.asr_result(self._receive)
        self.state = 0
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.title('语音输入')

    def pack(self)->None:
        self._insert_b.pack(side=RIGHT)
        self._delete_b.pack(side=LEFT)
        self._main_b.pack()
        self._button_f.pack(side=BOTTOM, fill=X, expand=True)
        self._state_l.pack(side=BOTTOM, fill=X, expand=True)
        self._main_st.pack(side=TOP, fill=BOTH, expand=True)

    # @
    def recall(self, func):
        '''configure recall function'''
        self.racallfunc = func
        return func
    def get_current_msg(self):
        pass

    def _insert(self)->None:
        self.target=self.get_current_msg()
        if self.target :
            self.target.insert(index=INSERT, chars=self._main_st.get('1.0', END).strip())
            self._delete()

    def _mainb(self)->None:
        if self.state:
            self._state_l.config(text='正在处理...')
            self._main_b.config(state=DISABLED)
            swdra.finish_recording_process()
        else:
            swdra.start_recording_process()
            self._state_l.config(text='正在听...')
            self._main_b.config(image=iconmap['STOPMIC'])
        self.state = 1-self.state

    def _delete(self)->None:
        self._main_st.delete('1.0', END)

    def _receive(self, inputdic):
        if inputdic['asr_error_state_code']:
            self._state_l.config(text='发生异常:'+inputdic['asr_error_infomation'])
        else:
            self._main_st.insert(INSERT, inputdic['asr_result_message'])
            self._state_l.config(text='单击按钮以说话...')
        self._main_b.config(state=NORMAL, image=iconmap['MIC'])


def _demo():
    demotk = Tk()
    demost = scrolledtext.ScrolledText(master=demotk)
    demotl = VoiceRecToplevel(master=demotk, target=demost)
    demotl.title('SWDChat-VoiceRec')
    demotl.pack()
    demost.pack(fill=BOTH, expand=True)
    demotk.mainloop()


if __name__ == '__main__':
    _demo()
else:
    voicetoplevel=VoiceRecToplevel(target=None)
