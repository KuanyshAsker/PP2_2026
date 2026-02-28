import datetime 
today = datetime.datetime.now()
yesterday = today - datetime.timedelta(day=1)
tomorrow = today + datetime.timedelta(day=1)
print(yesterday)
print(today)
print(tomorrow)