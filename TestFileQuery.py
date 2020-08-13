import json
import sys
import hashlib
import re


# This function converts a STEP file to a JSON object
def stepToJSON(filename):
    f = open(filename, "r")
    # md5.update(f.read())
    contents = f.readlines()
    pattern = re.compile(r"(^#\d+) =\(? ([A-Z0-9_]+) (.+)" )
    inData = False
    myDict = {}
    testDict = {}

    for x in contents:
        if inData == False:
            pass
        else:
            # print(x.rstrip())
            match = pattern.match(x.rstrip())
            if match:
                key = filename + match.groups()[0]

                # print(match.groups()[0], match.groups()[1], match.groups()[2])
                myDict[key, match.groups()[0], match.groups()[1]] = match.groups()[2]

        if 'DATA;' in x:
            inData = True
            print('changed inData variable')
    for k, v in myDict.items():
        print(k, v)
    json.dumps(testDict)



# print(contents)

stepToJSON('step_test_1.STEP')

