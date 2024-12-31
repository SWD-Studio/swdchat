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

import os,platform,subprocess

def open_file(file_path):
    '''open a file. use in multiplatform'''
    file_path = os.path.realpath(file_path)
    if platform.system() == "Windows":
        os.startfile(file_path)
    elif platform.system() == "Darwin":  # macOS
        os.system(f'open "{file_path}"')
    elif platform.system() == "Linux":
        os.system(f'xdg-open "{file_path}"')

def open_folder(folder_path):
    '''open a filefolder. use in multiplatform'''
    system_name = platform.system()
    if system_name == 'Windows':
        os.startfile(folder_path)
    elif system_name == 'Darwin':  # macOS
        subprocess.Popen(['open', folder_path])
    elif system_name == 'Linux':
        subprocess.Popen(['xdg-open', folder_path])
    else:
        raise OSError('Unsupported operating system: ' + system_name)
