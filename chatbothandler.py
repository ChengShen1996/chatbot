"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages orders for flowers.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'OrderFlowers' template.

For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.
"""
import math
import dateutil.parser
import datetime
import time
import os
import logging
import datetime
# import requests
from botocore.vendored import requests
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode
API_KEY= 'tlOgofRsGdLuuAC5pUDzAnl_QysN1TmzzQtV6VcRaR-8qPLAHGyxTL1SBEdeFGhE6WQ9g2bUkcICpryqQ2uoqtzkjpzTnQF7hMN8ikILVSEMAPrh33Uv8xTfCM99XHYx' 
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
SEARCH_LIMIT = 3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """

def request(host, path, api_key, url_params=None):
    
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()

def search(api_key, term,open_at ,location):
   
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'open_at':open_at,
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']






""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')






""" --- Intents --- """
def greeting(intent_request):
    output = {
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
                "contentType": "PlainText",
                "content": "How can I help you?"
            }
        }
    }
    return output
def thank_you(intent_request):
    output = {
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
            "contentType": "PlainText",
            "content": "You are welcome!"
           }
        }
    }
    return output
def dining_suggestions(intent_request):
    
    
    term = get_slots(intent_request)["Cuisin"]
    location = get_slots(intent_request)["Location"]
    time = get_slots(intent_request)["Dining_Time"]
    people = get_slots(intent_request)["People"]
    dining_time = time
    time = time.split(':')
    hour = int(time[0])
    minute = int(time[1])
    now = datetime.datetime.now()
    realtime = int(datetime.datetime(now.year,now.month,now.day,hour,minute).timestamp())
    temp = search(API_KEY,term,realtime,location)
    logger.debug(temp)
    logger.debug(temp['businesses'][0]['name'])
    content = "We have found 3 perfect matches. Here are my {} restautrant suggestions for {} at {}:(1).{} at {} (2).{} at {} (3).{} at {}. Have a good meal :)".format(term,people,dining_time,temp['businesses'][0]['name'],temp['businesses'][0]['location']['address1'],temp['businesses'][1]['name'],temp['businesses'][1]['location']['address1'],temp['businesses'][2]['name'],temp['businesses'][2]['location']['address1'])
    # return close({},'Fulfilled',
    #              {'contentType': 'PlainText',
    #               'content': 'I suggest {}'.format(temp['businesses'][0]['name'])})
    output = {
        "dialogAction": {
          "type": "Close",
          "fulfillmentState": "Fulfilled",
          "message": {
            "contentType": "PlainText",
            "content": content
           }
        }
    }
    logger.debug(output)
    # for i,k in event:
    #     print(i,k)
    return output

  
def dining_handler(event):
    # TODO implement
    term = event["currentIntent"]["slots"]["Cuisine"]
    location = event["currentIntent"]["slots"]["Location"]
    price = event["currentIntent"]["slots"]["Price"]
    try:
        response = query_api(term, location, price)
    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )
    name = []
    location = []
    for i in range(3):
        name.append(response[i]["name"])
        loc = response[i]["location"]["display_address"]
        addr = ''
        for j in range(len(loc)):
            addr += loc[j]+' '
        location.append(addr)
    # response = query_api(DEFAULT_TERM, DEFAULT_LOCATION)
    content = "We have found 3 perfect matches: 1. {}, address: {}; 2. {}, address: {}; 3. {}, address: {}".format(
        name[0],location[0],name[1],location[1],name[2],location[2])
    output = {
        "dialogAction": {
          "type": "Close",
          "fulfillmentState": "Fulfilled",
          "message": {
            "contentType": "PlainText",
            "content": content
           }
          
       
     }
   }
    # for i,k in event:
    #     print(i,k)
    return output

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'OrderFlowers':
        return order_flowers(intent_request)
    if intent_name == 'GreetingIntent':
        return greeting(intent_request)
    if intent_name=='ThankYouIntent':
        return thank_you(intent_request)
    if intent_name=='DiningSuggestionsIntent':
        return dining_suggestions(intent_request)


    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
