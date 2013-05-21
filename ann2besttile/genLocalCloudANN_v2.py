#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Instituto Nacional de Pesquisas Espaciais (INPE)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import sys
import gdal
import json
import time
import random
import shutil
import urllib2
import datetime
from gdalconst import *
from optparse import OptionParser

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

def genInput(origLocation, destLocation, typeGray, samplSize):
    """
    Generate input file for ANN

    :arg list dict tasksInfo: Dictionary list with the tasks info.
    :arg list dict results: Dictionary list with the processed results.
    :arg string origLocation: Directory with orginal images.
    :arg string origLocation: Directory for the results.
    :arg string typeGray: Type of gray scale transformation
    :arg integer samplSize: Size of the sampling [0.0, 1.0]

    :returns: Nothing
    :rtype: None
    """
    
    # Training / aplication
    treina = False
    verdade = False

    # Sampling pixels from image
    sampl = True
    if sampl == True:
        buildSampl = True
    else:
        buildSampl = False

    # Write data to file
    if treina:
        outInput = open('testRond/trainInput.dat', 'w')
        outOutput = open('testRond/trainOutput.dat', 'w')
        selecOut = open('testRond/selected.dat', 'w')
    else:
        outInput = open('testRond/aplicInput.dat', 'w')
        outTasks = open('testRond/aplicTasks.dat', 'w')
        if verdade:
            outOutput = open('testRond/verdadeOutput.dat', 'w')

    #~ #Setting info on temporary directory for images
    #~ numberImages = 12
    #~ tmpImg = []
    #~ for i in range(numberImages):
        #~ tmpImg.append(destLocation+"tmpImg_n"+str(i+1).zfill(2)+"/")

    imgFile = []
    imgFile.append('2011352')
    imgFile.append('2011353')
    imgFile.append('2011355')
    imgFile.append('2011357')
    imgFile.append('2011358')
    imgFile.append('2011359')
    imgFile.append('2011360')
    imgFile.append('2011361')
    imgFile.append('2011362')
    imgFile.append('2011363')
    imgFile.append('2011364')
    imgFile.append('2011365')

    #Setting info on temporary directory for images
    numberImages = 12
    tmpImg = []
    for i in range(numberImages):
        tmpImg.append(destLocation+imgFile[i]+"/")

    #Hardcode taskID
    tasksInfo = []
    tasksInfo.append('00_00')
    tasksInfo.append('00_01')
    tasksInfo.append('01_00')
    tasksInfo.append('01_01')

    #If we need to skip line
    finishLine = True
    #Getting number of tasks
    numberTasks = 2*2
    print 'number of tasks: ', numberTasks
    for task in range(numberTasks):
        #Geting the selected day for each task
        taskId = tasksInfo[task]
        for img in range(numberImages):
            imgName = tmpImg[img] + str(taskId) + '.tif'
            #Openning image (and testing)
            if os.path.exists(imgName) is False:
                print 'INPUT -> Task miss: ' + str(taskId) + ' Image: ' + str(img) + ' Name: ' + imgName
                finishLine = False
                continue
            print 'INPUT -> Task: ' + str(taskId) + ' Image: ' + str(img)
            fileSat = gdal.Open(imgName, GA_ReadOnly)
            if fileSat is None:
                print 'Could not open ' + imgName
                sys.exit(1)
            # Read band values from image
            rows = fileSat.RasterYSize
            cols = fileSat.RasterXSize
            R_band_sat = fileSat.GetRasterBand(1)
            G_band_sat = fileSat.GetRasterBand(2)
            B_band_sat = fileSat.GetRasterBand(3)
            R_data_sat = R_band_sat.ReadAsArray(0, 0, cols, rows)
            G_data_sat = G_band_sat.ReadAsArray(0, 0, cols, rows)
            B_data_sat = B_band_sat.ReadAsArray(0, 0, cols, rows)
            #Closing image
            fileSat = None

            #If we are sampling the image, then we'll pick our samples
            print 'sampl: ', sampl
            print 'buildSampl: ', buildSampl
            if ((sampl == True) and (buildSampl == True)):
                universe = []
                samplList = []
                random.seed(8225)
                for i in range(rows):
                    for j in range(cols):
                        universe.append([i,j])
                sizeUniverse = len(universe)
                samplSizeInt = int(samplSize * sizeUniverse)
                print 'Sampling mode activated.'
                print 'Using ', samplSizeInt, ' out of ', sizeUniverse, ' pixels.'
                for i in range(samplSizeInt):
                    samplList.append(universe.pop(random.randint(0,len(universe)-1)))
                buildSampl = False

            sumValueGray = 0.0
            if (sampl == False):
                #Working with the values
                for i in range(rows):
                    for j in range(cols):
                        #~ valueString = str(float(R_data_sat[i,j])/255.0)+' '+str(float(G_data_sat[i,j])/255.0)+' '+str(float(B_data_sat[i,j])/255.0)
                        valueGray = rgb2gray((float(R_data_sat[i,j])/255.0),(float(G_data_sat[i,j])/255.0),(float(B_data_sat[i,j])/255.0),typeGray)
                        sumValueGray = sumValueGray + valueGray
                        valueString = str(taskId)+' '+str(valueGray)
                        #~ outInput.write("%s "%valueString)
                sumValueString = str(taskId)+' '+str(sumValueGray/(rows*cols))
                #~ outInput1par.write("%s "%sumValueString)
                outInput.write("%s "%sumValueString)
            else:
                #Working with the sampled values
                for idx in range(samplSizeInt):
                    i = samplList[idx][0]
                    j = samplList[idx][1]
                    valueGray = rgb2gray((float(R_data_sat[i,j])/255.0),(float(G_data_sat[i,j])/255.0),(float(B_data_sat[i,j])/255.0),typeGray)
                    sumValueGray = sumValueGray + valueGray
                    valueString = str(valueGray)
                    #~ outInput.write("%s "%valueString)
                sumValueString = str(sumValueGray/samplSizeInt)
                #~ outInput1par.write("%s "%sumValueString)
                outInput.write("%s "%sumValueString)

        #If we did not had a problem with missing task
        if finishLine == True:
            #Closing the line of the file
            outInput.write("\n")
            #~ outInput1par.write("\n")
            outTasks.write(str(taskId)+"\n")
        else:
            finishLine = True

        #If we are training (or we know the truth), then we also generate the truth
        if treina or verdade:
            selecName = 'X/home/eduardo/ForestWatchers/ann2besttile/results/tmpMosaic_n0/' + str(taskId) + '.tif'
            #Openning image (and testing)
            if os.path.exists(selecName) is False:
                print 'OUTPUT -> Task miss: ' + str(taskId)
                continue
            #~ fileSelec = gdal.Open(selecName, GA_ReadOnly)
            #~ if fileSelec is None:
                #~ print 'Could not open ' + selecName
                #~ sys.exit(1)
            #~ # Read band values from image
            #~ rows = fileSelec.RasterYSize
            #~ cols = fileSelec.RasterXSize
            #~ R_band_selec = fileSelec.GetRasterBand(1)
            #~ G_band_selec = fileSelec.GetRasterBand(2)
            #~ B_band_selec = fileSelec.GetRasterBand(3)
            #~ R_data_selec = R_band_selec.ReadAsArray(0, 0, cols, rows)
            #~ G_data_selec = G_band_selec.ReadAsArray(0, 0, cols, rows)
            #~ B_data_selec = B_band_selec.ReadAsArray(0, 0, cols, rows)
            #~ #Closing image
            #~ fileSelec = None
