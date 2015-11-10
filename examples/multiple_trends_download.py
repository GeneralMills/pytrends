from pytrends.pyGTrends import pyGTrends
import time
from random import randint

google_username = "xxx@gmail.com"
google_password = "xxxx"
path = ""

# connect to Google
connector = pyGTrends(google_username, google_password)

# Either put your list here or get a text file of words and read it using python

list = ['Red Panda', 'Giant Panda', 'New york', 'California', 'florida', 'as much', 'as you want']
count = 0

for q in list:    
    connector.request_report(q)
    # wait a random amount of time between requests to avoid bot detection
    i = randint(4, 9)
    time.sleep(randint(1*i, 2*i))
    # download file
    i = randint(4, 9)
    count += 1
    connector.save_csv(path, q)
    print (count) + (" files downloaded")    
    time.sleep(randint(1*i, 2*i))
