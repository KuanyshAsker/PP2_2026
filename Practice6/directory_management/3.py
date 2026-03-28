import os
for root, dirs, folders in os.walk("first"):
    for files in folders:
        if files.endswith(".txt"):
            print(os.path.join(root, files))