#~ 
            #~ if (sampl == False):
                #~ #Working with the values
                #~ for i in range(rows):
                    #~ for j in range(cols):
                        #~ valueGray = rgb2gray((float(R_data_selec[i,j])/255.0),(float(G_data_selec[i,j])/255.0),(float(B_data_selec[i,j])/255.0),'gleam')
                        #~ valueString = str(valueGray)
                        #~ outOutput.write("%s "%valueString)
            #~ else:
                #~ #Working with the values
                #~ for idx in range(samplSizeInt):
                    #~ i = samplList[idx][0]
                    #~ j = samplList[idx][1]
                    #~ valueGray = rgb2gray((float(R_data_selec[i,j])/255.0),(float(G_data_selec[i,j])/255.0),(float(B_data_selec[i,j])/255.0),'gleam')
                    #~ valueString = str(valueGray)
                    #~ outOutput.write("%s "%valueString)
#~ 
            #~ #Closing line of the file
            #~ outOutput.write("\n")

            selectedTile = results[task].index(max(results[task]))
            if selectedTile == 0:
                selectedName = str(taskId) + ' 2011352'
                selectedFile = '1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0'
            elif selectedTile == 1:
                selectedName = str(taskId) + ' 2011353'
                selectedFile = '0.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0'
            elif selectedTile == 2:
                selectedName = str(taskId) + ' 2011355'
                selectedFile = '0.0 0.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0'
            elif selectedTile == 3:
                selectedName = str(taskId) + ' 2011357'
                selectedFile = '0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0'
            elif selectedTile == 4:
                selectedName = str(taskId) + ' 2011358'
                selectedFile = '0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0'
            elif selectedTile == 5:
                selectedName = str(taskId) + ' 2011359'
                selectedFile = '0.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0'
            elif selectedTile == 6:
                selectedName = str(taskId) + ' 2011360'
                selectedFile = '0.0 0.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 0.0'
            elif selectedTile == 7:
                selectedName = str(taskId) + ' 2011361'
                selectedFile = '0.0 0.0 0.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0'
            elif selectedTile == 8:
                selectedName = str(taskId) + ' 2011362'
                selectedFile = '0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0'
            elif selectedTile == 9:
                selectedName = str(taskId) + ' 2011363'
                selectedFile = '0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0'
            elif selectedTile == 10:
                selectedName = str(taskId) + ' 2011364'
                selectedFile = '0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 1.0 0.0'
            elif selectedTile == 11:
                selectedName = str(taskId) + ' 2011365'
                selectedFile = '0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 1.0'
            #~ outOutputClass.write("%s\n"%selectedFile)
            outOutput.write("%s\n"%selectedFile)
            selecOut.write("%s\n"%selectedName)

    # Close files
    outInput.close()
    outTasks.close()
    #~ outInput1par.close()
    if treina or verdade:
        outOutput.close()
        #~ outOutputClass.close()
        selecOut.close()

    statusGenInput = 0
    print '\nend of genInput\n'
    return statusGenInput

