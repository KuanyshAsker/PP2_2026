import os 
if os.path.exists("copy_1.txt"):
    os.remove("copy_1.txt")
else:
    print("The file does not exist")
