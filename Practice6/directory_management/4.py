import shutil 

shutil.move("first/second/third/3.py", "first/3.py")
print("I moved 3.py from third inner folder to first folder")

shutil.copy("first/second/2.txt", "first/2_copy.txt")
