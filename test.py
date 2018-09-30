# -*- coding: utf-8 -*-

import pyexcel as pe
import csv
import re
import matplotlib.pyplot as plt
import numpy as np
import datetime
import arcpy

path = 'data/tvrdonice_124_2_21642_crop1_ps.csv'

def csvReader(path):
    with open(path) as csvfile:
        dialect = csv.excel_tab()
        reader = csv.reader(csvfile, dialect=dialect)
        data = list(reader)
        data_split = []
        for value in data:
            value_re = value[0].replace(', ', ' ')  # odstranenie ciarky s medzerou pre dalsie parsrovanie
            # print value_re
            value_split = re.split(',|;|\t',
                                   value_re)  # znaky oddelovaca v csv subore , alebo ; alebo tab (medzera ako odelovac nepodporovany)
            data_split.append(value_split)
    return data_split

def runningMeanFast(x, N):
    return np.convolve(x, np.ones((N,))/N)[(N-1):]

read = csvReader(path)
sheet = pe.Sheet(read)
sheet.name_columns_by_row(0)
header = sheet.colnames

lat = map(float, sheet.column['LAT'])
lon = map(float, sheet.column['LON'])
#plt.plot(lon, lat, 'o')
#plt.show()

print header

dataHeader = []
for d in header[12:]:
    date = d.split('-')

    dataHeader.append(date)


for row in sheet.row:

    data = row[12:]
    elements = np.array(map(float, data))

    """
    mean = np.mean(elements, axis=0)
    sd = np.std(elements, axis=0)
    final_list = [x for x in data if (x > mean - 2 * sd)]
    final_list = [x for x in final_list if (x < mean + 2 * sd)]
    #plt.plot(dataHeader, map(float, data), 'o')
    #plt.plot([dataHeader[0], dataHeader[-1]], [2 * sd, 2 * sd], 'r')
    #plt.plot([dataHeader[0], dataHeader[-1]], [-2 * sd, -2 * sd], 'r')
    plt.boxplot(elements)
    plt.show()
    plt.hist(elements)
    plt.show()"""
    ma = runningMeanFast(elements, 10)
    plt.plot(dataHeader, ma)
    plt.show()


