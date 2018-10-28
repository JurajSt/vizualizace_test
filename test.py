# -*- coding: utf-8 -*-
import pyexcel as pe
import csv
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import locale
import datetime
import jD
from scipy import interpolate


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

def movingAverage(x, jds, N):
    movAverage_mean, movAverage_median = [], []
    for jd in jds:
        values = []
        for v, val in enumerate(x):
            if jd-(N/2) <= jds[v] <= jd+(N/2):
                values.append(val)
            if jd+(N/2) < jds[v]:
                break
        #plt.plot(test_day, values, 'o')
        #plt.show()
        mean = np.mean(values)
        median = np.median(values)
        movAverage_mean.append(mean)
        movAverage_median.append(median)
    return movAverage_mean, movAverage_median

read = csvReader(path)
sheet = pe.Sheet(read)
sheet.name_columns_by_row(0)
header = sheet.colnames

lat = map(float, sheet.column['LAT'])
lon = map(float, sheet.column['LON'])
#plt.plot(lon, lat, 'o')
#plt.show()

#print header
locale.setlocale(locale.LC_ALL, 'english_united-states.437')  # nastevenie datumu
dataHeader = []
julianDays = []

for d in header[12:]:
    date = datetime.datetime.strptime(d, '%d-%b-%Y').date()
    julianDate = jD.date_to_jd(date.year, date.month, date.day)
    julianDays.append(julianDate)
    dataHeader.append(date)

xnew = []
i = julianDays[0]
while i <= julianDays[-1]:
    xnew.append(i)
    i += 1

for row in sheet.row:

    data = row[12:]
    elements = np.array(map(float, data))
    MA_mean, MA_median = movingAverage(elements, julianDays, 100)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.plot(dataHeader, elements)
    plt.plot(dataHeader, MA_mean)
    plt.plot(dataHeader, MA_median)
    plt.gcf().autofmt_xdate()

    plt.show()