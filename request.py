from pandas.io.parsers import read_csv
import download
import datetime
from dateutil.relativedelta import relativedelta

inDirectory = "C://GoogleTrends/"
outDirectory = "C:/GoogleTrends/gtFiles/"
file = "Google_Trends_API_File.csv"

#read list from file
csvFile = inDirectory +file
df = read_csv(csvFile, delimiter=',', index_col=False, header=0)
subset = df[["Trend_Name", "Topic_Flag", "API_Query"]]
termList = [tuple(x) for x in subset.values]

#set date for 5yrs ago
fiveYrsAgo = datetime.datetime.now() - relativedelta(years=5)
dateParam = fiveYrsAgo.strftime("%m/%Y")+" 61m"

for term in termList:
    #set REST parameters
    trendParam = term[0]
    topic_flag = term[1]
    if topic_flag == 1:
        topicParam = True
    else:
        topicParam = False
    queryParam = term[2]
    #make REST request
    download.getGTData(trendName=trendParam, path=outDirectory, keywords=queryParam, date=dateParam, topicFg=topicParam)
