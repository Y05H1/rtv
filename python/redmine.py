# -*- coding: utf-8 -*-

import json
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import dateutil.parser
import numpy as np

class RedmineAnalyzer(object):
  def __init__(self, rc):
    self.rc = rc

  def _get_id(self, path='', list_name='', key='', name=''):
    ret = self.rc.get(path=path)
    lists = json.loads(ret.text)
    
    for l in lists[list_name]:
      if l[key] == name:
        return l['id']

    return -1

  def _get_list(self, path, list_name, key):
    ret = self.rc.get(path=path)
    lists = json.loads(ret.text)
    ret_list = []
    for l in lists[list_name]:
      ret_list.append(l[key])
    return ret_list
  
  def get_user_id(self, name=''):
    return self._get_id(path='redmine/users.json', list_name='users', key='login', name=name)

  def get_user_list(self):
    return self._get_list(path='redmine/users.json', list_name='users', key='login')

  def get_project_id(self, name=''):
    return self._get_id(path='redmine/projects.json', list_name='projects', key='name', name=name)

  def get_status_id(self, name=''):
    return self._get_id(path='redmine/issue_statuses.json', list_name='issue_statuses', key='name', name=name)

  def get_status_list(self):
    return self._get_list(path='redmine/issue_statuses.json', list_name='issue_statuses', key='name')


  def get_version_id(self, name=''):
    return self._get_id(path='redmine/projects/1/versions.json', list_name='versions', key='name', name=name)
  
  def get_versions_list(self):
    ret = self.rc.get(path='redmine/projects/1/versions.json')
    lists = json.loads(ret.text)
    ret_list = []
    for l in lists['versions']:
      if ( l['status'] == 'open' ):
        ret_list.append(l['name'])
    return ret_list

  def get_roadmap_status(self, versions_list):
    roadmap_list = []
    for version in versions_list:
      vid = self.get_version_id(name=version)

      query = 'fixed_version_id=' + str(vid) + '&status_id=*&limit=100'
      ret = self.rc.get(path='redmine/issues.json?'+query)
      tickets = json.loads(ret.text)
      fixed_total = 0
      persons = []
      closed_tickets = 0
      for t in tickets['issues']:
        fixed_total += t['done_ratio']
        p = t['assigned_to']['name'].split(" ")[1].lower() if t.has_key('assigned_to') else ''
        persons.append(p)
        if ( t.has_key('closed_on') ):
          closed_tickets += 1
      status = round(( fixed_total / ( 100.0 * tickets['total_count'] ) ) * 100.0,1) if tickets['total_count'] != 0 else 0
      total = tickets['total_count']
      persons = list(set(persons))

      ret = self.rc.get(path='redmine/versions/'+ str(vid) +'.json')
      tickets = json.loads(ret.text)
      due_date = tickets['version']['due_date'] if tickets['version'].has_key('due_date') else '2999-12-31'
      name = tickets['version']['name']

      roadmap_list.append( {'version': version, 'status': status, 'author': persons, 
                            'total': total, 'unclosed': total - closed_tickets, 'due': due_date} )

    return sorted(roadmap_list, key=lambda x:x['due'], reverse=False)


  def get_tickets_list(self, query):
    ret = self.rc.get(path='redmine/issues.json?limit=100&'+query)
    tickets = json.loads(ret.text)
    rslt = []
    for t in tickets['issues']:
      assign = t['assigned_to']['name'].split(" ")[1].lower() if t.has_key('assigned_to') else ''
      author = t['author']['name'].split(" ")[1].lower() if t.has_key('author') else ''
      created = t['created_on'].split("T")[0]
      updated = t['updated_on'].split("T")[0]
      estimated = t['estimated_hours'] if t.has_key('estimated_hours') else 0
      term = 0
      if ( t.has_key('closed_on') ):
        closed_date = dateutil.parser.parse(t['closed_on'])
        created_date =  dateutil.parser.parse(t['created_on'])
        dt = closed_date - created_date
        term = dt.days + 1
      rslt.append({'id':t['id'], 'subject':t['subject'], 'assign':assign, 'author':author, 'term':term, 'status':t['status']['name'],
             'tracker':t['tracker']['name'], 'project':t['project']['name'], 'created':created, 'updated':updated, 
             'estimated':estimated, 'done_ratio':t['done_ratio']})

    return rslt

  def get_tickets_count_per_user(self, user_list, status_list, query=''):
    rslt = {}
    for user in user_list:
      uid = self.get_user_id(name=user)
      rslt[user] = {}
      total_tickets = 0
      for status in status_list:
        sid = self.get_status_id(name=status)
        q = query + '&assigned_to_id=' + str(uid) + '&status_id=' + str(sid)
        ret = self.rc.get(path='redmine/issues.json?'+q)
        lists = json.loads(ret.text)
        rslt[user][status] = lists['total_count']
        total_tickets += lists['total_count']
      rslt[user]['Total'] = total_tickets

    return rslt

  def get_tickets_count(self, query):
    ret = self.rc.get(path='redmine/issues.json?'+query)
    tickets = json.loads(ret.text)
    return tickets['total_count']
  
  def get_tickets_transition_per_tracker(self, search=[], query='', label=''):
    data = []
    for s in search:
      created_tickets = self.get_tickets_count(query='status_id=*&created_on=<='+s+'&'+query)
      closed_tickets = self.get_tickets_count(query='status_id=*&closed_on=<='+s+'&'+query)
      data.append(created_tickets - closed_tickets)
    return {'label': label, 'data': data}
    

  def get_tickets_lifetime(self, max=1000, query=''):
    q = 'status_id=closed&limit=100&' + query
    pages = self.get_tickets_count(query=q)/100 + 1
    tickets = []
    #print pages
    for p in range(pages):
      ret = self.rc.get(path='redmine/issues.json?'+'page='+str(p+1)+'&'+q)
      ret2 = json.loads(ret.text)
      tickets.extend(ret2['issues'])

    term = []
    term_map = {}
    for t in tickets:
      closed_date = dateutil.parser.parse(t['closed_on'])
      created_date =  dateutil.parser.parse(t['created_on'])
      dt = closed_date - created_date
      day = dt.days + 1 if dt.days < max else max
      term.append(day)
      if not term_map.has_key(day):
        term_map[day] = 0
      term_map[day] += 1
    if len(term) == 0:
      return term_map
    np_data = np.array(term)
    for i in range(1,np.max(np_data)+1):
      if not term_map.has_key(i):
        term_map[i] = 0

    return term_map


  def get_updated_ticket_count(self, search_month=[], status='', query='', label=''):
    rslt = []
    for m in search_month:
      nextmonth = m + relativedelta(months=1)
      q = 'status_id=*&'+status+'=><'+m.strftime('%Y-%m-%d')+'|'+nextmonth.strftime('%Y-%m-%d') + '&' + query
      rslt.append(self.get_tickets_count(query=q))
    return {'label':label, 'data':rslt}
  
  def get_updated_tickets_transition(self, term):
    sm = self.get_term(term=term)
    monthly_created_tickets = self.get_updated_ticket_count(search_month=sm, status='created_on', label='created')
    monthly_closed_tickets = self.get_updated_ticket_count(search_month=sm, status='closed_on', label='closed')
    monthly_updated_tickets_data = []
    monthly_updated_tickets_data.append(monthly_created_tickets)
    monthly_updated_tickets_data.append(monthly_closed_tickets)
    monthly_updated_tickets_desc = self.get_term(term=term, mode='%Y-%m')
    return (monthly_updated_tickets_desc, monthly_updated_tickets_data)


  def get_reporter_list(self, user_list=[], query=''):
    rslt = {}
    for user in user_list:
      uid = self.get_user_id(name=user)
      q = query + '&author_id=' + str(uid) + '&status_id=*'
      rslt[user] = self.get_tickets_count(query=q)
    
    return rslt

  def set_date(self, day, val=1):
    if val==0:
      val = 1
    return date(day.year, day.month, val)
  
  def get_term(self, term, inc=False, per=1, mode=''):
    search = []
    ignores = [1]
    today = date.today()
    target = self.set_date(today, 1)
    for i in range(term):
      target2 = target - relativedelta(months=i)
      for j in range(per):
        target3 = self.set_date(target2, 30/per*j)
        ignores.append( 30/per*j )
        if today < target3:
          continue
        target4 = target3.strftime(mode) if mode != '' else target3
        search.append( target4 )
    if inc and today.day not in ignores:
      td = today.strftime(mode) if mode != '' else today
      search.append(td)
    search.sort()
    #search.reverse()
    return search


  def get_gantt_data(self, query):
    ret = self.rc.get(path='redmine/issues.json?limit=100&'+query)
    tickets = json.loads(ret.text)
    pdict = {}
    plist = []
    tlist = []
    rslt = {}
    for t in tickets['issues']:
      group = t['project']['id']
      if not pdict.has_key(group):
        plist.append({'id':group, 'content':t['project']['name']})
        pdict[group] = True
      
      type = 'point' if ( t['status']['id'] == 1 ) else 'range'
      start = t['created_on'].split("T")[0]
      end   = t['closed_on'] if ( t.has_key('closed_on') ) else t['updated_on'].split("T")[0]
      end   = dateutil.parser.parse(end) + relativedelta(days=1)
      classname = ''
      if ( t['status']['id'] == 1 ):
        classname = 'created'
      elif ( t.has_key('closed_on') ):
        classname = 'closed'
      else:
        classname = 'updated'
      content = '#' + str(t['id']) + ' ' +t['subject']
      tlist.append({'group':group, 'content':content, 'start':start, 'end':end.strftime('%Y-%m-%d'), 'className':classname, 'type':type});

    #return sorted(roadmap_list, key=lambda x:x['due'], reverse=False)

    #plist = sorted(plist, key=lambda x:x['id'])
    rslt['groups'] = sorted(plist, key=lambda x:x['id'])
    rslt['items'] = tlist
    return rslt

  def get_gantt_term(self, before=10, after=3):
    end_date = date.today() + relativedelta(days=after)
    start_date = end_date - relativedelta(days=before)
    return [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]

  def get_trackers_list(self):
    return self._get_list(path='redmine/trackers.json', list_name='trackers', key='name')

  def get_trackers_id(self, name=''):
    return self._get_id(path='redmine/trackers.json', list_name='trackers', key='id', name=name)

  def get_tickets_transition(self, search, trackers):
    ret = []
    tr = self.get_tickets_transition_per_tracker(search=search, label='total')
    ret.append(tr)
    for tracker in trackers:
      id = self.get_trackers_id(name=tracker)
      tr = self.get_tickets_transition_per_tracker(search=search, label=tracker, query='tracker_id='+str(id))
      ret.append(tr)
    return ret
