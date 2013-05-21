#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  shuffleTrainANN.py
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
#  

import shutil
import random

def main():
    #Original files
    origInput = 'trainInput.dat'
    origOutput = 'trainOutput.dat'

    #~ #Backup
    #~ shutil.copyfile(origInput, origInput+'.orig')
    #~ shutil.copyfile(origOutput, origOutput+'.orig')

    #Open files
    dataInput = open(origInput,'r')
    if dataInput is None:
        print 'Could not open input data!\n'
        sys.exit(1)
    dataOutput = open(origOutput,'r')
    if dataOutput is None:
        print 'Could not open input data!\n'
        sys.exit(1)

    #New files
    shufInput = 'shuf_'+origInput
    shufOutput = 'shuf_'+origOutput
    newInput = open(shufInput,'w')
    newOutput = open(shufOutput,'w')

    #Read and shuffle data
    dataSize = 12
    for lineIn in dataInput.readlines():
        #Read all data
        lineOut = dataOutput.readline()
        valuesIn = [value for value in lineIn.split()]
        valuesOut = [value for value in lineOut.split()]
        #Prepare to shuffle
        pos = range(dataSize)
        newPos = pos
        newIn = [0.0] * dataSize
        newOut = [0.0] * dataSize
        #Shuffle X times
        timeShuffle = 10
        for t in range(timeShuffle):
            random.shuffle(newPos)
            for i in pos:
                newIn[i] = valuesIn[newPos[i]]
                newOut[i] = valuesOut[newPos[i]]
            #Write data
            newInput.write(' '.join(newIn))
            newInput.write('\n')
            newOutput.write(' '.join(newOut))
            newOutput.write('\n')
        

    #Close files
    dataInput = None
    dataOutput = None
    newInput = None
    newOutput = None

    return 0

if __name__ == '__main__':
    main()

