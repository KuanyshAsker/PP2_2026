import datetime 
today = datetime.datetime.now()
five_d_ago = today - datetime.timedelta(days=5)
print(five_d_ago.date())