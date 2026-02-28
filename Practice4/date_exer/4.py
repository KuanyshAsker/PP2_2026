import datetime
date1 = input("Enter datetime1 (YYYY-MM-DD HH:MM:SS): ")
date2 = input("Enter datetime2 (YYYY-MM-DD HH:MM:SS): ")
date1 = datetime.datetime.strptime(date1, "%Y-%m-%d %H:%M:%S")
date2 = datetime.datetime.strptime(date2, "%Y-%m-%d %H:%M:%S")