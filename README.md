# rtv
Redmine ticket viewer

## Description
This is a tool to visualize the Redmine ticket.
collector.py gets the data from the Redmine.
web page will display the data that collector.py has collected.

## Requirement
The following OS, libraries are required

- CentOS 6.8
- python 2.6.6(system default)
- json
- relativedelta
- numpy

## Install
After you install the web server, and clone.

```
# yum install httpd
# cd /var/www/html
# git clone https://github.com/Y05H1/rtv.git
# /etc/init.d/httpd start
```

## Usage

#### change redmine information
Change the api_key and host of redmine.

```
# cd /var/www/html/rtv/python/
# cat collector.py
...
""" parameter """
redmine_api_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
redmine_host = 'http://127.0.0.1/'
...
```

#### get redmine information
Get the information from redmine.
After the execution, data.js is generated.

```
# python collector.py
```

#### view redmine data
Access to the following URL

```
http://<your web server ip>/rtv
```

