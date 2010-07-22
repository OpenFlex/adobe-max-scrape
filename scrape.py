#!/usr/bin/python

import simplejson, urllib, pprint, sys
from datetime import datetime, timedelta
from icalendar import Calendar,Event,UTC

def load_speakers():
  speaker_data = simplejson.load(open('speakers.json','r'))
  speakers = {}
  for speaker in speaker_data:
    id = speaker['id']
    speakers[id] = speaker
    del speaker['id']
  return speakers

def load_session(id,list):
  url = baseurl + id + ".json"
  while True:
    try:
      session = simplejson.load(urllib.urlopen(url))
      print 'Loaded session: '+session['name']
      break
    except IOError:
      print 'Error loading url, retrying'
  del session['id']
  session['_id'] = id
  list.append(session)
  return session
  
def denormalize_speakers(session,all_speakers):
  speakers = []
  for speaker_id in session['speakers']:
    speakers.append(all_speakers[speaker_id])
  del session['speakers']
  session['speakers'] = speakers

def build_events(session,cal):
  for i,occurance in enumerate(session['instances']):
    datestr = occurance['datetime']
    datestr = occurance['datetime'][:-6]
    dtstart = datetime.strptime(datestr,'%Y-%m-%dT%H:%M:%S')
    duration = timedelta(minutes=int(occurance['duration']))
    dtend = dtstart + duration
    event = Event()
    event['uid'] = session['_id'] + "-" + str(i)
    event.add('summary',session['name'])
    event.add('description',session['description'])
    event.add('dtstart',dtstart)
    event.add('dtend',dtend)
    event.add('dtstamp',dtstart)
    event.add('priority',5)
    cal.add_component(event)

def write_cal(fname,c):
  f = open(fname,'wb')
  f.write(c.as_string())
  f.close()
  return;
  
def write_sessions_as_json(fname,sessionlist):
  docs = {'docs':sessionlist}
  f = open(fname,'w')
  f.write(simplejson.dumps(docs))
  f.close()

################################################################

eventid = 'ebdabc28-aab4-479f-86f3-6bd9d97b4cc7'
baseurl = 'https://max.adobe.com/api/events/'+eventid+'/sessions/'

cal = Calendar()
cal.add('prodid','-//Adobe MAX 2010//mxm.dk//')
cal.add('version','2.0')
sessionlist = [];

print 'Loading speaker data...'
speakers = load_speakers()
print 'Finished loading speaker data'

linenum = 0
for line in open(sys.argv[1],'r').readlines():
  sessionid = line.strip()
  session = load_session(sessionid,sessionlist)
  denormalize_speakers(session,speakers)
  build_events(session,cal)  
  linenum = linenum + 1
  if linenum%10 == 0:
    print 'Loaded '+str(linenum)+' sessions'

write_cal(sys.argv[2]+'.ics',cal)
print 'Calendar written'

write_sessions_as_json(sys.argv[2]+'.json',sessionlist)
print 'JSON written'
