import numpy as np
import arcpy
import pythonaddins
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import locale
import datetime, time
import os
import math
import scipy.signal as signal
import matplotlib.dates as mdates

locale.setlocale(locale.LC_ALL, 'english_united-states.437')  # nastevenie datumu
arcpy.env.overwriteOutput = True

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

class ButtonClass4(object):
    """Implementation for test4_addin.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        x = tool.x
        y = tool.y
        blockgroups = tool.layer

        field_names = [str(f.name) for f in arcpy.ListFields(blockgroups.name)]

        try:
            N = int(combobox.text)

            # combobox.refresh()
            # query = """ 'FID' = %s """, ss
            dates = []
            julianDays = []
            header = field_names[14:]
            header.insert(0, "FID")

            for name in header[1:]:
                date = datetime.datetime.strptime(name, '%d%b%Y').date()
                julianDate = date_to_jd(date.year, date.month, date.day)
                julianDays.append(julianDate)
                dates.append(date)

            # for v, val in enumerate(field_names[14:]):
            # field = "'" + field_names[v] + "'"
            data = []
            rows = arcpy.SearchCursor(blockgroups.name, header)
            for row in rows:
                if row.getValue(header[0]):
                    value = []
                    for name in header[1:]:
                        value.append(float(row.getValue(name)))

                    data.append(value)
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
            for d in data:

                elements = np.array(map(float, d))
                mean, median = movingAverage(elements, julianDays, N)

                plt.plot(dates, elements, color='red')
                plt.plot(dates, mean, color='blue')
                plt.plot(dates, median, color='green')

                plt.legend(['Input data', 'Moving mean', 'Moving Median'])
                #blue_patch = mpatches.Patch(color='blue', label='moving average mean')
                #green_patch = mpatches.Patch(color='green', label='moving average median')
                #red_patch = mpatches.Patch(color='red', label='raw data')
                #plt.legend(handles=[blue_patch, green_patch, red_patch])
                plt.gcf().autofmt_xdate()
                plt.xlabel('Time')
                plt.ylabel('Elevation mm')
                plt.title('Graph Moving Average')
                plt.savefig("graph")
                plt.clf()
                os.system('start graph.png')


        except Exception as e:
            pythonaddins.MessageBox(e, "ERROR")

class ComboBoxClass3(object):
    """Implementation for test4_addin.combobox (ComboBox)"""
    def __init__(self):
        self.items = []
        self.editable = True
        self.enabled = True
        self.dropdownWidth = 'WWWWW'
        self.width = 'WWWWW'

    def onEditChange(self, text):
        self.text = text

    def refresh(self):
        self.value = " "

class ToolClass2(object):
    """Implementation for test4_addin.tool (Tool)"""
    def __init__(self):
        self.enabled = True
        self.cursor = 3

    def onMouseDownMap(self, x, y, button, shift):

        blockgroups = pythonaddins.GetSelectedTOCLayerOrDataFrame()
        if not blockgroups:
            pythonaddins.MessageBox("Select the block groups layer.", "Info", 0)
            return
        self.x = x
        self.y = y
        self.layer = blockgroups

        sr = arcpy.SpatialReference(arcpy.Describe(blockgroups.name).spatialReference.factoryCode)
        pt = arcpy.PointGeometry(arcpy.Point(x, y), sr)
        arcpy.SelectLayerByLocation_management(blockgroups.name, "WITHIN_A_DISTANCE", pt, search_distance=0.0001,
                                               selection_type='ADD_TO_SELECTION')
        aa = arcpy.Describe(blockgroups.name)
        ss = aa.FIDset
        selectRow = ss.split(';')
        self.sRow = selectRow


