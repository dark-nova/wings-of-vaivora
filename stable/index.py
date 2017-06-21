# encoding: utf-8
from datetime import date, datetime, timedelta
from dateutil import parser
from dateutil.relativedelta import relativedelta
import sqlite3, calendar


ch = 1
mins = 30
hour = 8
vhr = int()
vmn = int()

def main(resp):
    text = []
    now = datetime.now()
    then = now - timedelta(hours=4)
    text.append('<!DOCTYPE html>')
    text.append('<html>')
    text.append('<title></title>')
    text.append('<head>')
    text.append('<meta charset=UTF-8>')
    text.append('<style>')
    text.append('body {font-family:sans-serif;font-size:15px;color:#222222}')
    text.append('.mono {font-family:monospace}')
    text.append('.caps {font-variant:small-caps}')
    text.append('table {border-collapase:collapse}')
    text.append('</style>')
    text.append('</head>')
    text.append('<body>')
    if then.hour >= hour and then.minute > mins:
        hour += 4
        mins += 0.5
        channel += 1
        channel %= 2

        verified = False
    if resp == 'POST':
        verified = True
        vhr = now.hour
        vmn = now.minute
    text.append('<form action=/bt/ce>')
    text.append('Old:')
    text.append(str(ch+4))
    text.append('<input type="submit" value="Verify">')
    text.append('</form>')

    text.append('</body>')
    text.append('</html>')
    return [line.encode('utf8') for line in text]


def application(environ, start_response):
    status = '200 OK'
    
    #output = 'Hello world'
    output = main(environ['REQUEST_METHOD'])
    
    response_headers = [('Content-type', 'text/html; charset=utf-8'),
                        ('Content-Length', str(len('\n'.join(output))))]

    start_response(status, response_headers)

    return output

