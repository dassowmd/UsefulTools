from fuzzywuzzy import fuzz
import sys
import csv
import os
import argparse

#Test with csv load
def LoadCSV(filepath):
    with open(filepath, 'rb') as f:
        reader = csv.reader(f)
        l = []
        for s in reader:
            l.append(s[0])
        # l = list(reader)
    f.close()
    return l
def LoadManual(string):
    l = []
    for s in string.lower().split(","):
        l.append(s)
    return l

# fileLocation is intentionally not being used. Just wanted a quick hack to be able to call it after assigning it to the outputMethod (needed 3 params to match the same method)
def printResults(matchList, SaveFileLocation):
    if len(matchList) > 0:
        # print('\n' + 'List for ' + item)
        for i in matchList:
            print str(i[0]) + " | " + str(i[1]) + " | " +    str(i[2]) + " | " + str(i[3]) + " | " + str(i[4])
        raw_input("Press Enter go to next")

def saveResults(matchList, SaveFileLocation):
    if os.path.exists(SaveFileLocation):
        try:
            os.remove(SaveFileLocation)
        except Exception as e:
            print('\nFile' + SaveFileLocation + ' in use, please close and hit "Enter"\n')
            raw_input()
            saveResults(item, matchList, SaveFileLocation)
    with open(SaveFileLocation, 'wb') as csvFile:
        writer = csv.writer(csvFile)
        if len(matchList) > 0:
            writer.writerow(['Item', 'Matched Item', 'Full Match Percent', 'Partial Match Percent', 'Token Match Percent'])
            for i in matchList:
                writer.writerow([i[0], i[1], i[2], i[3], i[4]])

def getMatches(List1, List2, ignoreCase, fullOrPartialOrToken, ratioPercent, SaveFileLocation, matchLimit):
    matchList = []
    for item in List1:
        tempMatchList = []
        word1 = str(item).strip()
        sys.stdout.write('.')
        for word in List2:
            rFull = 0
            rPartial = 0
            rToken = 0
            word2 = str(word).strip()
            if ignoreCase == "yes":
                word1 = word1.lower()
                word2 = word2.lower()
            if fullOrPartialOrToken == 'full':
                rFull = fuzz.ratio(word1,word2)
            elif fullOrPartialOrToken == 'partial':
                rPartial = fuzz.partial_ratio(word1,word2)
            elif fullOrPartialOrToken == 'token':
                rToken = fuzz.token_set_ratio(word1,word2)
            elif fullOrPartialOrToken == 'all':
                rFull = fuzz.ratio(word1,word2)
                rPartial = fuzz.partial_ratio(word1,word2)
                rToken = fuzz.token_set_ratio(word1,word2)
            else:
                raise("\nI don't recognize that command")

            if rFull > int(ratioPercent) or rPartial > int(ratioPercent) or rToken > int(ratioPercent):
                tempMatchList.append([word1, word2, rFull, rPartial, rToken])
        # Compare length of list to match limit to account for when comparing a list to itself
        if len(tempMatchList) > matchLimit:
            matchList.extend(tempMatchList)
    return matchList

def main(argDict):
    # loadType = 'csv'
    # fullOrPartialOrToken = 'all'
    # ignoreCase = True
    # output = 'print'
    # ratioPercent = 80
    # matchLimit = 0
    # SaveFileLocation = 'null'
    List1 = []
    List2 = []

    if argDict['loadType'] == None:
        loadType = raw_input('Would you like to load from CSV or manual input? (Import "CSV" or "Manual")\n\n').lower()
    if argDict['loadType'] == "csv":
        if argDict['fileLocation_List1'] == None:
            argDict['fileLocation_List1'] = raw_input('Please enter the absolute file path of the 1st file you would like to load\n')
        List1 = LoadCSV(argDict['fileLocation_List1'])
        if argDict['fileLocation_List2'] == None:
            argDict['fileLocation_List2'] = raw_input('Please enter the absolute file path of the 2nd file you would like to load\n')
        List2 = LoadCSV(argDict['fileLocation_List2'])
    elif(argDict['loadType'] == 'manual'):
        List1 = LoadManual(raw_input('Please enter a comma separated list for list 1\n\n'))
        List2 = LoadManual(raw_input('Please enter a comma separated list for list 2\n\n'))
    else:
        List1 = LoadManual(raw_input('Please enter a comma separated list for list 1\n\n'))
        List2 = LoadManual(raw_input('Please enter a comma separated list for list 2\n\n'))

    if argDict['fullOrPartialOrToken'] == None:
        argDict['fullOrPartialOrToken'] = raw_input('\nWould you like to do a full, partial, token or all comparison?\n').lower()

    if argDict['ignoreCase'] == None:
        argDict['ignoreCase'] = raw_input('Would you like to ignore case? Yes/No\n').lower()

    # If there is a save location set the output option to save automatically
    if argDict['saveFileLocation'] != None:
        argDict['output'] = 'save'

    if argDict['output'] == None:
        argDict['output'] = raw_input('How would you like to output the results? Print to console or Save to file (Print or Save)\n').lower()

    if argDict['matchLimit'] == None:
        matchLimit = 0

    if argDict['ratioPercent'] == None:
        argDict['ratioPercent'] = int(raw_input("What percentage match? 0-100 (100 means exact match)\n\n"))

    # Reset match limit to only return results greater than 1 when the list is being compared to itself
    if List1 == List2:
        print('The lists are the same. Will return results where matches are greater than 1')
        argDict['matchLimit'] = 1

    if argDict['output'] == 'print':
        outputMethod = printResults
        argDict['saveFileLocation'] = None
    elif(argDict['output'] == 'save'):
        outputMethod = saveResults
        if argDict['saveFileLocation'] == None:
            argDict['saveFileLocation'] = raw_input('Please give the location of the csv file (including the name of the file) that you would like to save\n').replace('"', '')
    else:
        print "Did not recognize output command"

    matchList = getMatches(List1, List2, argDict['ignoreCase'], argDict['fullOrPartialOrToken'], argDict['ratioPercent'], argDict['saveFileLocation'], argDict['matchLimit'])

    if len(matchList) > 0:
        outputMethod(matchList, argDict['saveFileLocation'])


if __name__ == '__main__':
    parser= argparse.ArgumentParser()
    parser.add_argument('--loadType')
    parser.add_argument('--fullOrPartialOrToken')
    parser.add_argument('--ignoreCase')
    parser.add_argument('--output')
    parser.add_argument('--ratioPercent')
    parser.add_argument('--matchLimit')
    parser.add_argument('--saveFileLocation')
    parser.add_argument('--fileLocation_List1')
    parser.add_argument('--fileLocation_List2')

    args = parser.parse_args()


    argDict = {'loadType': args.loadType, 'fullOrPartialOrToken': args.fullOrPartialOrToken, 'ignoreCase': args.ignoreCase, 'output': args.output, 'ratioPercent': args.ratioPercent, 'matchLimit': args.matchLimit, 'saveFileLocation': args.saveFileLocation, 'fileLocation_List1': args.fileLocation_List1, 'fileLocation_List2': args.fileLocation_List2}
    main(argDict)