def rgb2gray(R,G,B,T):
    """
    Converts RGB values to gray scale depending on type of convertion
    Based on doi:10.1371/journal.pone.0029740

    :arg real R: value for red pixel
    :arg real G: value for green pixel
    :arg real B: value for blue pixel
    :arg string T: type of gray scale transform

    :returns: grayValue
    :rtype: real
    """
    gammaCorrection = (1.0/2.2)
    if T == 'intensity':
        grayValue = (R+G+B)/3.0
    elif T == 'gleam':
        grayValue = (R**(gammaCorrection)+G**(gammaCorrection)+B**(gammaCorrection))/3.0
    elif T == 'luminance':
        grayValue = 0.3*R + 0.59*G + 0.11*B
    elif T == 'luma':
        grayValue = 0.2126*R**(gammaCorrection) + 0.7152*G**(gammaCorrection) + 0.0722*B**(gammaCorrection)
    elif T == 'lightness':
        Y = 0.2126*R + 0.7152*G + 0.0722*B
        if Y > ((6.0/29)**3):
            fY = Y**(1.0/3.0)
        else:
            fY = (1.0/3.0)*((29.0/6.0)**2)*Y + (4.0/29.0)
        grayValue = (116.0*fY-16.0)/100.0
    elif T == 'value':
        grayValue = max(R,G,B)
    elif T == 'luster':
        grayValue = (max(R,G,B)+min(R,G,B))/2.0
    else:
        print 'ERROR: Type of gray scale convertion not recognized!'
        sys.exit(1)
    return grayValue

#######################
# Begin of the script #
#######################

if __name__ == "__main__":

    # Arguments for the application
    usage = "usage: %prog arg1 arg2 ..."
    parser = OptionParser(usage)

    parser.add_option("-i", "--images-directory", dest="imagesDir", \
        help="Directory containing the images", metavar="IMAGESDIR")
    parser.add_option("-d", "--destination-directory", dest="destDir", \
        help="Directory for results", metavar="DESTDIR")

    (options, args) = parser.parse_args()

    if options.imagesDir:
        imagesDir = options.imagesDir
    else:
        imagesDir = "/home/eduardo/Testes/fw_img/FAS_Brazil7/"
    if options.destDir:
        destDir = options.destDir
    else:
        destDir = "/home/eduardo/ForestWatchers/ann2besttile/resultsLocal/"

    #Genereting input for ANN
    typeGray = 'luminance'
    sampleSize = 0.10
    print "Generating input for ANN..."
    start = time.time()
    input = genInput(imagesDir, destDir, typeGray, sampleSize)
    end = time.time()
    globalEnd = end
    elapsed = end - start
    print "Time taken: ", elapsed, "seconds"
    print " "
