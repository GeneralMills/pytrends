from __future__ import print_function, unicode_literals

from getpass import getpass
from pprint import pprint
import sys

from pytrends import pytrends

if sys.version_info[0] == 2:  # Python 2
    google_username = raw_input('Google username: ')
else:  # Python 3
    google_username = input('Google username: ')
google_password = getpass('Google password: ')

# connect to google
gt = pytrends.GoogleTrends(google_username, google_password, wait=5)

# query google trends with search terms, and print out raw data
gt.query(['spam', 'eggs', 'sausage', '"monty python"'],
         is_topic=False)
print(gt.get_data())

# query google trends with "topics", and print out parsed data
gt.query(['%2Fm%2F070rx', '%2Fm%2F033cnk', '%2Fm%2F0kdzn', '%2Fm%2F04sd0'],
         is_topic=True)
pprint(gt.get_data(parsed=True))

# query google trends with mix of search terms and "topics"
# and save data to disk in both CSV and JSON forms
gt.query(['spam', '%2Fm%2F033cnk', 'sausage', '%2Fm%2F04sd0'],
         is_topic=[False, True, False, True])
gt.save_data('./multiterm_query.csv')
gt.save_data('./multiterm_query.json')
