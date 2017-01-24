from fuzzywuzzy import fuzz
import sys
import csv
import os

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
def printResults(item, matchList, fileLocation):
    if len(matchList) > 0:
        print('\n' + 'List for ' + item)
        for i in matchList:
            print str(i[0]) + " | " + str(i[1]) + " | " +    str(i[2]) + " | " + str(i[3]) + " | " + str(i[4])
        raw_input("Press Enter go to next")

def saveResults(item, matchList, fileLocation):
    if os.path.exists(fileLocation):
        try:
            os.remove(fileLocation)
        except Exception as e:
            print('\nFile' + fileLocation + ' in use, please close and hit "Enter"\n')
            raw_input()
            saveResults(item, matchList, fileLocation)
    with open(fileLocation, 'wb') as csvFile:
        writer = csv.writer(csvFile)
        if len(matchList) > 0:
            writer.writerow(['Item', 'Matched Item', 'Full Match Percent', 'Partial Match Percent', 'Token Match Percent'])
            for i in matchList:
                writer.writerow([i[0], i[1], i[2], i[3], i[4]])

def getMatches(item, ignoreCase, fullOrPartialOrToken, ratioPercent, fileLocation):
    matchList = []
    for item in List1:
        tempMatchList = []
        word1 = str(item)
        sys.stdout.write('.')
        for word in List2:
            rFull = 0
            rPartial = 0
            rToken = 0
            word2 = str(word)
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
            if rFull > ratioPercent or rPartial >  ratioPercent or rToken > ratioPercent:
                tempMatchList.append([word1, word2, rFull, rPartial, rToken])
        # Compare length of list to match limit to account for when comparing a list to itself
        if len(tempMatchList) > matchLimit:
            matchList.extend(tempMatchList)
    if len(matchList) > 0:
        outputMethod(item, matchList, fileLocation)

def main(**kwargs):
    loadType = 'csv'
    fullOrPartialOrToken = 'all'
    ignoreCase = True
    output = 'print'
    ratioPercent = 80
    matchLimit = 0
    fileLocation = 'null'

    if len(**kwargs) > 0:
        #Put code for passing args here
        loadType = kwargs['loadType']
        print loadType
    else:
        loadType = raw_input('Would you like to load from CSV or manual input? (Input "CSV" or "Manual")\n\n').lower()
        if loadType == "csv":
            List1 = LoadCSV(raw_input('Please enter the absolute file path of the 1st file you would like to load\n'))
            List2 = LoadCSV(raw_input('Please enter the absolute file path of the 2nd file you would like to load\n'))
        else:
            List1 = LoadManual(raw_input('Please enter a comma separated list for list 1\n\n'))
            List2 = LoadManual(raw_input('Please enter a comma separated list for list 2\n\n'))


        fullOrPartialOrToken = raw_input('\nWould you like to do a full, partial, token or all comparison?\n').lower()

        ignoreCase = raw_input('Would you like to ignore case? Yes/No\n').lower()

        output = raw_input('How would you like to output the results? Print to console or Save to file (Print or Save)\n').lower()

        # Reset match limit to only return results greater than 1 when the list is being compared to itself
        matchLimit = 0
        if List1 == List2:
            print('The lists are the same. Will return results where matches are greater than 1')
            matchLimit = 1

        if output == 'print':
            outputMethod = printResults
            fileLocation = 'null'
        elif(output == 'save'):
            outputMethod = saveResults
            fileLocation = raw_input('Please give the location of the csv file (including the name of the file) that you would like to save\n').replace('"', '')
        else:
            print "Did not recognize output command"

        ratioPercent = int(raw_input("What percentage match? 0-100 (100 means exact match)"))

main(sys.argv)
