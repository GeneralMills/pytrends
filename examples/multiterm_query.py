from getpass import getpass
from pprint import pprint
from random import random, randint
from time import sleep
import sys
if sys.version_info[0] == 2:  # Python 2
    import raw_input as input

from pytrends import pytrends

google_username = input('Google username: ')
google_password = getpass('Google password: ')

# connect to google
gt = pytrends.GoogleTrends(google_username, google_password)

# randomize time between requests to avoid bot detection
sleep(1 + random()*randint(1, 4))

# query google trends with search terms, and print out raw data
gt.query(['spam', 'eggs', 'sausage', '"monty python"'],
         is_topic=False)
print(gt.get_data())

sleep(1 + random()*randint(1, 4))

# query google trends with "topics", and print out parsed data
gt.query(['%2Fm%2F070rx', '%2Fm%2F033cnk', '%2Fm%2F0kdzn', '%2Fm%2F04sd0'],
         is_topic=True)
pprint(gt.get_data(parsed=True))

sleep(1 + random()*randint(1, 4))

# query google trends with mix of search terms and "topics"
# and save data to disk in both CSV and JSON forms
gt.query(['spam', '%2Fm%2F033cnk', 'sausage', '%2Fm%2F04sd0'],
         is_topic=[False, True, False, True])
gt.save_data('./multiterm_query.csv')
gt.save_data('./multiterm_query.json')
