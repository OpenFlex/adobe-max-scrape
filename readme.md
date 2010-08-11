# Overview

For a more detailed synopsis, please visit
http://d2fn.com/2010/07/28/schedule-scraping.html

# Usage
This script requires an input file of one id per line of the sessions to scrape.  The included file all-sessions.txt is an example.

Usage:
pythons scrape.py [input-sessions-file] [out]

Called in this way, the scraper will download information for all sessions given in [input-sessions-file].  [out] defines the names of the output files that will be generated.  [out].ics will contain the iCalendar output and [out].json will contain a single json document of all downloaded sessions.  This json document is suitable for uploading to CouchDB

## Dependencies
icalendar library from http://codespeak.net/icalendar/
simplejson

