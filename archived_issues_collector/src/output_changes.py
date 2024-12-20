# -*- coding: utf-8 -*-
import os
import re
import sys
import logging

defaultInputPath = "./"
defaultOutputPath = "./out"

invalidRowOffset = 3
originalFileParsed = 0

logging.basicConfig(
           format='%(asctime)s [%(levelname)s] (%(funcName)s) %(message)s'
           )
logger = logging.getLogger()

def init_logger():
    global logger
    logging.basicConfig(filename="out/debug.log",
                        format='%(asctime)s [%(levelname)s] (%(funcName)s) %(message)s',
                        filemode='w')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

def dbgdummy(*values: object):
    pass

# dbgprint = print
dbgprint = dbgdummy

class Record:
    def __init__(self):
        self.Type = ''
        self.Description = ''
        self.IssueType = ''#issue type description, bug adjustment and so on
        self.Issue = ''
        self.StartVersion = ''
        self.EndVersion = ''
    pass

RecordList = [Record()]

def get_short_name(filename):
    (filepath, tempfilename) = os.path.split(filename)
    (shortname, extention) = os.path.splitext(tempfilename)
    return shortname, extention


def ParseLine(lineStr: str):
    record = Record()
    sections = lineStr.split('|')
    logger.debug('sections:%s', sections)

    def parseDesc(rcontext: str):
        print(rcontext)
        lbracketPos = rcontext.find('(')
        if(lbracketPos == -1): 
            logger.error("left bracket not found")

        rbracketPos = rcontext.find(')')
        if(rbracketPos == -1): 
            logger.error("right bracket not found")

        record.Type = rcontext[lbracketPos + 1 : rbracketPos]
        
        mcontext = rcontext[rbracketPos + 1 :]
        #parse issue number
        issueContent = ''
        recLBracketPos = mcontext.find('[')
        if(recLBracketPos != -1):
            recRBracketPos = mcontext.find(']')
            issueContent = mcontext[recLBracketPos +1 : recRBracketPos]
            record.Description = mcontext[0 : recLBracketPos]
        else:
            issueContent = mcontext
        nsPos = issueContent.find('#')
        if(nsPos != -1):
            record.IssueType = issueContent[:nsPos]
            record.Issue = issueContent[nsPos+1:]
            logger.debug('issue number:' + record.Issue)
            if(recLBracketPos == -1):
                record.Description = issueContent[:nsPos]
        else:
            record.Description = mcontext
    
    parseDesc(sections[2].strip())
    record.StartVersion = sections[3].strip()
    record.EndVersion = sections[4].strip()

    logger.debug("#%s record.StartVersion:%s", record.Issue, record.StartVersion)

    if record.StartVersion.isspace():
        logger.debug("isspace check")
        record.StartVersion = ''

    RecordList.append(record)
    print("==ParseLine finished==")
    return

def escapeSuffix(input) -> str:
    debug = True
    #print(input[-1])
    #print(input[-2])
    #print('9')
    dbgprint(input)
    expandCount = 0
    resetSuffx = False
    inputLen = len(input)
    if input[-1] > '9':
        resetSuffx = True
        expandCount = 1
    elif inputLen >=2 and input[-2] > '9':
        resetSuffx = True
    else:
        expandCount = 2
    for idx in range(expandCount):
        input = input + '0'
    if resetSuffx:
        input = input.replace('P',
                            '0').replace('A',
                            '1').replace('a',
                            '1').replace('B',
                            '2').replace('b',
                            '2').replace('C',
                            '3').replace('D',
                            '4').replace('E',
                            '5').replace('F',
                            '6').replace('G', 
                            '7').replace('H',
                            '8')
    logger.debug(input)
    return input

def getPrefixNum(input):
    num = {'Y' : '-1', 
            'E':'0', 
            'F': '1', 
            'G' : '2',
            'H' : '3'
            }
    return num[input]

def strToHex(strIn):
    num = {
        '0':0,
        '1':1,
        '2':2,
        '3':3,
        '4':4,
        '5':5,
        '6':6,
        '7':7,
        '8':8,
        '9':9,
        'a':10,
        'b':11,
    }
    ret = 0
    round = len(strIn) - 1
    for ch in strIn:
        ret += (num[ch] << (round * 4))
        round -= 1
    return ret


