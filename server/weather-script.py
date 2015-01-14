#!/usr/bin/python2

import urllib2
from xml.dom import minidom
import codecs
import time
import pytz
import datetime
import tableview

utc = pytz.utc

LATITUDE  =  36.012731
LONGITUDE = -78.9066788
TIMEZONE = 'US/Eastern'

ICONS = {
	'bkn'      : '_partly_sunny',
	'dust'     : '_fog',
	'few'      : '_partly_sunny',
	'fg'       : '_fog',
	'fzra'     : '_hail',
	'fzrara'   : '_wintry_mix',
	'hi_shwrs' : '_light_rain',
	'hi_tsra'  : '_light_tstorm',
	'ip'       : '_hail',
	'mist'     : '_fog',
	'mix'      : '_wintry_mix',
	'nsurtsra' : '_doge',
	'ovc'      : '_cloudy',
	'ra'       : '_heavy_rain',
	'ra1'      : '_light_rain',
	'raip'     : '_hail',
	'rasn'     : '_wintry_mix',
	'sct'      : '_partly_sunny',
	'shra'     : '_light_rain',
	'skc'      : '_sunny',
	'smoke'    : '_fog',
	'sn'       : '_heavy_snow',
	'tsra'     : '_heavy_tstorm',
	'wind'     : '_wind',
	'scttsra'  : '_light_tstorm'
}

# Fetch data (change lat and lon to desired location)
weather_xml = urllib2.urlopen('http://graphical.weather.gov/xml/SOAP_server/ndfdSOAPclientByDay.php?whichClient=NDFDgenByDay&lat=%s&lon=%s&format=24+hourly&numDays=4&Unit=e' % (LATITUDE, LONGITUDE)).read()
dom = minidom.parseString(weather_xml)

# Parse temperatures
xml_temperatures = dom.getElementsByTagName('temperature')
highs = [None]*4
lows = [None]*4
for item in xml_temperatures:
    if item.getAttribute('type') == 'maximum':
        values = item.getElementsByTagName('value')
        for i in range(len(values)):
            highs[i] = int(values[i].firstChild.nodeValue)
    if item.getAttribute('type') == 'minimum':
        values = item.getElementsByTagName('value')
        for i in range(len(values)):
            lows[i] = int(values[i].firstChild.nodeValue)

# Parse icons
xml_icons = dom.getElementsByTagName('icon-link')
icons = [None]*4
for i in range(len(xml_icons)):
    icon = xml_icons[i].firstChild.nodeValue.split('/')[-1].split('.')[0].rstrip('0123456789')
    if icon not in ICONS:
    	print icon
    icons[i] = ICONS.get(icon, '_doge')
    
# Parse dates
xml_day_one = dom.getElementsByTagName('start-valid-time')[0].firstChild.nodeValue[0:10]
day_one = datetime.datetime.strptime(xml_day_one, '%Y-%m-%d')

# Parse time
now = utc.localize(datetime.datetime.utcnow())
local = pytz.timezone(TIMEZONE)
now = now.astimezone(local)
time_string = now.strftime('%I:%M').lstrip('0')

# Parse recycling schedule
schedule = tableview.load('recycling_schedule.csv')
pickup_days = set()
for row in schedule[1:]:
    year = int(row[0])
    month = int(row[1])
    days = [int(cell) for cell in row[2:] if cell]
    for day in days:
        pickup_days.add((year,month,day))
warning_days = [now + datetime.timedelta(days=n) for n in range(3)]
warning_days = [(day.year, day.month, day.day) for day in warning_days]

recycling = False
for day in warning_days:
    if day in pickup_days:
        recycling = True


print "Summary"
print "-------"
print      "Highs: %s" % highs
print "      Lows: %s" % lows
print "     Icons: %s" % icons
print "        TZ: %s" % local
print "      Time: %s" % time_string
print " Recycling: %s" % recycling
output = codecs.open('clock_inkscape.svg', 'r', encoding='utf-8').read()

output = output.replace('88:88', time_string)

for i in range(3):
	output = output.replace('D%dH' % i, str(highs[i]))
	output = output.replace('D%dL' % i, str(lows[i]))
	output = output.replace('#_use_d%d' % i, ('#' + icons[i]))

if recycling:
    output = output.replace('#_use_g0', '#_recycle')

codecs.open('clock-output.svg', 'w', encoding='utf-8').write(output)

'''
#
# Preprocess SVG
#

# Open SVG to process
output = codecs.open('weather-script-preprocess.svg', 'r', encoding='utf-8').read()

# Insert icons and temperatures
output = output.replace('ICON_ONE',icons[0]).replace('ICON_TWO',icons[1]).replace('ICON_THREE',icons[2]).replace('ICON_FOUR',icons[3])
output = output.replace('HIGH_ONE',str(highs[0])).replace('HIGH_TWO',str(highs[1])).replace('HIGH_THREE',str(highs[2])).replace('HIGH_FOUR',str(highs[3]))
output = output.replace('LOW_ONE',str(lows[0])).replace('LOW_TWO',str(lows[1])).replace('LOW_THREE',str(lows[2])).replace('LOW_FOUR',str(lows[3]))

# Insert days of week
one_day = datetime.timedelta(days=1)
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
output = output.replace('DAY_THREE',days_of_week[(day_one + 2*one_day).weekday()]).replace('DAY_FOUR',days_of_week[(day_one + 3*one_day).weekday()])

# Write output
codecs.open('weather-script-output.svg', 'w', encoding='utf-8').write(output)
'''
