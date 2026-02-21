def myfunc(username, **data):
    print("your username", username)
    print("All of your data is below")
    for key, value in data.items():
        print(" ", key + ":", value)
myfunc("kuanysh123", name = "Kuanysh", age = 19, city = "Almaty", university = "KBTU")