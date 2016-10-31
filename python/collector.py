# -*- coding: utf-8 -*-

import sys, json
from rest import RestClient
from redmine import RedmineAnalyzer

""" parameter """
redmine_api_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
redmine_host = 'http://127.0.0.1/'
output_file = '../js/data.js'

rc = RestClient(api_key=redmine_api_key, host=redmine_host)
ra = RedmineAnalyzer(rc)

def _debug(con):
  if len(sys.argv) >= 2:
    print con

if len(sys.argv) >= 2:
  print "Debug mode"

print "get common data ..."
ul = ra.get_user_list()
_debug(ul)
sl = ra.get_status_list()
_debug(sl)
vl = ra.get_versions_list()
_debug(vl)
tl = ra.get_trackers_list()
_debug(tl)



""" index.html - start """
print "get roadmap status ..."
roadmap_status = ra.get_roadmap_status(versions_list=vl)
_debug(roadmap_status)

print "get gantt data ..."
gantt_term = ra.get_gantt_term()
_debug(gantt_term)
gantt_data = ra.get_gantt_data(query='status_id=*&updated_on=>t-7')
_debug(gantt_data)

""" index.html - end """

""" list.html - start """
print "get weekly modified tickets ..."
weekly_created_tickets = ra.get_tickets_list(query='status_id=*&created_on=>t-7')
_debug(weekly_created_tickets)
weekly_closed_tickets = ra.get_tickets_list(query='status_id=*&closed_on=>t-7')
_debug(weekly_closed_tickets)
weekly_updated_tickets = ra.get_tickets_list(query='updated_on=>t-7&status_id=!1|5|6')
_debug(weekly_updated_tickets)

print "get tickets count per user ..."
total_tickets_count = ra.get_tickets_count_per_user(user_list=ul, status_list=sl)
_debug(total_tickets_count)
weekly_tickets_count = ra.get_tickets_count_per_user(user_list=ul, status_list=sl, query='updated_on=>t-7')
_debug(weekly_tickets_count)
monthly_tickets_count = ra.get_tickets_count_per_user(user_list=ul, status_list=sl, query='updated_on=>t-30')
_debug(monthly_tickets_count)

print "get unattended ticket ..."
unattended_tickets = ra.get_tickets_list(query='sort=updated_on&limit=20')
_debug(unattended_tickets)

""" list.html - end """

""" chart.html - start """
print "get tickets transition ..."
search_month = ra.get_term(term=6, inc=True, mode='%Y-%m-%d', per=2)
_debug(search_month)
tickets_transition = ra.get_tickets_transition(search=search_month, trackers=tl)
_debug(tickets_transition)

print "get tickets lifetime ..."
tickets_lifetime = ra.get_tickets_lifetime(max=100)
_debug(tickets_lifetime.keys())
tickets_lifetime_data = []
tickets_lifetime_data.append({'label':'total', 'data':tickets_lifetime.values()})
_debug(tickets_lifetime_data)

print "get monthly modified tickets transition ..."
monthly_updated_tickets_desc, monthly_updated_tickets_data = ra.get_updated_tickets_transition(term=6)
_debug(monthly_updated_tickets_desc)
_debug(monthly_updated_tickets_data)

print "get reporter list ..."
reporter_list = ra.get_reporter_list(ul)
weekly_reporter_list = ra.get_reporter_list(user_list=ul, query='created_on=>t-7')
_debug(reporter_list)
_debug(weekly_reporter_list)
reporter_list_data = []
reporter_list_data.append({'label':'total', 'data':reporter_list.values()})
reporter_list_data.append({'label':'weekly', 'data':weekly_reporter_list.values()})
_debug(reporter_list_data)

""" chart.html - end """

""" write to file """
file_contents = {
  #index
  'table_roadmap_status': roadmap_status,
  'chart_gantt_term': gantt_term,
  'chart_gantt_projects': gantt_data['groups'],
  'chart_gantt_items': gantt_data['items'],
  #list
  'table_weekly_created_tickets': weekly_created_tickets,
  'table_weekly_closed_tickets': weekly_closed_tickets,
  'table_weekly_updated_tickets': weekly_updated_tickets,
  'table_weekly_tickets_count': weekly_tickets_count,
  'table_monthly_tickets_count': monthly_tickets_count,
  'table_total_tickets_count': total_tickets_count,
  'table_unattended_ticket': unattended_tickets,
  #chart
  'chart_transition_desc': search_month,
  'chart_transition_data': tickets_transition,
  'chart_lifetime_desc': tickets_lifetime.keys(),
  'chart_lifetime_data': tickets_lifetime_data,
  'chart_monthly_updated_tickets_desc': monthly_updated_tickets_desc,
  'chart_monthly_updated_tickets_data': monthly_updated_tickets_data,
  'chart_reporter_list_desc': reporter_list.keys(),
  'chart_reporter_list_data': reporter_list_data,
}

print "write output file ..."
with open(output_file, 'w') as f:
  for k, v in file_contents.iteritems():
    f.write('var '+k+' = \n')
    json.dump(v, f, sort_keys=True, indent=2)
    f.write(';\n')

print "finished"
