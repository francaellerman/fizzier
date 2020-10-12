from __future__ import print_function
import pickle
import json
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_oauthlib import flow
from google.auth.transport.requests import Request
import os
from os.path import expanduser
import pprint
import datetime

from . import todolists

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

def ojson():
  with open(os.path.expanduser('~/.cache/known_courses.json')) as f:
    data = json.load(f)
  return data

def wjson(data):
  os.path.expanduser('~/.cache/credentials.json')
  with open(os.path.expanduser('~/.cache/known_courses.json'), 'w') as f:
    json.dump(data, f)

#This pickle has the Google authorization code, access token, and refresh token stuff.
def write_pickle(credentials):
  with open(os.path.expanduser('~/.cache/fizzier_gc_creds.pickle'), 'wb') as token:
    pickle.dump(credentials, token)

def open_pickle():
  with open(os.path.expanduser('~/.cache/fizzier_gc_creds.pickle'), 'rb') as token:
    credentials = pickle.load(token)
  return credentials

def og_creds(scope):
  appflow = flow.InstalledAppFlow.from_client_secrets_file(os.path.expanduser('~/.config/credentials.json'), scopes=[scope])
  appflow.run_console()
  credentials = appflow.credentials
  write_pickle(credentials)

def find_creds():
  if not os.path.isfile(os.path.expanduser('~/.cache/fizzier_gc_creds.pickle')):
    og_creds('https://www.googleapis.com/auth/classroom.student-submissions.me.readonly https://www.googleapis.com/auth/classroom.courses.readonly https://www.googleapis.com/auth/classroom.coursework.me.readonly')
  else:
    credentials = open_pickle()
    if not credentials or not credentials.valid:
      if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        write_pickle(credentials)
        #print("Creds refreshed.")

def create_service():
  credentials = open_pickle()
  service = build('classroom', 'v1', credentials=credentials)
  return service

def make_date(cwork):
  duedate = cwork.get('dueDate')
  duetime = cwork.get('dueTime')
  if duedate and duetime:
    #print("dueDate and dueTime exist")
    the_date = datetime.datetime(duedate.get('year'), duedate.get('month'), duedate.get('day'), duetime.get('hours'), duetime.get('minutes', 0), duetime.get('seconds', 0))
    #pprint.pprint(the_date)
  else:
    the_date = False
    #print("the_date = False")
  return the_date

def check_ss_state(service, courseId, courseworkid):
  ss = service.courses().courseWork().studentSubmissions().list(courseId=courseId, courseWorkId=courseworkid).execute()
  if not ss:
    raise Exception("No studentSubmissions().get() results.")
  else:
    state = ss['studentSubmissions'][0]['state']
  return state

def check_single_classwork(service, courseId, coursename, cwork):
  tw = todolists.twshorthand()
  #pprint.pprint(cwork)
  courseworkid = cwork['id']
  title = cwork['title']
  link = cwork['alternateLink']
  #make_date seems to work well
  due = make_date(cwork)
  state = check_ss_state(service, courseId, courseworkid)
  itd = todolists.in_task_database(tw, courseworkid)
  if not itd:
    sync = 1
    todolists.create_task(tw, courseId, coursename, courseworkid, title, link, state, sync)
  elif itd:
    todolists.modify_task(tw, courseId, courseworkid, title, state)
  else:
    raise Exception("Not not in the database but isn't in the database??")
  if not due == False:
    todolists.date_task(tw, courseId, courseworkid, due)

def check_classwork(service, courseId, coursename):
  #print("courseId: " + courseId)
  cw = service.courses().courseWork().list(courseId=courseId).execute()
  knowncourses = ojson()
  if not cw:
    return
  else:
    coursename = knowncourses[courseId]

    for cwork in cw['courseWork']:
      check_single_classwork(service, courseId, coursename, cwork)

def check_courses(service):
  courses = service.courses().list(courseStates='ACTIVE').execute()

  if not courses:
    #print("No courses.")
    return
  else:
    if not os.path.isfile(os.path.expanduser('~/.cache/known_courses.json')):
      #print("Known_courses not found")
      wjson({})
    knowncourses = ojson()

    for course in courses['courses']:
      courseId=course['id']
      coursename=course['name']
      if not courseId in knowncourses:
        #print(coursename + " unknown.")
        knowncourses[courseId] = coursename
        wjson(knowncourses)
      check_classwork(service, courseId, coursename)

def main():
  todolists.taskwarrior.look_udas()
  find_creds()

  service = create_service()
  check_courses(service)
  

if __name__ == '__main__':
  main()

