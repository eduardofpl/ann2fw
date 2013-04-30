#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  getMODISdata.py
#  
#  Copyright 2013 Eduardo Fávero Pacheco da Luz <eduardofpl@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  ftp://e4ftl01.cr.usgs.gov/MOLT/MOD09GQ.005/2006.04.06/MOD09GQ.A2006096.h09v07.005.2008094155942.hdf

import ftplib

def main():
  ftp = ftplib.FTP('e4ftl01.cr.usgs.gov')

  ftp.login()

  directory = '/MOLT/MOD09GQ.005/2006.04.06/'

  ftp.cwd(directory)
  
  #~ ftp.retrlines('LIST')

  data = []

  ftp.dir(data.append)

  ftp.quit()

  for line in data:
    print line

  linha1 = data[1].split()

  print 'Tamanho da estrutura: ', len(data)
  print 'Tamanho de uma linha: ', len(linha1)
  print 'Ultima estrutura: ', linha1[len(linha1)-1]

  return 0

if __name__ == '__main__':
  main()

