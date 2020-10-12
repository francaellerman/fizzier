from tasklib import TaskWarrior, Task
#from subprocess import run
import sys
import pprint
import os

#Note about status and state: some courseworks might have directions to do something after turning in the coursework (often short answer courseworks), but Fizzier will set them as completed in TW.
#It's possible 'RETURNED' can mean the student should do the coursework again, but at my school it seems to only happen after a teacher grades an assignment.

def twshorthand():
  return TaskWarrior()

def add_uda(tw, uda, uda_type):
  tw.execute_command(['config', 'uda.' + uda + '.type', uda_type])
  tw.execute_command(['config', 'uda.' + uda + '.label', uda])

def all_udas():
  with open(os.path.expanduser('~/.taskrc'), 'a') as f:
    f.write("#Fizzier v0.1.0 has inserted the UDAs.")
  tw = TaskWarrior()
  add_uda(tw, 'fizzier_courseId', 'string')
  add_uda(tw, 'fizzier_courseWorkId', 'string')
  add_uda(tw, 'fizzier_alternateLink', 'string')

def look_udas():
  UDAsloaded = False
  with open(os.path.expanduser('~/.taskrc'), 'r') as f:
    for line in f.readlines():
      #print(line)
      if "#Fizzier v0.1.0 has inserted the UDAs." in line:
        UDAsloaded = True
        print("UDasloaded True")
        return
  if not UDAsloaded:
    all_udas()

def in_task_database(tw, cw):
  intacount = int(tw.execute_command(['fizzier_courseWorkId:' + cw, 'count'])[0])
  #print(intacount, " in database")
  if intacount == 1:
    inta = True
  elif intacount == 0:
    inta = False
  else:
    raise Exception("Not zero or one taks with the same courseWorkId.")
  return inta

def stater(state):
  if state == 'TURNED_IN' or state == 'RETURNED':
    status = 'completed'
  else:
    status = 'pending'
  #print("API state: " + state)
  return status

def create_task(tw, courseid, coursename, cwid, title, link, state, sync):
  status = stater(state)
  ntask = Task(tw, fizzier_courseId = courseid, project = coursename, fizzier_courseWorkId = cwid, description = title, fizzier_alternateLink = link, status = status)
  ntask.save()

def modify_task(tw, courseId, courseworkid, title, state):
  status = stater(state)
  mtask = tw.tasks.get(fizzier_courseId = courseId, fizzier_courseWorkId = courseworkid)
  #pprint.pprint(mtask['tags'])
  if not 'fizzier_exclude' in mtask['tags']:
    mtask['description'] = title
    #print(mtask['description'])
    mtask['status'] = status
    #print(mtask['status'])
    mtask.save()

def date_task(tw, courseId, courseworkid, due):
  mtask = tw.tasks.get(fizzier_courseId = courseId, fizzier_courseWorkId = courseworkid)
  mtask['due'] = due
  mtask.save()
