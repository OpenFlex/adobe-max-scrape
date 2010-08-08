#!/usr/bin/python

import simplejson, urllib, pprint, sys, codecs
from datetime import datetime, timedelta
from icalendar import Calendar,Event,UTC
from operator import itemgetter

def load_speakers():
  speaker_data = simplejson.load(open('speakers.json','r'))
  open('speakers2.json','w').write(simplejson.dumps(speaker_data))
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
  
def write_info_line(f,session):
  line = session['_id']+'\t'+str(len(session['instances']))+'\t'+session['name']+'\n'
  f.write(line.encode('UTF-8'))
  
def denormalize_speakers(session,all_speakers):
  speakers = []
  for speaker_id in session['speakers']:
    speakers.append(all_speakers[speaker_id])
  del session['speakers']
  session['speakers'] = speakers

def build_events(session,cal):
  for i,occurance in enumerate(session['instances']):
    # datestr = occurance['datetime']
    # datestr = occurance['datetime'][:-6]
    # dtstart = datetime.strptime(datestr,'%Y-%m-%dT%H:%M:%S')
    # duration = timedelta(minutes=int(occurance['duration']))
    # dtend = dtstart + duration
    timespan = get_timespan(occurance['datetime'],int(occurance['duration']))
    event = Event()
    event['uid'] = session['_id'] + "-" + str(i)
    event.add('summary',session['name'])
    event.add('description',session['description'])
    event.add('dtstamp',timespan[0])
    event.add('dtstart',timespan[0])
    event.add('dtend',timespan[1])
    event.add('priority',5)
    cal.add_component(event)

def get_timespan(datestr,duration_min):
    datestr = datestr[:-6]
    dtstart = datetime.strptime(datestr,'%Y-%m-%dT%H:%M:%S')
    duration = timedelta(minutes=duration_min)
    dtend = dtstart + duration
    return (dtstart,dtend)

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
  

# find all instances of sessions 
def get_instances(session):
  instances = []
  for instance in session['instances']:
    timespan = get_timespan(instance['datetime'],int(instance['duration']))
    timefmt = '%I:%M%p'
    timestr = timespan[0].strftime(timefmt) + ' - ' + timespan[1].strftime(timefmt)
    instance = {
      'start':timespan[0],'end':timespan[1],
      'daterange':str(timespan[0]) + '-' + str(timespan[1]),
      'key':str(timespan[0]) + '-' + str(timespan[1]) + '-' + session['name'],
      'timestr':timestr,'day':timespan[0].strftime('%A'),
      'name':session['name'],'description':session['description'],'occurances':len(session['instances']),
      'video_url':session['video_url'],
      '_id':session['_id']
      }
    instances.append(instance)
  return instances

def write_agenda(fname,instances,include_descriptions):
  sorted_instances = sorted(instances, key=itemgetter('key'))
  f = codecs.open(fname,'w','utf-8')
  f.write('<html><head><title>Adobe MAX 2010 Agenda</title></head>\n')
  last_slot = ''
  last_day = ''
  for instance in sorted_instances:
    # new time slot?
    if last_day != instance['day']:
      f.write('<h1>' + instance['day'] + '</h1><br/>\n')
    if last_slot != instance['daterange']:
      f.write('<h2>' + instance['timestr'] + '</h2><br/>\n')
    f.write('<h3>' + instance['name'])
    if instance['occurances'] > 1:
      f.write(' (' + str(instance['occurances']) + ')')
    f.write('</h3><br/>\n')
    if include_descriptions:
      f.write(instance['description'] + '<br/><br/>\n')
    last_slot = instance['daterange']
    last_day = instance['day']
    
  f.write('\n</html>\n')
  f.close()

################################################################

eventid = 'ebdabc28-aab4-479f-86f3-6bd9d97b4cc7'
baseurl = 'https://max.adobe.com/api/events/'+eventid+'/sessions/'

cal = Calendar()
cal.add('prodid','-//Adobe MAX 2010//mxm.dk//')
cal.add('version','2.0')
sessionlist = []

speakers = load_speakers()
instances = []

f = open(sys.argv[1][:-4]+'-report.tsv','wb')

linenum = 0
for line in open(sys.argv[1],'r').readlines():
  sessionid = line.strip()
  # load session data (remotely)
  session = load_session(sessionid,sessionlist)
  # save listing of session instances
  instances.extend(get_instances(session))
  # save session id and name to file for quickly glancing at session names later
  write_info_line(f,session)
  # save speaker data with each session for json/couch output
  denormalize_speakers(session,speakers)
  # add all occurances of this session to the calendar
  build_events(session,cal)

f.close()

# write out an agenda
# this is where we could weave in attendees and deconflict in the future
write_agenda(sys.argv[2]+'.html',instances,False)
print 'Agenda written'

# write an iCalendar of found sessions
write_cal(sys.argv[2]+'.ics',cal)
print 'Calendar written'

# write a CouchDB compatible JSON dump of all sessions
write_sessions_as_json(sys.argv[2]+'.json',sessionlist)
print 'JSON written'
