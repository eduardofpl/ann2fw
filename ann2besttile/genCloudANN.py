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

def getAppId(server, appName):
    """
    Get the application id given the short name

    :arg string server: Address of the server
    :arg string appName: Short name of the application
    :returns: Numerical id of the application
    :rtype: integer
    """
    JSONdata = urllib2.urlopen(url=server+"/api/app?short_name="+ \
        appName).read()
    data = json.loads(JSONdata)
    appId = data[0]['id']
    return appId

def getTasks(server, appId, maxNumberTasks, completedOnly):
    """
    Get the tasks of a particular application from the server.

    :arg string server: Address of the server
    :arg string appId: ID of the application to be analysed
    :arg integer maxNumberTasks: Maximum number of tasks to be downloaded
    :arg int completedOnly: If we'll get only completed tasks
    :returns: Tasks info for the application
    :rtype: dictionary
    """
    if completedOnly == 1:
        JSONdata = urllib2.urlopen(url=server+"/api/task?app_id="+ \
            str(appId)+"&state=completed&limit="+ \
            str(maxNumberTasks)).read()
    else:
        JSONdata = urllib2.urlopen(url=server+"/api/task?app_id="+ \
            str(appId)+"&limit="+str(maxNumberTasks)).read()
    data = json.loads(JSONdata)
    numberTasks = len(data)
    tasksInfo = []
    for item in range(numberTasks):
        tasksInfo.append({'taskId':data[item]['id'], \
            'area':data[item]['info']['tile']['restrictedExtent']})
    return tasksInfo

def getResults(server, tasksInfo, maxNumberAnswers):
    """
    Get the results of a particular application from the server.

    :arg string server: Address of the server
    :arg integer maxNumberAnswers: Maximum number of answers per task to be downloaded
    :arg list tasksInfo: List of tasks
    :returns: Results for the application
    :rtype: dictionary
    """
    answersApp = []
    numberTasks = len(tasksInfo)
    for item in range(numberTasks):
        answersApp.append([])
        JSONdata = urllib2.urlopen(url=server+"/api/taskrun?task_id="+ \
            str(tasksInfo[item]['taskId'])+"&limit="+ \
            str(maxNumberAnswers)).read()
        data = json.loads(JSONdata)
        lenData = len(data)
        for ans in range(lenData):
            answersApp[item].append({'taskId':data[ans]['task_id'], \
            'id':data[ans]['id'], 'answer':data[ans]['info']['besttile']})
    return answersApp

def genStats(data, printStats = 0):
    """
    Calculate statistics about the results

    :arg list dict data: Dictionary list with all the results.

    :returns: Matrix with answers count for each task
    :rtype: list
    """
    fVotes = open('/home/eduardo/tmpImplement/results/votes.txt','w')
    tileCount = []
    numberTasks = len(data)
    for task in range(numberTasks):
        tileCount.append([0] * 12)
        numberResults = len(data[task])
        fVotes.write(str(task)+" ")
        for result in range(numberResults):
            fVotes.write(data[task][result]['answer']+" ")
            if data[task][result]['answer'] == '2011352':
                tileCount[task][0] += 1
            elif data[task][result]['answer'] == '2011353':
                tileCount[task][1] += 1
            elif data[task][result]['answer'] == '2011355':
                tileCount[task][2] += 1
            elif data[task][result]['answer'] == '2011357':
                tileCount[task][3] += 1
            elif data[task][result]['answer'] == '2011358':
                tileCount[task][4] += 1
            elif data[task][result]['answer'] == '2011359':
                tileCount[task][5] += 1
            elif data[task][result]['answer'] == '2011360':
                tileCount[task][6] += 1
            elif data[task][result]['answer'] == '2011361':
                tileCount[task][7] += 1
            elif data[task][result]['answer'] == '2011362':
                tileCount[task][8] += 1
            elif data[task][result]['answer'] == '2011363':
                tileCount[task][9] += 1
            elif data[task][result]['answer'] == '2011364':
                tileCount[task][10] += 1
            elif data[task][result]['answer'] == '2011365':
                tileCount[task][11] += 1
        fVotes.write("\n")
        #Print info for debug
        if printStats == 1:
            print "Stats for task " + str(task)
            print "Tile 00 (352) = " + str(tileCount[task][0])
            print "Tile 01 (353) = " + str(tileCount[task][1])
            print "Tile 02 (355) = " + str(tileCount[task][2])
            print "Tile 03 (357) = " + str(tileCount[task][3])
            print "Tile 04 (358) = " + str(tileCount[task][4])
            print "Tile 05 (359) = " + str(tileCount[task][5])
            print "Tile 06 (360) = " + str(tileCount[task][6])
            print "Tile 07 (361) = " + str(tileCount[task][7])
            print "Tile 08 (362) = " + str(tileCount[task][8])
            print "Tile 09 (363) = " + str(tileCount[task][9])
            print "Tile 10 (364) = " + str(tileCount[task][10])
            print "Tile 11 (365) = " + str(tileCount[task][11])
            print "Maximum value = " + str(max(tileCount[task]))
            print "Position = " + str(tileCount[task].index(max(tileCount[task])))
            print ""
    fVotes.close()
    return tileCount

