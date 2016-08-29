from pytrends.pyGTrends import pyGTrends
import time
from random import randint

google_username = "an_email@gmail.com"
google_password = "password"
path = ""

# connect to Google
custom_useragent = {'User-Agent': 'My Pytrends Script'}
connector = pyGTrends(google_username, google_password, custom_useragent)


# make request
payload = {'q': ['Pizza, Italian, Spaghetti, Breadsticks, Sausage'], 'cat': '0-71'}
connector.request_report(payload)

# wait a random amount of time between requests to avoid bot detection
time.sleep(randint(5, 10))

# download file
connector.save_csv(path, "pizza")

# get suggestions for keywords
keyword = "milk substitute"
data = connector.get_suggestions(keyword)
print(data)
