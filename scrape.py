#!/usr/bin/python

import simplejson, urllib, pprint
from datetime import datetime, timedelta
from icalendar import Calendar,Event,UTC

eventid = 'ebdabc28-aab4-479f-86f3-6bd9d97b4cc7'
baseurl = 'https://max.adobe.com/api/events/'+eventid+'/sessions/'

cal = Calendar()

cal.add('prodid','-//ISS Adobe MAX 2010//mxm.dk//')
cal.add('version','2.0')

for line in open('session-ids.txt','r').readlines():
  sessionid = line.strip()
  url = baseurl + sessionid + ".json"
  session = simplejson.load(urllib.urlopen(url))
  open('session-'+sessionid+'.py','w').write(pprint.pformat(session)) 
  
  occurance = session['instances'][0]
  datestr = occurance['datetime']
  datestr = occurance['datetime'][:-6]
  dtstart = datetime.strptime(datestr,'%Y-%m-%dT%H:%M:%S')
  duration = timedelta(minutes=int(occurance['duration']))
  dtend = dtstart + duration
  
  print session['name']
  print dtstart
  print dtend
  print occurance['duration'] , ' min'
  print '\n'
  
  event = Event()
  event['uid'] = sessionid
  event.add('summary',session['name'])
  event.add('description',session['description'])
  event.add('dtstart',dtstart)
  event.add('dtend',dtend)
  event.add('dtstamp',dtstart)
  event.add('priority',5)
  cal.add_component(event)
  

f = open('max2010.ics','wb')
f.write(cal.as_string())
f.close()

print cal.as_string()
print
print 'Calendar written'


  
#       cal = Calendar()
#       from datetime import datetime
#       from icalendar import UTC # timezone
#       cal.add('prodid', '-//My calendar product//mxm.dk//')
#       cal.add('version', '2.0')
#       
#       event = Event()
#       event.add('summary', 'Python meeting about calendaring')
#       event.add('dtstart', datetime(2005,4,4,8,0,0,tzinfo=UTC))
#       event.add('dtend', datetime(2005,4,4,10,0,0,tzinfo=UTC))
#       event.add('dtstamp', datetime(2005,4,4,0,10,0,tzinfo=UTC))
#       event['uid'] = '20050115T101010/27346262376@mxm.dk'
#       event.add('priority', 5)
#       
#       cal.add_component(event)
#       
#       f = open('example.ics', 'wb')
#       f.write(cal.as_string())
#       f.close()

# {u'description': u'Learn how to use Flash Catalyst CS5 to rapidly create and publish an interactive portfolio to the web as a finished SWF file for Adobe Flash Player, or as an Adobe AIR project that can run across platforms outside the browser. See how you can leverage your existing design skills in Adobe Illustrator and Adobe Photoshop to effectively showcase your videos, photos, designs, or products, all without writing any code.',
#  u'event_id': u'ebdabc28-aab4-479f-86f3-6bd9d97b4cc7',
#  u'filter_items': [2,
#                    5,
#                    7,
#                    16,
#                    680,
#                    714,
#                    716,
#                    721,
#                    727,
#                    733,
#                    735,
#                    738,
#                    739,
#                    758],
#  u'has_video': False,
#  u'id': u'065508c2-b237-4274-9e59-7cab85ef2fbd',
#  u'instances': [{u'code': u'',
#                  u'date': u'2010-10-25',
#                  u'datetime': u'2010-10-25T12:45:00-07:00',
#                  u'duration': 90,
#                  u'id': 166,
#                  u'room_id': 22,
#                  u'session_id': u'065508c2-b237-4274-9e59-7cab85ef2fbd',
#                  u'time': u'12:45'}],
#  u'name': u'Building an Interactive Portfolio with Flash Catalyst CS5',
#  u'prerequisites': u'Working knowledge of Adobe Illustrator and Adobe Photoshop',
#  u'private': False,
#  u'speakers': [u'160c6925-0bee-4743-8218-48f320ea2d69'],
#  u'video_url': u''}