def cutTiles(tasksInfo, results, origLocation, destLocation, \
    completedOnly, nAnswers = 0):
    """
    Cut the best tiles based on the results obtained by genStats

    :arg list dict tasks: Dictionary list with the tasks info.
    :arg list dict results: Dictionary list with the processed results.
    :arg string origLocation: Directory with orginal images.
    :arg string origLocation: Directory for the results.
    :arg int completedOnly: If we are processing only completed tasks
    :arg int nAnswers: Mininum number of answers to be considered

    :returns: Nothing
    :rtype: None
    """
    tmpMosaic = destLocation+"/tmpMosaic_n"+str(nAnswers)+"/"
    createDir(tmpMosaic)

    #Setting info on images
    numberImages = 12
    tmpImg = []
    for i in range(numberImages):
        tmpImg.append(destLocation+"/tmpImg_n"+str(i+1).zfill(2)+"/")
        createDir(tmpImg[i])
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

    #Setting info on image type
    formatFile = "GTiff"
    driver = gdal.GetDriverByName(formatFile)

    #Open file containing geoinfo on best result and statistical info on all
    if completedOnly == 1:
        f = open(destLocation+'/bestInfo.txt','w')
        fStat = open(destLocation+'/statInfoCompleted.txt','w')
    else:
        fStat = open(destLocation+'/statInfoAll_n'+str(nAnswers)+'.txt','w')

    fSelect = open(destLocation+'/selectedTile.txt','w')
    numberTasks = len(tasksInfo)
    for task in range(numberTasks):
        #Checking if the task has the mininum number of answers
        if (sum(results[task]) < nAnswers):
            #If it has not, lets go to the next task
            continue
        #Geting the selected day for each task
        taskId = tasksInfo[task]['taskId']
        definedArea = tasksInfo[task]['area']
        selectedTile = results[task].index(max(results[task]))
        if selectedTile == 0:
            selectedFile = '2011352'
        elif selectedTile == 1:
            selectedFile = '2011353'
        elif selectedTile == 2:
            selectedFile = '2011355'
        elif selectedTile == 3:
            selectedFile = '2011357'
        elif selectedTile == 4:
            selectedFile = '2011358'
        elif selectedTile == 5:
            selectedFile = '2011359'
        elif selectedTile == 6:
            selectedFile = '2011360'
        elif selectedTile == 7:
            selectedFile = '2011361'
        elif selectedTile == 8:
            selectedFile = '2011362'
        elif selectedTile == 9:
            selectedFile = '2011363'
        elif selectedTile == 10:
            selectedFile = '2011364'
        elif selectedTile == 11:
            selectedFile = '2011365'
        print taskId
        print selectedFile
        print definedArea
        fSelect.write(str(task)+" "+str(taskId)+" "+selectedFile+"\n")
        #Printing bestInfo
        if completedOnly == 1:
            f.write(str(definedArea[0])+" "+ str(definedArea[1])+" "+\
            str(definedArea[2])+" "+str(definedArea[3])+"\n")
        cmd = "gdal_translate -projwin "+str(definedArea[0])+" "+ \
            str(definedArea[3])+" "+str(definedArea[2])+" "+ \
            str(definedArea[1])+" "+origLocation+selectedFile+".tif "+ \
            tmpMosaic+str(taskId)+".tif"
        os.system(cmd)
        #Generating image cuts for all images
        for i in range(numberImages):
            cmd = "gdal_translate -projwin "+str(definedArea[0])+" "+ \
                str(definedArea[3])+" "+str(definedArea[2])+" "+ \
                str(definedArea[1])+" "+origLocation+imgFile[i]+".tif "+ \
                tmpImg[i]+str(taskId)+".tif"
            os.system(cmd)
    #Changing filename based on the type of result (if all results or
    #completed only.
    if completedOnly == 0:
        if nAnswers == 0:
            fileMosaic = "mosaicall"
        else:
            fileMosaic = "mosaicall"+"_n"+str(nAnswers)
    elif completedOnly == 1:
        if nAnswers == 0:
            fileMosaic = "mosaiccompleted"
        else:
            fileMosaic = "mosaiccompleted"+"_n"+str(nAnswers)
    #Checking if the temporary tile folder is not empty
    if os.listdir(tmpMosaic) == []:
        print "No output detected for desired parameter N = " + str(nAnswers)
        #Removing temporary directories
        removeDir(tmpMosaic)
        #Returning error code
        resultCut = 1
        return resultCut
    #Merging the tiles into one mosaic
    cmd = "gdal_merge.py -init '200 200 200' -o "+destLocation+fileMosaic+".tif "+tmpMosaic+ \
        "*.tif"
    os.system(cmd)
    #Copying file with timestamp
    now = datetime.datetime.now()
    timeCreation = now.strftime("%Y-%m-%d_%Hh%M")
    shutil.copyfile(destLocation+fileMosaic+".tif", destLocation+ \
        fileMosaic+"_"+timeCreation+".tif")
    #Close file containing geoinfo on best result
    if completedOnly == 1:
        f.close()
    #Close stat file
    fStat.close()
    fSelect.close()
    #Removing temporary directories
    #~ removeDir(tmpMosaic)
    #~ for i in range(numberImg):
        #~ removeDir(tmpImg[i])
    #Final state
    resultCut = 0
    return resultCut

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

