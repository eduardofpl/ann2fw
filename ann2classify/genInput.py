#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  genInput.py
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

import sys
import gdal
import struct
from gdalconst import *

def main():
    print 'Begin'

    # Treinamento / aplicacao ou comparacao com verdade
    treina = True
    verdade = False

    # Write data to file
    if treina:
        outInput = open('trainInput.dat', 'w')
        outOutput = open('trainOutput.dat', 'w')
        outArff = open('train.arff', 'w')
    else:
        outInput = open('aplicInput.dat', 'w')
        if verdade:
            outOutput = open('verdadeOutput.dat', 'w')

    # Original raster files
    listDesArea = ['0_0','0_1','0_2','0_5','0_6','0_8','0_9','0_12','0_14','0_17','0_18','0_32','0_34','3_0','3_4','3_33','3_38','5_32','6_0','9_33']
    #~ listDesArea = ['11_25'] # Compara 1
    #~ listDesArea = ['8_24'] # Compara 2
    #~ listDesArea = ['9_26'] # Compara 3
    #~ listDesArea = ['9_27'] # Compara 4
    #~ listDesArea = ['area_Guatemala']
    if treina:
        print 'For training with ', len(listDesArea), ' tile(s)'
    else:
        print 'For application with ', len(listDesArea), ' tile(s)'
    for desArea in listDesArea:
        inputSat = '/home/eduardo/ForestWatchers/Marilyn/Marilyn_500Km/cuts/Img_'+desArea+'_sattelite.bmp'
        #~ inputSat = '/home/eduardo/ForestWatchers/interest2013/'+desArea+'.tif'
        if treina or verdade:
            inputProdes = '/home/eduardo/ForestWatchers/Marilyn/Marilyn_500Km/cuts/Img_'+desArea+'_prodes.bmp'

        # Open raster files with GDAL
        fileSat = gdal.Open(inputSat, GA_ReadOnly)
        if fileSat is None:
            print 'Could not open ' + inputSat
            sys.exit(1)
        if treina or verdade:
            fileProdes = gdal.Open(inputProdes, GA_ReadOnly)
            if fileProdes is None:
                print 'Cound not open ' + inputProdes
                sys.exit(1)

        # Read band values from raster files
        rows = fileSat.RasterYSize
        cols = fileSat.RasterXSize
        #HARDCODE
        #~ rows = 10
        #~ cols = 10
        # Satellite
        R_band_sat = fileSat.GetRasterBand(1)
        G_band_sat = fileSat.GetRasterBand(2)
        B_band_sat = fileSat.GetRasterBand(3)
        R_data_sat = R_band_sat.ReadAsArray(0, 0, cols, rows)
        G_data_sat = G_band_sat.ReadAsArray(0, 0, cols, rows)
        B_data_sat = B_band_sat.ReadAsArray(0, 0, cols, rows)
        if treina or verdade:
            # Prodes
            R_band_prod = fileProdes.GetRasterBand(1)
            G_band_prod = fileProdes.GetRasterBand(2)
            B_band_prod = fileProdes.GetRasterBand(3)
            R_data_prod = R_band_prod.ReadAsArray(0, 0, cols, rows)
            G_data_prod = G_band_prod.ReadAsArray(0, 0, cols, rows)
            B_data_prod = B_band_prod.ReadAsArray(0, 0, cols, rows)

        # Close raster images
        fileSat = None
        if treina or verdade:
            fileProdes = None

        #Normalize?
        norm = 1

        for i in range(rows):
            for j in range(cols):
                if treina or verdade:
                    if R_data_prod[i,j] == 255:
                        outOutput.write('0.0 1.0\n')
                        valArff = '0'
                    else:
                        outOutput.write('1.0 0.0\n')
                        valArff = '1'
                if norm == 1:
                    valueString = str(float(R_data_sat[i,j])/255.0)+' '+str(float(G_data_sat[i,j])/255.0)+' '+str(float(B_data_sat[i,j])/255.0)
                    outInput.write("%s\n"%valueString)
                    if treina:
                        valueStringArff = str(R_data_sat[i,j])+','+str(G_data_sat[i,j])+','+str(B_data_sat[i,j])+','+valArff
                        outArff.write("%s\n"%valueStringArff)
                else:
                    valueString = str(float(R_data_sat[i,j]))+' '+str(float(G_data_sat[i,j]))+' '+str(float(B_data_sat[i,j]))
                    outInput.write("%s\n"%valueString)
                    if treina:
                        valueStringArff = str(R_data_sat[i,j])+','+str(G_data_sat[i,j])+','+str(B_data_sat[i,j])+','+valArff
                        outArff.write("%s\n"%valueStringArff)

    # Close files
    outInput.close()
    if treina or verdade:
        outOutput.close()
        if treina:
            outArff.close()

    return 0

if __name__ == '__main__':
    main()
