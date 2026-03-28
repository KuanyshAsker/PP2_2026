import shutil 
source = "1.txt"
backup = "backup_1.txt"

shutil.copy("1.txt", "copy_1.txt") #copy
shutil.copy2(source, backup) #backup

