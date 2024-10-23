'''
Utility library
    Author:        SCS
    date:          15/12/2022
    description:   Implements different utilities (logging, regex, generic parsing)
                   which might be adapted to the specific extension. See **CUSTOM BEGIN** ... **CUSTOM END** blocks.
    Exceptions:    NOT traced
    Log:
        24/01/2022: first release
        17/02/2022: parsing optimized
        31/03/2022: added extensions for logging
        22/04/2022: corrected parsing
        15/12/2022: generalized
        11/01/2023: debugging
        17/01/2023: added metrics
        17/02/2023: parsing optimization, added more useful functions
        
'''

import cast_upgrade_1_6_22 # @UnusedImport

import re
import sys
import uuid
import os
import subprocess
import csv
from datetime import datetime
from builtins import str

from tempfile import gettempdir
import logging
import cast.analysers.log
from cast.application import open_source_file


# ***********************************************************************************************************************************
# ***********************************************************************************************************************************
# GLOBAL CONSTANTS - This has to be adapted to the application
# ***********************************************************************************************************************************
# ***********************************************************************************************************************************

# **CUSTOM** BEGIN *********************************
# **************************************************
EXTENSION_VER = ""
EXTENSION_DATE = "16/09/2024"

# Language fingerprint for log messages
LANG_FINGERPRINT = "PYTHON"

# Plugin name
PLUGIN_NAME = "com.castsoftware.uc.python_extracwe"

# Language comment styles flags
LANG_HAS_MULTILINE_COMMENTS = False
LANG_HAS_INLINE_COMMENTS = False

# **CUSTOM** END ***********************************

# Debug flag at application level
EXTENSION_DEBUG = True
# Debug flag at analysis level
EXTENSION_ANA_DEBUG = True

# Verbose log mode flags
EXTENSION_ANA_VERBOSE = True
EXTENSION_VERBOSE = True

# ***********************************************************************************************************************************
# ***********************************************************************************************************************************
# FUNCTIONS
# ***********************************************************************************************************************************
# ***********************************************************************************************************************************

# ================================================================================================================
# ================================================================================================================
# DEBUGGING
# ================================================================================================================
# ================================================================================================================

# *** APPLICATION LEVEL LOGGING *************************************************
# *******************************************************************************

# Logs info, removing string ERROR from log line (application level)
def loggingInfo(msg):
    msgCorrect = "{0} : ".format(LANG_FINGERPRINT) + msg
    if "ERROR" in msg.upper(): msgCorrect = msg.replace("error",".BUG.").replace("Error", ".BUG.").replace("ERROR", ".BUG.")
    logging.info(msgCorrect)
    
# Logs info, removing string ERROR from log line (application level) - For verbose mode
def verboseLoggingInfo(msg):
    if EXTENSION_VERBOSE:
        msgCorrect = "{0} : ".format(LANG_FINGERPRINT) + msg
        if "ERROR" in msg.upper(): msgCorrect = msg.replace("error",".BUG.").replace("Error", ".BUG.").replace("ERROR", ".BUG.")
        logging.info(msgCorrect)

# Debug log (application level)
def debugloggingApp(msg): 
    msgCorrect = "{0} : ".format(LANG_FINGERPRINT) + msg   
    if EXTENSION_DEBUG:
        loggingInfo("{0} * {1} DEBUG".format(msgCorrect,LANG_FINGERPRINT))
        
# Verbose error log (application level)
def verboseErrorLog(msg, exc):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    msgCorrect = "{0} : ".format(LANG_FINGERPRINT) + msg
    logging.error("{0} - LINE {1} - {2}".format(msgCorrect, str(exc_traceback.tb_lineno), str(exc)))

def loggingError(msg):
    msgCorrect = "{0} : ".format(LANG_FINGERPRINT) + msg
    logging.error(msgCorrect)


# *** ANALYZER LEVEL LOGGING ****************************************************
# *******************************************************************************

# Logs info, removing string ERROR from log line (analysis level)
def loggingInfoAna(msg): 
    msgCorrect = msg
    if "ERROR" in msg.upper(): msgCorrect = msg.replace("error",".BUG.").replace("Error", ".BUG.").replace("ERROR", ".BUG.")
    cast.analysers.log.info(msgCorrect)

