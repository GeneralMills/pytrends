from pyGTrends import pyGTrends
import time
from random import randint

google_username = 'an_account@gmail.com'
google_password = 'paasword'

def getGTData( trendName= "Unknown", path='C:/', keywords = "Unknown", date="all", topicFg="False" ) :
    
    connector = pyGTrends( google_username, google_password )
    connector.download_report(keywords=keywords , trendName = trendName, date = date, topicFg=topicFg)
    time.sleep(randint(5,10))  # Delay for a random amount of seconds (avoid bot detection)

    data = connector.csv(path, trendName)
    print("File saved: %s " % ( trendName.replace(" ","_") + '.csv' ))

