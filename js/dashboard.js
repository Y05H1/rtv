
// index.html

if(document.getElementById('redmine_roadmap_status')){
  var table_roadmap_status_desc = ['version', 'due', 'unclosed', 'total', 'status'];
  var table_roadmap_status_unit = ['', '', '', '', '%'];
  setTableBody('redmine_roadmap_status', table_roadmap_status_desc, table_roadmap_status, table_roadmap_status_unit);
}

if(document.getElementById('redmine_gantt')){
  showGantt('redmine_gantt', chart_gantt_projects, chart_gantt_items, chart_gantt_term);
}

// list.html

if(document.getElementById('redmine_weekly_created_tickets')){
  setTableCount('redmine_weekly_created_tickets_count', table_weekly_created_tickets);
  var table_weekly_created_tickets_desc = ['id', 'subject', 'project', 'created', 'assign'];
  var table_weekly_created_tickets_unit = ['', '', '', '', '', ''];
  setTableBody('redmine_weekly_created_tickets', table_weekly_created_tickets_desc, table_weekly_created_tickets, table_weekly_created_tickets_unit);
}

if(document.getElementById('redmine_weekly_closed_tickets')){
  setTableCount('redmine_weekly_closed_tickets_count', table_weekly_closed_tickets);
  var table_weekly_closed_tickets_desc = ['id', 'subject', 'project', 'term', 'assign'];
  var table_weekly_closed_tickets_unit = ['', '', '', 'd', ''];
  setTableBody('redmine_weekly_closed_tickets', table_weekly_closed_tickets_desc, table_weekly_closed_tickets, table_weekly_closed_tickets_unit);
}

if(document.getElementById('redmine_weekly_updated_tickets')){
  setTableCount('redmine_weekly_updated_tickets_count', table_weekly_updated_tickets);
  var table_weekly_updated_tickets_desc = ['id', 'subject', 'project', 'done_ratio', 'assign'];
  var table_weekly_updated_tickets_unit = ['', '', '', '%', ''];
  setTableBody('redmine_weekly_updated_tickets', table_weekly_updated_tickets_desc, table_weekly_updated_tickets, table_weekly_updated_tickets_unit);
}

if(document.getElementById('redmine_total_tickets')){
  var status_list = ['New', 'In Progress', 'Resolved', 'Feedback', 'Closed', 'Rejected', 'Total'];
  showTicketList('redmine_total_tickets', status_list, table_total_tickets_count);
}
if(document.getElementById('redmine_monthly_tickets')){
  var status_list = ['New', 'In Progress', 'Resolved', 'Feedback', 'Closed', 'Rejected', 'Total'];
  showTicketList('redmine_monthly_tickets', status_list, table_monthly_tickets_count);
}
if(document.getElementById('redmine_weekly_tickets')){
  var status_list = ['New', 'In Progress', 'Resolved', 'Feedback', 'Closed', 'Rejected', 'Total'];
  showTicketList('redmine_weekly_tickets', status_list, table_weekly_tickets_count);
}
if(document.getElementById('redmine_unattended_ticket')){
  setTableCount('redmine_unattended_ticket_count', table_unattended_ticket);
  var table_unattended_ticket_desc = ['id', 'subject', 'project', 'updated', 'assign'];
  var table_unattended_ticket_unit = ['', '', '', '', ''];
  setTableBody('redmine_unattended_ticket', table_unattended_ticket_desc, table_unattended_ticket, table_unattended_ticket_unit);
}

// chart.html
if(document.getElementById('chart_transition')){
  showChart('chart_transition', 'line', chart_transition_desc, chart_transition_data);
}
if(document.getElementById('chart_ticketupdate')){
  showChart('chart_ticketupdate', 'bar', chart_monthly_updated_tickets_desc, chart_monthly_updated_tickets_data);
}
if(document.getElementById('chart_lifetime')){
  showChart('chart_lifetime', 'bar', chart_lifetime_desc, chart_lifetime_data);
}
if(document.getElementById('chart_reporter_list')){
  showChart('chart_reporter_list', 'horizontalBar', chart_reporter_list_desc, chart_reporter_list_data);
}

// func

function showGantt(id, gantt_projects, gantt_items, chart_gantt_term) {
  var container = document.getElementById(id);
  var groups = new vis.DataSet(gantt_projects);
  var items = new vis.DataSet(gantt_items);
  var options = {
  groupOrder: function (a, b) {
    return a.value - b.value;
  },
  orientation: 'both',
  editable: false,
  groupEditable: false,
  start: chart_gantt_term[0],
  end: chart_gantt_term[1],
  //height: '600px'
  };

  var timeline = new vis.Timeline(container);
  timeline.setOptions(options);
  timeline.setGroups(groups);
  timeline.setItems(items);
}

function setTableCount(id, table_data) {
  var tbody = document.getElementById(id);
  tbody.innerHTML += " (" + table_data.length + ")";
}

function setTableBody(id, table_desc, table_data, table_unit) {
  var tbody = document.getElementById(id);
  for(i=0;i<table_data.length;i++) {
    var tr = document.createElement("tr");
    for(j=0;j<table_desc.length;j++) {
      var td = document.createElement("td");
      if ( table_unit[j] == '%' ) {
        var div = document.createElement("div");
        div.setAttribute('id','progress');
        div.setAttribute('class','progress-bar');
        div.setAttribute('style','width:'+table_data[i][table_desc[j]]+table_unit[j]);
        div.innerHTML= table_data[i][table_desc[j]]+table_unit[j];
        td.appendChild(div);
      } else {
        td.innerHTML= table_data[i][table_desc[j]] + table_unit[j];
      }
      tr.appendChild(td);
      //td.setAttribute('width',350);
    }
    tbody.appendChild(tr);
  }
}

function showTicketList(id, status_list, ticket_data) {
  
  var tbody = document.getElementById(id);
  //var user_list = [ "root", "user01", "user02" ];
  for (user in ticket_data) {
    //if ( user_list.indexOf(user) == -1 ) {
    //  continue;
    //}
    var tr = document.createElement("tr");
    var td = document.createElement("td");
    td.innerHTML= user;
    tr.appendChild(td);
    
    for(i=0;i<status_list.length;i++) {
      var td = document.createElement("td");
      td.innerHTML= ticket_data[user][status_list[i]];
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
  
}

function showChart(id, type, label, dataset) {
  var config = {
    type: type,
    data: {
    labels: label,
    datasets: dataset,
    },
    options: {
    responsive: true,
    }
  };
  new Chart(document.getElementById(id).getContext("2d"), config);
}