def versionCodeToValue(input):
    if '.' in input:
        verParts = input.split('.')
        multiRound = len(verParts) - 1
        ret = 0
        for part in verParts:
            ret += strToHex(part) << 10 * multiRound
            multiRound -= 1
        return ret
    raise ValueError

def versionCodeCombinedStr(input: str) -> str:
    if not '.' in input:
        return escapeSuffix(input)
    verParts = input.split('.')
    # for part in verParts:
    #     ret += escapeSuffix(part)
    lastAdjustedPart = verParts[-1]
    # release version
    if len(lastAdjustedPart) == 3:
        lastAdjustedPart += 'zz'
    elif len(lastAdjustedPart) == 4:
        lastAdjustedPart += '00'
    # alpha/beta version
    elif len(lastAdjustedPart) > 3:
        lastPart = lastAdjustedPart
        if lastPart[-2] >= 'a':
            lastAdjustedPart = lastPart[:-1] + '0' + lastPart[-1]

    ret = verParts[0] + verParts[1] + lastAdjustedPart
    logger.debug("input:%s, ret:%s", input, ret)
    return ret

class VersionCompareResult:
    CouldNotDetermine = -1
    BeforeStart = 0
    RightWithinRange = 1
    AfterEnd = 2

def isVersionInRange(
    issueNum,
    input,
    startRange,
    endRange,
    emptyDefault=VersionCompareResult.BeforeStart) -> VersionCompareResult:
    if len(input) == 0:
        logger.debug("#%s found empty input", issueNum)
        return emptyDefault
    result = VersionCompareResult.CouldNotDetermine
    if '.' in input or '.' in startRange or '.' in endRange:
        try:
            curVerVal = versionCodeCombinedStr(input)
            startVerVal = versionCodeCombinedStr(startRange)
            endVerVal = versionCodeCombinedStr(endRange)
            logger.debug('#%s curVerVal value = %s', issueNum, curVerVal)
            logger.debug('#%s startVerVal value = %s', issueNum, startVerVal)
            logger.debug('#%s endVerVal value = %s', issueNum, endVerVal)
            if startVerVal < curVerVal and curVerVal <= endVerVal:
                result = VersionCompareResult.RightWithinRange
            elif curVerVal <= startVerVal:
                result = VersionCompareResult.BeforeStart
            elif curVerVal > endVerVal:
                result = VersionCompareResult.AfterEnd
        except:
            pass
        logger.debug('compare ret = %s', result)
        return result

    #compare prefix first, e.g. G > F
    #if input[0] < startRange[0] or input[0] > endRange[0]:
    #    return False
    #if input[0] > startRange[0]:
    #    return True
    if('-1' in getPrefixNum(input[0])):
        return VersionCompareResult.RightWithinRange

    #same prefix, compare content
    inputAdjust = escapeSuffix(''.join(getPrefixNum(input[0]) + input[1:]))
    startRangeAdjust = escapeSuffix(''.join(getPrefixNum(startRange[0]) + startRange[1:]))
    endRangeAdjust = escapeSuffix(''.join(getPrefixNum(endRange[0]) + endRange[1:]))

    if int(startRangeAdjust) < int(inputAdjust) and int(inputAdjust) <= int(endRangeAdjust):
        result = VersionCompareResult.RightWithinRange
    logger.debug('startRangeAdjust value = ' + str(int(startRangeAdjust)))
    logger.debug('inputAdjust value = ' + str(int(inputAdjust)))
    logger.debug('endRangeAdjust value = ' + str(int(endRangeAdjust)))
    logger.debug('result = ' + str(result))
    return result