def removeOldFiles(directory,daysLimit):
    """
    Removes old files from a directory older than a given limit
    Example from: http://www.jigcode.com/2009/06/07/python-list-files-older-than-or-newer-than-a-specific-date-and-time/

    :arg string directory: Directory to be analysed
    :arg int daysLimit: Limit to remove files

    :returns: statusRemoval
    :rtype: int
    """
    files = os.listdir(directory)
    files = [ f for f in files if re.search('.tif$', f, re.I)]
    now = time.time()
    for file in files:
        if os.stat(directory+file).st_mtime < now - daysLimit * 86400:
            if os.path.isfile(directory+file):
                os.remove(os.path.join(directory, file))
                print "Old file deleted: ", file
    statusRemoval = 0
    return statusRemoval

def genInput(tasksInfo, results, origLocation, destLocation, typeGray):
    """
    Generate input file for ANN

    :arg list dict tasksInfo: Dictionary list with the tasks info.
    :arg list dict results: Dictionary list with the processed results.
    :arg string origLocation: Directory with orginal images.
    :arg string origLocation: Directory for the results.
    :arg string typeGray: Type of gray scale transformation

    :returns: Nothing
    :rtype: None
    """

    # Training / aplication
    treina = True

    # Sampling pixels from image
    sampl = True
    if sampl == True:
        buildSampl = True
    else:
        buildSampl = False

    # Write data to file
    if treina:
        outInput = open('trainInput.dat', 'w')
        outOutput = open('trainOutput.dat', 'w')
        outOutputClass = open('trainOutputClass.dat', 'w')
    else:
        outInput = open('aplicInput.dat', 'w')
        if verdade:
            outOutput = open('verdadeOutput.dat', 'w')
            outOutputClass = open('verdadeOutputClass.dat', 'w')

    #Setting info on temporary directory for images
    numberImages = 12
    tmpImg = []
    for i in range(numberImages):
        tmpImg.append(destLocation+"tmpImg_n"+str(i+1).zfill(2)+"/")

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

    #Getting number of tasks
    numberTasks = len(tasksInfo)
    for task in range(numberTasks):
        #Geting the selected day for each task
        taskId = tasksInfo[task]['taskId']
        for img in range(numberImages):
            imgName = tmpImg[img] + str(taskId) + '.tif'
            #Openning image (and testing)
            if os.path.exists(imgName) is False:
                #~ print 'Task miss: ' + str(taskId)
                continue
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
            if ((sampl == True) and (buildSampl == True)):
                universe = []
                samplList = []
                random.seed(8225)
                for i in range(rows):
                    for j in range(cols):
                        universe.append([i,j])
                sizeUniverse = len(universe)
                samplSize = int(0.10 * sizeUniverse)
                print 'Sampling mode activated.'
                print 'Using ', samplSize, ' out of ', sizeUniverse, ' pixels.'
                for i in range(samplSize):
                    samplList.append(universe.pop(random.randint(0,len(universe)-1)))
                buildSampl = False


            if (sampl == False):
                #Working with the values
                for i in range(rows):
                    for j in range(cols):
                        #~ valueString = str(float(R_data_sat[i,j])/255.0)+' '+str(float(G_data_sat[i,j])/255.0)+' '+str(float(B_data_sat[i,j])/255.0)
                        valueGray = rgb2gray((float(R_data_sat[i,j])/255.0),(float(G_data_sat[i,j])/255.0),(float(B_data_sat[i,j])/255.0),typeGray)
                        valueString = str(valueGray)
                        outInput.write("%s "%valueString)
            else:
                #Working with the sampled values
                for idx in range(samplSize):
                    i = samplList[idx][0]
                    j = samplList[idx][1]
                    valueGray = rgb2gray((float(R_data_sat[i,j])/255.0),(float(G_data_sat[i,j])/255.0),(float(B_data_sat[i,j])/255.0),typeGray)
                    valueString = str(valueGray)
                    outInput.write("%s "%valueString)

        #Closing the line of the file
        outInput.write("\n")

        #If we are training, then we also generate the true
        if treina:
            selecName = '/home/eduardo/tmpImplement/results/tmpMosaic_n0/' + str(taskId) + '.tif'
            #Openning image (and testing)
            if os.path.exists(selecName) is False:
                print 'Task miss: ' + str(taskId)
                continue
            fileSelec = gdal.Open(selecName, GA_ReadOnly)
            if fileSelec is None:
                print 'Could not open ' + selecName
                sys.exit(1)
            # Read band values from image
            rows = fileSelec.RasterYSize
            cols = fileSelec.RasterXSize
            R_band_selec = fileSelec.GetRasterBand(1)
            G_band_selec = fileSelec.GetRasterBand(2)
            B_band_selec = fileSelec.GetRasterBand(3)
            R_data_selec = R_band_selec.ReadAsArray(0, 0, cols, rows)
            G_data_selec = G_band_selec.ReadAsArray(0, 0, cols, rows)
            B_data_selec = B_band_selec.ReadAsArray(0, 0, cols, rows)
            #Closing image
            fileSelec = None

            if (sampl == False):
                #Working with the values
                for i in range(rows):
                    for j in range(cols):
                        valueGray = rgb2gray((float(R_data_selec[i,j])/255.0),(float(G_data_selec[i,j])/255.0),(float(B_data_selec[i,j])/255.0),'gleam')
                        valueString = str(valueGray)
                        outOutput.write("%s "%valueString)
            else:
                #Working with the values
                for idx in range(samplSize):
                    i = samplList[idx][0]
                    j = samplList[idx][1]
                    valueGray = rgb2gray((float(R_data_selec[i,j])/255.0),(float(G_data_selec[i,j])/255.0),(float(B_data_selec[i,j])/255.0),'gleam')
                    valueString = str(valueGray)
                    outOutput.write("%s "%valueString)

            #Closing line of the file
            outOutput.write("\n")

        selectedTile = results[task].index(max(results[task]))
        if selectedTile == 0:
            selectedFile = '1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0'
        elif selectedTile == 1:
            selectedFile = '0.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0'
        elif selectedTile == 2:
            selectedFile = '0.0 0.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0'
        elif selectedTile == 3:
            selectedFile = '0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0'
        elif selectedTile == 4:
            selectedFile = '0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0'
        elif selectedTile == 5:
            selectedFile = '0.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0'
        elif selectedTile == 6:
            selectedFile = '0.0 0.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 0.0'
        elif selectedTile == 7:
            selectedFile = '0.0 0.0 0.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0'
        elif selectedTile == 8:
            selectedFile = '0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0'
        elif selectedTile == 9:
            selectedFile = '0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0'
        elif selectedTile == 10:
            selectedFile = '0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 1.0 0.0'
        elif selectedTile == 11:
            selectedFile = '0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 1.0'
        outOutputClass.write("%s\n"%selectedFile)

    # Close files
    outInput.close()
    if treina:
        outOutput.close()
        outOutputClass.close()

    statusGenInput = 0
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

    parser.add_option("-s", "--server", dest="server", \
        help="Address to the server", metavar="SERVER")
    parser.add_option("-n", "--app-name", dest="appName", \
        help="Short name of the application", metavar="APPNAME")
    parser.add_option("-t", "--max-number-tasks", dest="maxNumberTasks", \
        help="Maximum number of tasks to be downloaded", \
        metavar="MAXNUMBERTASKS")
    parser.add_option("-a", "--max-number-answers", dest="maxNumberAnswers", \
        help="Maximum number of answers to be downloaded", \
        metavar="MAXNUMBERANSWERS")
    parser.add_option("-c", "--completed-only", dest="completedOnly", \
        help="Get only completed tasks", metavar="COMPLETEDONLY")
    parser.add_option("-i", "--images-directory", dest="imagesDir", \
        help="Directory containing the images", metavar="IMAGESDIR")
    parser.add_option("-d", "--destination-directory", dest="destDir", \
        help="Directory for results", metavar="DESTDIR")
    parser.add_option("-f", "--full-build", dest="fullBuild", \
        help="Build the full set of results", metavar="FULLBUILD")
    parser.add_option("-r", "--remove-files", dest="removeFiles", \
        help="Remove files older than D days", metavar="REMOVEFILES")

    (options, args) = parser.parse_args()

    if options.server:
        server = options.server
    else:
        server = "http://forestwatchers.net/pybossa"
    if options.appName:
        appName = options.appName
    else:
        appName = "besttile"
    if options.maxNumberTasks:
        maxNumberTasks = options.maxNumberTasks
    else:
        maxNumberTasks = 1056
    if options.maxNumberAnswers:
        maxNumberAnswers = options.maxNumberAnswers
    else:
        maxNumberAnswers = 30
    if options.completedOnly:
        completedOnly = options.completedOnly
    else:
        completedOnly = 1
    if options.imagesDir:
        imagesDir = options.imagesDir
    else:
        imagesDir = "/home/eduardo/Testes/fw_img/FAS_Brazil7/"
    if options.destDir:
        destDir = options.destDir
    else:
        #~ destDir = "/home/eduardo/Testes/fw_img/results/"
        destDir = "/home/eduardo/tmpImplement/results/"
    if options.fullBuild:
        fullBuild = options.fullBuild
    else:
        fullBuild = 0
    if options.removeFiles:
        removeFiles = options.removeFiles
    else:
        removeFiles = 9999

    #Get the data and start analysing it
    print "Obtaining AppId..."
    start = time.time()
    globalStart = start
    appId = getAppId(server, appName)
    end = time.time()
    elapsed = end - start
    print "Time taken: ", elapsed, "seconds"
    print " "

    #For complete tasks only
    completedOnly = 1
    print "Obtaining Tasks..."
    start = time.time()
    tasksInfo = getTasks(server, appId, maxNumberTasks, completedOnly)
    end = time.time()
    elapsed = end - start
    print "Time taken: ", elapsed, "seconds"
    print " "
    
    print "Obtaining Results..."
    start = time.time()
    results = getResults(server, tasksInfo, maxNumberAnswers)
    end = time.time()
    elapsed = end - start
    print "Time taken: ", elapsed, "seconds"
    print " "
    
    print "Generating statistics..."
    start = time.time()
    stats = genStats(results, 0)
    end = time.time()
    elapsed = end - start
    print "Time taken: ", elapsed, "seconds"
    print " "
    
    #~ print "Cutting images..."
    #~ start = time.time()
    #~ finalResult = cutTiles(tasksInfo, stats, imagesDir, destDir, \
        #~ completedOnly)
    #~ end = time.time()
    #~ elapsed = end - start
    #~ print "Time taken: ", elapsed, "seconds"
    #~ print " "

    #Genereting input for ANN
    typeGray = 'luminance'
    print "Generating input for ANN..."
    start = time.time()
    input = genInput(tasksInfo, stats, imagesDir, destDir, typeGray)
    end = time.time()
    globalEnd = end
    elapsed = end - start
    globalElapsed = globalEnd - globalStart
    print "Time taken: ", elapsed, "seconds"
    print " "

    #Printing final elapsed time
    print "Total time taken: ", globalElapsed, "seconds"
