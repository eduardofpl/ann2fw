#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  buildANNanswer.py
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

import os
import gdal
import numpy
import shutil
from gdalconst import *

def createDir(directory):
    """
    Creates a directory if it doesn't exists

    :arg string directory: Directory to be created.

    :returns: statusCreation
    :rtype: int
    """
    if not os.path.exists(directory):
        statusCreation = os.makedirs(directory)
    else:
        statusCreation = 2
    return statusCreation

def removeDir(directory):
    """
    Removes a directory and all its contents

    :arg string directory: Directory to be created.

    :returns: statusDeletion
    :rtype: int
    """
    if os.path.exists(directory):
        statusDeletion = shutil.rmtree(directory)
    else:
        statusDeletion = 2
    return statusDeletion

def main():

    #Read tasks ID
    tasksID = open('aplicTasks.dat','r')
    if tasksID is None:
        print 'Could not open tasks ID!\n'
        sys.exit(1)
    tasksList = []
    for line in tasksID.readlines():
        temp = [int(value) for value in line.split()]
        tasksList.append(temp)
    tasksID.close()
    tasks = numpy.asarray(tasksList)

#######################################################

    #Read results from ANN
    resultANN = open('saidaAplic.dat','r')
    if resultANN is None:
        print 'Could not open results from ANN!\n'
        sys.exit(1)
    resultsList = []
    for line in resultANN.readlines():
        temp = [float(value) for value in line.split()]
        resultsList.append(temp)
    resultANN.close()
    results = numpy.asarray(resultsList)

#######################################################

    #Check if everything is okay
    lenTasks = len(tasks)
    lenResults = len(results)
    if (lenTasks != lenResults):
        print 'PROBLEM: Lengths do not match!\n'
        sys.exit(1)

    #Set dir directory to hold the answer
    annBuildDir = 'results/annBuild'
    annTempDir = 'results/annTemp'
    annHeatTemp = 'results/heatTemp'
    stat = createDir(annBuildDir)
    stat = createDir(annTempDir)
    stat = createDir(annHeatTemp)

    #Determine the selected one
    sureLevel = 0.5
    good = 0
    bad = 0
    for i in range(lenTasks):
        taskID = tasks[i]
        selected = numpy.argmax(results[i])
        prob = results[i][selected]
        if (prob < sureLevel):
            bad = bad + 1
        else:
            good = good + 1
        selectedFile = 'results/tmpImg_n'+str(selected+1).zfill(2)+'/'+str(taskID).replace('[','').replace(']','')+'.tif'
        shutil.copy(selectedFile,annTempDir)
        #Building heat map
        origCut = selectedFile
        heatCut = annHeatTemp+'/'+str(taskID).replace('[','').replace(']','')+'.tif'
        if os.path.isfile(origCut):
            shutil.copy(origCut, heatCut)
            pointFile = gdal.Open(heatCut, 2)
            #Calculating level of agreement
            agree = prob
            #Getting bands
            data1 = pointFile.GetRasterBand(1).ReadAsArray()
            data2 = pointFile.GetRasterBand(2).ReadAsArray()
            data3 = pointFile.GetRasterBand(3).ReadAsArray()
            #Seting colours based on agreement
            if agree <= 0.0:
                newData1 = (data1 * 0) + int(255)
                newData2 = (data1 * 0) + int(0)
                newData3 = (data1 * 0) + int(0)
            elif agree > 0.0 and agree < 0.1:
                newData1 = (data1 * 0) + int(229)
                newData2 = (data1 * 0) + int(0)
                newData3 = (data1 * 0) + int(0)
            elif agree >= 0.1 and agree < 0.2:
                newData1 = (data1 * 0) + int(204)
                newData2 = (data1 * 0) + int(0)
                newData3 = (data1 * 0) + int(0)
            elif agree >= 0.2 and agree < 0.3:
                newData1 = (data1 * 0) + int(178)
                newData2 = (data1 * 0) + int(0)
                newData3 = (data1 * 0) + int(0)
            elif agree >= 0.3 and agree < 0.4:
                newData1 = (data1 * 0) + int(153)
                newData2 = (data1 * 0) + int(0)
                newData3 = (data1 * 0) + int(0)
            elif agree >= 0.4 and agree < 0.5:
                newData1 = (data1 * 0) + int(127)
                newData2 = (data1 * 0) + int(0)
                newData3 = (data1 * 0) + int(0)
            elif agree >= 0.5 and agree < 0.6:
                newData1 = (data1 * 0) + int(0)
                newData2 = (data1 * 0) + int(0)
                newData3 = (data1 * 0) + int(127)
            elif agree >= 0.6 and agree < 0.7:
                newData1 = (data1 * 0) + int(0)
                newData2 = (data1 * 0) + int(0)
                newData3 = (data1 * 0) + int(153)
            elif agree >= 0.7 and agree < 0.8:
                newData1 = (data1 * 0) + int(0)
                newData2 = (data1 * 0) + int(0)
                newData3 = (data1 * 0) + int(178)
            elif agree >= 0.8 and agree < 0.9:
                newData1 = (data1 * 0) + int(0)
                newData2 = (data1 * 0) + int(0)
                newData3 = (data1 * 0) + int(204)
            elif agree >= 0.9 and agree < 1.0:
                newData1 = (data1 * 0) + int(0)
                newData2 = (data1 * 0) + int(0)
                newData3 = (data1 * 0) + int(229)
            elif agree >= 1.0:
                newData1 = (data1 * 0) + int(0)
                newData2 = (data1 * 0) + int(0)
                newData3 = (data1 * 0) + int(225)
            #Writing each band of new values
            pointFile.GetRasterBand(1).WriteArray(newData1)
            pointFile.GetRasterBand(2).WriteArray(newData2)
            pointFile.GetRasterBand(3).WriteArray(newData3)
            #Close and save file
            pointFile = None

    #Merge final resulting image
    #For image
    cmd = "gdal_merge.py -o "+annBuildDir+"/annBuild.tif "+annTempDir+"/*.tif"
    os.system(cmd)
    #For heat map
    cmd = "gdal_merge.py -o "+annBuildDir+"/annHeat.tif "+annHeatTemp+"/*.tif"
    os.system(cmd)

    #Some final considerations
    print 'Good levels: ', good
    print 'Bad levels: ', bad

    #Remove temp dir
    #~ stat = removeDir(annTempDir)
    #~ stat = removeDir(annHeatTemp)

    # End of only funcion :-)
    return 0

if __name__ == '__main__':
    main()

