#Import the libraries
import json
import os
import urllib.request
import dateutil.parser
import datetime
from datetime import date

#The format_message fucntions formats the necessary event information
#and constrtucts the payload as a python dictionary
def format_message(data):
    severity_level = get_severity_level(data['detail']['severity'])
    print(severity_level)
    #Call the countOccurences fucntions to check if there are more than one occurences in the same day
    occ=countOccurences(data)
   
    
    payload = {
        'username': 'GuardDuty Finding',
        'icon_emoji': ':guardduty:',
        'text': '{} GuardDuty Finding in {}'.format(severity_level['mention'], data['detail']['region']),
        'attachments': [
            {
                'fallback': 'Detailed information on GuardDuty Finding.',
                'color': severity_level['color'],
                'title': data['detail']['title'],
                'text': data['detail']['description'],
                'fields': [
                    {
                        'title': 'Account ID',
                        'value': data['detail']['accountId'],
                        'short': True
                    },
                    {
                        'title': 'Severity',
                        'value': severity_level['label'],
                        'short': True
                    },
                    {
                        'title': 'Type',
                        'value': data['detail']['type'],
                        'short': False
                    },
                    {
                        'title': 'Number of Occurences',
                        'value': occ,
                        'short': True
                    }
                ]
            }
        ]
    }
    return payload

 
#This function categorises the severity as 'high' and 'critical' based on the 
#numerical severity value
def get_severity_level(severity):
    # ref: http://docs.aws.amazon.com/guardduty/latest/ug/guardduty_findings.html#guardduty_findings-severity
    if 7.0 <= severity <= 8.9:
        level = {'label': 'High', 'color': 'danger', 'mention': '<!channel>'}
    else: 
        level = {'label': 'Critical', 'color': 'danger', 'mention': '<!channel>'}
   
    return level
    
#The notify Slack functions will convert the payload to JSON format, returns the response to the handler 
def notify_slack(url, payload):
    data = json.dumps(payload).encode('utf-8')
    method = 'POST'
    headers = {'Content-Type': 'application/json'}

    request = urllib.request.Request(url, data = data, method = method, headers = headers)
    with urllib.request.urlopen(request) as response:
        return response.read().decode('utf-8')
 #This fucntion sends an alert to Slack if there are more than one occurence of the same event in the same day
def countOccurences(data):
    #Parsing the eventFirstSeen and eventLastseen timestamps and converting them to date
    eventLastSeen=dateutil.parser.parse(data['detail']['service']['eventLastSeen'])
    eventFirstSeen=dateutil.parser.parse(data['detail']['service']['eventFirstSeen'])
    
    #The number of occurences of the event 
    count=data['detail']['service']['count']
    
    #Find the differnce in the timestamps
    Datediff=eventLastSeen-eventFirstSeen
    
    #Send an alert to Slack if there are more than one occurence of the same event in the same day
    if(Datediff.days<=1 and count>1):
      occurence= "There are "+str(count)+" occurences in "+str(diff.days+1)+" day"
    return occurence
     
  

def lambda_handler(event, context):
    
    webhook_url = os.environ['WEBHOOK_URL']
    #Filter the low and medium events 
    if not 0.0 <= event['detail']['severity'] <= 6.9:
        payload = format_message(event)
    else:
        return ''
    #call the notify_slack() fucntion with payload as a python dictionary
     response = notify_slack(webhook_url, payload)

    #print Log_stream and log groups in the console to enable trouble shooting
    print("Log stream name:", context.log_stream_name)
    print("Log group name:",  context.log_group_name)
    print("Request ID:",context.aws_request_id)
    print("Mem. limits(MB):", context.memory_limit_in_mb)
    
    return response

