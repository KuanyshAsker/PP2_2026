import os

with open("first/1.py", "w") as x:
    x.write("#python first file")
with open("first/second/2.txt", "w") as x:
    x.write("plaintext second file")
with open("first/second/third/3.py", "w") as x:
    x.write("#python third file")

for root, dirs, files in os.walk("first"):
    print("Folder:", root)
    print("Subfolders:", dirs)
    print("Files:", files)