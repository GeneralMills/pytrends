from pyGTrends import pyGTrends
import time
from random import randint

google_username = "an_account@gmail.com"
google_password = "password"
path = ""

#connect to Google
connector = pyGTrends(google_username, google_password)

#make request
connector.request_report("Pizza")

#download file
connector.csv(path, "pizza")