def OutputRecords(filename, type, startVersion='', endVersion=''):
    print("==trying to output==")
    (shortname, extention) = get_short_name(filename)
    print("== file name = " + shortname)
    suffix = "_output"
    if(type != ''):
        suffix = '_' + type

    checkVersion = False
    if startVersion == '':
        startVersion = '0000'
    elif endVersion == '':
        endVersion = '99999999'
    else:
        checkVersion = True

    with open(defaultOutputPath + '/' + shortname + suffix  + extention, "w+", encoding="utf-8") as outputFile:
        sequenceIdx = 0
        for record in RecordList :
            if(type != '' and type != record.Type):
                continue
            if checkVersion:
                #record starts and ends within the range selected , the record is ignored
                print(record.Description)
                # check if solved in wanted range, if not , abort
                endPointCmp = isVersionInRange(record.Issue, record.EndVersion, startVersion, endVersion)
                if endPointCmp != VersionCompareResult.RightWithinRange:
                    logger.debug("issue #%s resolved before start time", record.Issue)
                    continue
                # check if introduced before wanted range, or after, if not abort
                startPointCmp = isVersionInRange(record.Issue, record.StartVersion, startVersion, endVersion, False)
                if startPointCmp != VersionCompareResult.BeforeStart:
                    logger.debug("issue #%s resolved happens start time", record.Issue)
                    continue

            sequenceIdx += 1
            outputFile.write('1. [' + str(record.Type) + '(' + record.IssueType + '#' + str(record.Issue) + ')]\t' + str(record.Description) + '\n')
    print("output finished")

def HandleFile(filename):
    print("opening file" + filename)
    RecordList.clear()
    with open(filename, "r", encoding="utf-8") as inputFile :
        lineCounter = 0
        for line in inputFile :
            #first two lines should be skiped
            if(lineCounter >= invalidRowOffset and lineCounter != 0 + invalidRowOffset and lineCounter != 1 + invalidRowOffset):
                ParseLine(line)
            lineCounter += 1
    originalFileParsed = 1
    OutputRecords(filename, '')
    return

def QueryRecord(keyword, filename, startVersion='', endVersion=''):
    if(originalFileParsed == 0):
        print("original file was not parsed, now parsing")
        HandleFile(filename)
    if(keyword == ''):
        print("keyword is null, output all records")
    OutputRecords(filename, keyword, startVersion, endVersion)
    pass

def getCommands():
    hasCommands = False
    path = ''
    command = ''
    startVersion = ''
    endVersion = ''
    argCount = len(sys.argv)
    if(argCount > 1):
        for idx in range(1, argCount, 2):
            arg = sys.argv[idx]
            nextArg = sys.argv[idx+1]
            if '-i'in arg:
                path = nextArg
                hasCommands = True
            elif '-c'in arg:
                command = nextArg
                hasCommands = True
            elif '-s' in arg:
                startVersion = nextArg
                hasCommands = True
            elif '-e' in arg:
                endVersion = nextArg
                hasCommands = True
    if endVersion == '':
        endVersion = startVersion
    return hasCommands, path, command, startVersion, endVersion


def handleCommands(hasCommands, path, command, startVersion, endVersion):
    if not hasCommands:
        return
    if(path == ''):
        path = defaultInputPath + "/修改归档.md"
    HandleFile(path)
    QueryRecord(command, path, startVersion, endVersion)


def start():
    (hasCommands, path, command, startVersion, endVersion) = getCommands()
    if not os.path.exists(defaultInputPath):
        os.mkdir(defaultInputPath)
    if not os.path.exists(defaultOutputPath):
        os.mkdir(defaultOutputPath)
    handleCommands(hasCommands, path, command, startVersion, endVersion)
    if(hasCommands):
        return
    path = input(
    "input path or press 'enter' it will use current path and default name\n")
    while(True):
        if(path == ''):
            path = defaultInputPath + "/修改归档.md"
        command = input(('choose what you want to do\n'
                        '[1] reformat and out put. [2] reset file name. [3] query specific type records. [0] quit\n'))
        if command == '1':
            HandleFile(path)
            continue
        if command == '2':
            path = input(
            "input path or press 'enter' it will use current path and default name\n")
            continue
        if command == '3':
            keyword = input(
            "input keyword to query specific records\n")
            QueryRecord(keyword, path)
            continue
        if command == '0':
            break
        print('input error')
        continue
        
if __name__ == '__main__':
    init_logger()
    start()