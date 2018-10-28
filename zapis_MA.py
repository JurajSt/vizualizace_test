# -*- coding: utf-8 -*-

import pyexcel as pe
import csv
import numpy as np
import os, re
import datetime
import math

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
            value_split = re.split(',|;|\t', value_re)  # znaky oddelovaca v csv subore , alebo ; alebo tab (medzera ako odelovac nepodporovany)
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
        mean = round(np.mean(values), 3)
        median = round(np.median(values), 3)
        movAverage_mean.append(mean)
        movAverage_median.append(median)
    return movAverage_mean, movAverage_median

def date_to_jd(year, month, day):
    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month
    # this checks where we are in relation to October 15, 1582, the beginning
    # of the Gregorian calendar.
    if ((year < 1582) or
            (year == 1582 and month < 10) or
            (year == 1582 and month == 10 and day < 15)):
        # before start of Gregorian calendar
        B = 0
    else:
        # after start of Gregorian calendar
        A = math.trunc(yearp / 100.)
        B = 2 - A + math.trunc(A / 4.)
    if yearp < 0:
        C = math.trunc((365.25 * yearp) - 0.75)
    else:
        C = math.trunc(365.25 * yearp)
    D = math.trunc(30.6001 * (monthp + 1))
    jd = B + C + D + day + 1720994.5
    return jd


vystup = os.path.join("data/tvrdonice_124_2_21642_crop1_ps_MA.csv")
zapis = open(vystup, "w")
read = csvReader(path)
sheet = pe.Sheet(read)
sheet.name_columns_by_row(0)
header = sheet.colnames

lat = map(float, sheet.column['LAT'])
lon = map(float, sheet.column['LON'])
#plt.plot(lon, lat, 'o')
#plt.show()

dataHeader = []
julianDays = []

for d in header[12:]:
    date = datetime.datetime.strptime(d, '%d-%b-%Y').date()
    julianDate = date_to_jd(date.year, date.month, date.day)
    julianDays.append(julianDate)
    dataHeader.append(date)

dat_header = 'ID,LAT,LON'
for d in header[12:]:
    dat_header = dat_header + ','
    tx_date = d.replace('-', '')
    dat_header = dat_header + tx_date
dat_header = dat_header + '\n'
zapis.write(dat_header)

text = ''
for s in sheet.row:
    print s[0]
    text = text + s[0] + ',' + s[3] + ',' + s[4]
    ma = movingAverage(map(float, s[12:]), julianDays, 100)
    for ss in ma[0]:
        text = text + ','
        text = text + str(ss)
    text = text + '\n'
    zapis.write(text)
    text = ''

zapis.close()