# Logs info, removing string ERROR from log line (analysis level) - For verbose mode
def verboseLoggingInfoAna(msg): 
    if EXTENSION_ANA_VERBOSE:
        msgCorrect = msg
        if "ERROR" in msg.upper(): msgCorrect = msg.replace("error",".BUG.").replace("Error", ".BUG.").replace("ERROR", ".BUG.")
        cast.analysers.log.info(msgCorrect)

# Logs warnings, removing string ERROR from log line (analysis level)
def loggingWarningAna(msg): 
    msgCorrect = msg
    if "ERROR" in msg.upper(): msgCorrect = msg.replace("error",".BUG.").replace("Error", ".BUG.").replace("ERROR", ".BUG.")
    cast.analysers.log.warning(msgCorrect)

# Debug log (analysis level)
def debugloggingAna(msg): 
    if EXTENSION_ANA_DEBUG:
        loggingInfoAna("{0} * {1} DEBUG".format(msg,LANG_FINGERPRINT))

# True if debug mode is on
def isInAnaDebugMode():
    if EXTENSION_ANA_DEBUG: return True
    return False


# ================================================================================================================
# ================================================================================================================
# BUFFER MANAGEMENT
# ================================================================================================================
# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Reads a file in a buffer, excluding comments (which are turned into dummy comment lines with the same length, 
# to neutralize code in comments)
# pFile  a file object
# delims (optional) : a list of string delimiters to use if also strings have to be purged
# OUT > The file buffer
def FileToBuffer(pfile,delims=None):
    fileBuffer = ""
    with open_source_file(pfile.get_path()) as f:            
        CommCheck = CommentMarker(LANG_PATTERN_COMMENTS,LANG_PATTERN_INLINE_COMMENTS)            
        for line in f:                                            
            # Comment Exclusion
            line = CommCheck.Purge(line)              
            if CommCheck.LineIsCommented(line):
                fileBuffer = fileBuffer + BlankCommentLine(line) + "\n"
            else:              
                # Create buffer
                fileBuffer = fileBuffer + line.rstrip('\n') + "\n"

    if not delims is None:
        buffOut = ""
        inString = False
        escaped = False
        currentDelim = ""
        for i in range(0,len(fileBuffer)):
            cx = fileBuffer[i]
            if i > 0:
                if fileBuffer[i-1] == '\\': escaped = True
            
            foundDelim = False
            for delim in delims:
                if cx == delim and currentDelim == delim and inString and not escaped:
                    currentDelim = ""
                    inString = False
                    foundDelim = True
                    break
                if cx == delim and not inString and not escaped:
                    currentDelim = delim
                    inString = True
                    foundDelim = True
                    break
            if foundDelim:
                buffOut += cx
            else:
                if inString: cx = " "
                buffOut += cx
            
        return buffOut
    else:
        return fileBuffer


# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Gets the line number of position pEnd, relative to the start offset pStart
#  buff     The string buffer
#  pStart   The start index for search 
#  pEnd     The end index of search
# OUT > The position
def GetLineNumber(buff, pStart, pEnd):
    if pStart > len(buff)-1 or pEnd > len(buff):
        return 0
    
    count = 1
    for i in range(pStart,pEnd):
        if buff[i] == '\n':
            count += 1  
    
    return count

# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Gets the absolute position in buffer of the line where pos is located
#  buff     The string buffer
#  pos      The reference position
# OUT > The position
def GetLineAbsolutePosition(buff,pos):
    if pos > len(buff):
        return 0
    
    lastPos = 0
    for i in range(0,pos):
        if buff[i] == '\n': lastPos = i
        
    if lastPos != 0: lastPos += 1     
    
    return lastPos

# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Gets the buffer block corresponding to bookmark coordinates (1-based, CAST standard)
# Returns the buffer content
#  buff                        The string buffer
#  bline,bcol,eline, ecol      The bookmark coordinates
# OUT > The a buffer block as array
def GetBufferFromBookmarkReferences(buff,bline,bcol,eline,ecol):
    out = ""
    endBuffer = len(buff)

    # Find start line and col (1-based)
    lineCount = 1
    startPos = 0
    for i in range(0,endBuffer):
        if lineCount == bline : 
            startPos = i
            break
        if buff[i] == '\n': lineCount += 1
    startPos += bcol
    if startPos > endBuffer : startPos = 0

    # Find end line and col (1-based)
    lineCount = 1
    endPos = 0
    for i in range(0,endBuffer):
        if lineCount == eline : 
            endPos = i
            break
        if buff[i] == '\n': lineCount += 1
    endPos += ecol
    if endPos > endBuffer : endPos = endBuffer

    return buff[startPos:endPos]

# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Gets the buffer block coordinates (start and end) corresponding to bookmark coordinates (1-based, CAST standard)
# Returns the buffer offset and lenght as array
#  buff                        The string buffer
#  bline,bcol,eline, ecol      The bookmark coordinates
# OUT > The coordinates as list
def GetOffsetAndLengthFromBookmark(buff,bline,bcol,eline,ecol):
    startPosition = 0
    bkLength = 0
    endBuffer = len(buff)

    # Find start line and col (1-based)
    lineCount = 1
    startPos = 0
    for i in range(0,endBuffer):
        if lineCount == bline : 
            startPos = i
            break
        if buff[i] == '\n': lineCount += 1
    startPos += bcol
    if startPos > endBuffer : startPos = 0

        # Find end line and col (1-based)
    lineCount = 1
    endPos = 0
    for i in range(0,endBuffer):
        if lineCount == eline : 
            endPos = i
            break
        if buff[i] == '\n': lineCount += 1
    endPos += ecol
    if endPos > endBuffer : endPos = endBuffer

    return [startPos,endPos-startPos+1]

# ================================================================================================================
# ================================================================================================================
# REGEX MANAGEMENT
# ================================================================================================================
# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Search regex in a begin - end block
#  buff            The string buffer
#  patBlockBegin   The pattern for begin block
#  patBodyBegin    The pattern for the body begin. If it is None, the pattern pat is searched everywhere between begin and end
#  patBlockEnd     The pattern for end block
#  pat             The pattern to search
# Begin/end blocks can be nested, in the code to be scanned. Each nesting level is returned as result.
#
#  Returns a list of RegexInBlockMarker object, with all occurrences in buffer. Each list element corresponds to one nesting level (nesting context),
#  with its begin and end regex references, and with the list of all regex found in the block
#
# OUT > A list of RegexInBlockMarker (all matches, begin match, end match)
def FindRegexInBlock(buff,patBlockBegin,patBodyBegin,patBlockEnd,pat):
    out = list()
    pats = list()
    
    pats.append((patBlockBegin,"OPEN"))
    pats.append((patBlockEnd,"CLOSE"))
    if not patBodyBegin is None: pats.append((patBodyBegin,"BODY"))
    pats.append((pat,"PAT"))
    toks = Tokenizer(pats)
    res = toks.generateTokens(buff)
    
    nesting = 0
    # dict of lists where 0: patterns found (as list), 1: start pattern, 2: end pattern, 3: flag to indicate that body marker is found
    nestDict = dict()
    for r in res:
        if r[3] == "OPEN": 
            nesting += 1
            nestDict[nesting] = [list(), SimpleRegexMatch(r[0],r[1],r[2]), None, False]
            if patBodyBegin is None: nestDict[nesting][3] = True
        if r[3] == "BODY" and nesting > 0:
            nestDict[nesting][3] = True
        if r[3] == "CLOSE": 
            if nesting > 0:
                nestDict[nesting][2] = SimpleRegexMatch(r[0],r[1],r[2])
                out.append(RegexInBlockMarker(nestDict[nesting][0], nestDict[nesting][1], nestDict[nesting][2]))
                del nestDict[nesting]
                nesting -= 1
            
        if r[3] == "PAT" and nesting > 0 and nestDict[nesting][3]:
            nestDict[nesting][0].append(SimpleRegexMatch(r[0],r[1],r[2]))

    return out


# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Search a begin - end block defined by regex
#  buff            The string buffer
#  patBlockBegin   The pattern for begin block
#  patBlockEnd     The pattern for end block
# Begin/end blocks can be nested, in the code to be scanned. Each nesting level is returned as result.
#
# Returns a list of BlockByRegexMarker object, with all occurrences in buffer. Each list element corresponds to one nesting level (nesting context),
# with its begin and end regex references, and with buffer content between begin and end
#
# OUT > A list of BlockByRegexMarker (content of the block, begin pattern, end pattern)
def FindBlockByRegex(buff,patBlockBegin,patBlockEnd):     
    out = list()
    pats = list()
    nestDict = dict()
    
    pats.append((patBlockBegin,"OPEN"))
    pats.append((patBlockEnd,"CLOSE"))
    t = Tokenizer(pats)
    res = t.generateTokens(buff)

    b_start = 0
    nesting = 0
    # dict of lists where 0: buffer content, 1: start pattern, 2: end pattern
    nestDict = dict()
    for r in res:
        oldnesting = nesting
        if r[3] == "OPEN": 
            nesting += 1
            nestDict[nesting] = ["", SimpleRegexMatch(r[0],r[1],r[2]) ,None]
            if nesting > 1:
                nestDict[nesting-1][0] += buff[b_start:r[1]]
            b_start = r[2] + 1

        if r[3] == "CLOSE": 
            if nesting > 0:
                nestDict[nesting][2] = SimpleRegexMatch(r[0],r[1],r[2])
                nestDict[nesting][0] += buff[b_start:r[1]]
                b_start = r[2] + 1
                out.append(BlockByRegexMarker(nestDict[nesting][0], nestDict[nesting][1], nestDict[nesting][2]))
                del nestDict[nesting]
                nesting -= 1
        
    return out



# ================================================================================================================
# ================================================================================================================
# GENERAL UTILITIES
# ================================================================================================================
# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Creates a temporary folder in %TEMP% and returns the full path.
def GetTemporaryFolder():
    tmpDir = os.path.join(gettempdir(), PLUGIN_NAME)
    if not os.path.exists(tmpDir):
        os.makedirs(tmpDir)  
    
    return tmpDir  

# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Cleanup temporary folder.
def CleanupTemporaryFolder():
    tmpDir = GetTemporaryFolder()
    
    for file_object in os.listdir(tmpDir):
        file_object_path = os.path.join(tmpDir, file_object)
        if os.path.isfile(file_object_path):
            os.remove(file_object_path)

# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Creates a dump dir
def create_dump_dir():
    df = os.path.join(GetTemporaryFolder(), "DUMP_" + str(uuid.uuid4()))
    if not os.path.exists(df):
        os.makedirs(df)
        
    return df

# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Returns True if the file has one of the extensions specified
def FileHasExtension(pFile, extensionList):
    for ext in extensionList:
        if pFile.get_path().lower().endswith(ext.lower()): return True
    return False

# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Check if a string is a number, returns True or false
def isNumber(str):
    if not re.match(r'^(\+|\-)?([0-9]+\.)?[0-9]+(e(\+|\-)?([0-9]+\.)?[0-9]+)?$',str.strip()) is None:
        return True
    else:
        return False
    
# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Check if a name is a standard instruction (requires the instruction list), returns True or false
def CheckIfIsInstruction(name, instrList):
    if name in instrList:
        return True
    else:
        return False
    
# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Replace a commented line with a blank line of the same length, returns the purged line
def BlankCommentLine(line):
    line = line.rstrip('\n')
    if len(line) == 0 : return ""
    if len(line) == 1 : return " "
    if len(line) == 2 : return "  "
    ret = LANG_COMMENTED_LINE_MARKER
    if len(line) >= 2:
        l = len(line)-2
        while l > 1:
            ret += "-"
            l -= 1
            
    return  ret 

# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Gets and returnsonly the useful part of a full name, that is gets rid of the filsesystem path part. 
# Useful for custom objects
def CleanFullName(fullName):
    arrParts = fullName.split("\\")
    l = len(arrParts)
    if l < 3:
        ret = fullName
    else:
        ret = "\\" + arrParts[l-2] + "\\" + arrParts[l-1]
        
    return ret

# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Creates a string of spaces and returns it
def Spaces(n):
    ret = ""
    if n == 1: return " "
    for i in range(1,n): ret += " "
    return ret

# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# Reads a CSV into a list of tuples
#  . fileName is the name of the file
#  . delim    is the CSV delimiter
#  . returnNames is a flag to indicate whether the first row should return names (False is default)
#
#  . returns a list of tuples
def read_csv_file(fileName, delim, returnNames=False):
    out = list()
    
    with open(fileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delim)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                if returnNames:
                    out.append(tuple(row))
            else:
                out.append(tuple(row))
            line_count += 1

    return out


# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# Write a CSV from lists
#  . fileName is the name of the file
#  . delimiter is the CSV delimiter
#  . data are the rows as a list of tuples
#  . header is the list defining the header (default None)
#
#  . returns the number of rows written
def write_csv_file(fileName, delimiter, data, header=None):
    lines = 0
    
    with open(fileName, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f, delimiter)
        if not header is None:
            writer.writerow(header)
            lines += 1
        for r in data:
            writer.writerow(list(r))
            lines += 1
    
    return lines


# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# Explores a root and returns a list of fullpaths for all subfolders which
# contain specific file exrtensions
#  . root is the root folder where to start exploration
#  . exts is the list of extensions to search
def walk_folder_tree(root, exts):
    dirlist = list()
    for dirpath, dirs, files in os.walk(root): 
        for d in dirs:
            fp = os.path.join(dirpath, d)
            if fp not in dirlist:
                folderIsOK = False
                for fname in os.listdir(fp):
                    for ex in exts: 
                        if fname.endswith("."+ ex ): 
                            folderIsOK = True
                            break
                    if folderIsOK: break
                if folderIsOK: dirlist.append(fp)
    
    return dirlist

# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# Runs an external command
#  . args is the list of command arguments (the first is the command itself)
def run_exec(args):
    subprocess.call(args, universal_newlines = True)

# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# Returns a d-m-y-H-M-S formatted timestamp
def get_timestamp():
    date_time = datetime.fromtimestamp(datetime.timestamp(datetime.now()))
    return  date_time.strftime("%d-%m-%Y-%H-%M-%S")


# ***********************************************************************************************************************************
# ***********************************************************************************************************************************
# CLASSES
# ***********************************************************************************************************************************
# ***********************************************************************************************************************************

# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Used to track complex block patterns (begin, end and internal matches):
# matches : regex pattern results list for patterns in block (each item has group(n), start() and end())
# matches_begin : regex pattern result for block start (has group(n), start() and end())
# matches_end : regex pattern result for block end (has group(n), start() and end())
#
# Uses SimpleRegexMatch to store regex references/matches
#
class RegexInBlockMarker:
    def __init__(self,m,mb,me):
        self.matches = m      
        self.matches_begin = mb
        self.matches_end = me
    
    # Returns all matches found in block as list of SimpleRegexMatch
    def get_matches(self): return self.matches   
    # Returns the start marker as SimpleRegexMatch
    def get_start_mark(self): return self.matches_begin
    # Returns the end marker as SimpleRegexMatch
    def get_end_mark(self): return self.matches_end
    # Returns block start position in buffer
    def start(self): return self.matches_begin.start()
    # Returns block end position in buffer
    def end(self): return self.matches_end.end()


# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Used to track block patterns (begin, end and inner text, plus line position)
# block_content : the content within block begin/end
# block_begin : regex pattern result for block start (has group(n), start() and end())
# block_end : regex pattern result for block end (has group(n), start() and end())
#
# Uses SimpleRegexMatch to store regex references/matches
#
class BlockByRegexMarker:
    def __init__(self,bk,bb,be):
        self.block_content = bk           
        self.matches_begin = bb
        self.matches_end = be
    
    # Returns the start marker as SimpleRegexMatch
    def get_start_mark(self): return self.matches_begin
    # Returns the end marker as SimpleRegexMatch
    def get_end_mark(self): return self.matches_end
    # Returns the buffer content between start and end
    def get_content(self): return self.block_content
    # Returns block start position in buffer
    def start(self): return self.matches_begin.start()
    # Returns block end position in buffer
    def end(self): return self.matches_end.end() 


# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Used to store basic regex info:
# groups: the match groups (0 included) > group(n)
# rx_start: the regex start index > start()
# rx_end: the regex ind index > end()
#
class SimpleRegexMatch:
    def __init__(self,grps,start,end):
        self.groups = grps
        self.rx_start = start
        self.rx_end = end

    # Returns all match groups found (regex standard) in pattern
    def group(self,n): return self.groups[n]
    # Returns pattern start position
    def start(self): return self.rx_start
    # Returns pattern end position
    def end(self): return self.rx_end
    

# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Used to check if a line is within comment marker
#
class CommentMarker:
        
    def __init__(self, pComment, pInlineComment):
        self.isInSingleLineComment = False
        self.isInMultiLineComment = False
        self.isInLastMultiline = False

        self.patComment = pComment
        self.patInlineComment = pInlineComment

    # ----------------------------------------------------------
    # Cleanup all text included in inline comments, replacing it with spaces
    # - Parameters:
    # line    The line of text to purge
    def Purge(self,line):
        if LANG_HAS_INLINE_COMMENTS:
            resultCom = re.finditer(self.patInlineComment, line)

            if not resultCom is None:
                for c in resultCom:
                    pat = c.group(0)
                    line = line.replace(pat,Spaces(len(c.group(0))))
        
        return line

    # ----------------------------------------------------------
    # Returns True if the line is commented
    # - Parameters:
    # line    The line of text to check
    def LineIsCommented(self,line):
        resultCom = re.finditer(self.patComment, line)
        
        if not resultCom is None:
            for c in resultCom:
                if c.group(1):
                    self.isInSingleLineComment = True
                if LANG_HAS_MULTILINE_COMMENTS:
                    if c.group(2):
                        self.isInMultiLineComment = True
                    if c.group(3):
                        self.isInLastMultiline = True
                    
        if LANG_HAS_MULTILINE_COMMENTS:
            if self.isInMultiLineComment:
                if self.isInLastMultiline:
                    self.isInMultiLineComment = False 
                    self.isInLastMultiline = False
                return True
        if self.isInSingleLineComment:
            self.isInSingleLineComment = False
            return True
        
        return False
    
    
# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# Analyzes a buffer and returns a list of ordered tokens, based on regexes.
# The list of token definitions is made of tuples as follows:
#  (regex, name of token type)
# Each token is a tuple like this:
#  (the list of all match group found, start position in buffer, end position in buffer, name of token)
#
class Tokenizer:
    
    # ----------------------------------------------------------------
    # Construct
    #  myListOfPattern: a list of token pattern definitions
    def __init__(self, myListOfPattern):
        # The list of regex patterns that define the object to search in buffer
        # Each pattern is a tuple with the regex and a name (regex,name)
        self.listOfPatterns = list()
        if not myListOfPattern is None:
            for x in myListOfPattern: self.listOfPatterns.append(x)
            
        # The internal list of tokens, each token is a tuple
        # (the list of all group matches found, start position in buffer, end position in buffer, name of token)
        self.tokens = list()
    
    # ----------------------------------------------------------------
    # Returns the list of tokens found in the buffer
    #  buffer: the buffer to analyze
    def generateTokens(self, buffer):
        self.tokens = list()
        
        if not self.listOfPatterns is None:
            # 1. Scanning buffer for all patterns
            for p in self.listOfPatterns:
                results = re.finditer(p[0], buffer)
                
                if not results is None:
                    for t in results:
                        lt = list()
                        lt.append(t.group(0))
                        for i in t.groups(): lt.append(i)
                        tokTuple = (lt, t.start(), t.end(), p[1])
                        self.tokens.append(tokTuple)
                        
            # 2. Bubble sorting the tokens, based on start position
            for i in range(0,len(self.tokens)-1):
                for j in range(len(self.tokens)-1):
                    if(self.tokens[j][1] > self.tokens[j+1][1]):
                        self.tokens[j],self.tokens[j+1] = self.tokens[j+1], self.tokens[j]
            
        
        return  self.tokens

