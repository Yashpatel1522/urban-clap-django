import os

current_working_directory = os.getcwd()

def getusereveymin():
    f = open("demo.txt", "a")
    f.write(current_working_directory)
    f.close()
