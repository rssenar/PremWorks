
#!/usr/bin/env python3.4.3
# ---------------------- #
import csv, os, sys, glob, re, collections, datetime, subprocess, Constants
from dateutil.parser import *
from geopy.distance import vincenty
from nameparser import HumanName
from tqdm import tqdm

# ---------------------- #
os.chdir('../../../../Desktop/')
CSVFile = glob.glob('*.csv')
recpath = '../Dropbox/HUB/Projects/PyToolkit/Resources'

# ---------------------- #
DropFile = os.path.join(recpath,'_DropFile.csv')
GenSuppressionFile = os.path.join(recpath,'_GeneralSuppression.csv')
GenSuppressionFileNames = os.path.join(recpath,'_GeneralSuppressionNames.csv')
MonthlySuppressionFile = os.path.join(recpath,'_MonthlySuppression.csv')
ZipCoordFile = os.path.join(recpath,'USZIPCoordinates.csv')
SCF3DigitFile = os.path.join(recpath,'SCFFacilites.csv')
DDUFile = os.path.join(recpath,'DDUFacilites.csv')
Entries = set()
EntriesNames = set()

# ---------------------- #
print('=======================================')
print('            NORMALIZING FILE           ')
print('=======================================')
print()
# Select processing Mode
SuppSelect = str.upper(input('Select Mode............ (B)asic    | (S)tandard: '))
while SuppSelect != 'S' and SuppSelect != 'B':
  SuppSelect = str.upper(input('ERROR! Enter Valid Selection... : '))
# Select Source Mode
SourceSelect = str.upper(input('Select Source.......... (D)atabase | (P)urchase: '))
while SourceSelect != 'D' and SourceSelect != 'P':
  SourceSelect = str.upper(input('ERROR! Enter Valid Selection... : '))
# Generate Output Files
OutputFileSelect = str.upper(input('Generate Output Files..    (Y)es   |    (N)o   : '))
while OutputFileSelect != 'Y' and OutputFileSelect != 'N':
  OutputFileSelect = str.upper(input('ERROR! Enter Valid Selection... : '))

if SuppSelect == 'B':
  print('=======================================')
  print('             B  A  S  I  C             ')
  print('=======================================')
else:
  SuppSelect = 'S'
  print('=======================================')
  print('         S  T  A  N  D  A  R  D        ')
  print('=======================================')

# ---------------------- #
# Select Input File from Desktopbr
for file in CSVFile:
  IPFName = file.strip('.csv') # Extract filename only w/o ext.
  InputFile = file # Filename with ext.

# ---------------------- #
# Import DoNotMailSet for Constants.py for the purposes of de-duping
if SuppSelect != 'S':
  Constants.DoNotMailSet = set()
  print('.............. Mail DNQ File Not Loaded')

# ---------------------- #
# Import DropFile.csv file
try:
  DropDict = {}
  with open(DropFile,'rU') as DropFile:
    DropRec = csv.reader(DropFile)
    next(DropFile)
    for line in DropRec:
      DropDict[line[0]] = line[1]
except:
  print('..... ERROR: Unable to Load Drop Dictionary File')

# ---------------------- #
# Import GeneralSuppression.csv file
if SuppSelect == 'S':
  try:
    with open(GenSuppressionFile,'rU') as GenSuppressionFile:
      GenSuppression = csv.reader(GenSuppressionFile)
      next(GenSuppressionFile)
      for line in GenSuppression:
        Entries.add((str.title(line[2]),str.title(line[5])))
  except:
    print('..... ERROR: Unable to Load GENERAL Suppression File')
else:
  print('... General Suppression File Not Loaded')

# ---------------------- #
# Import GeneralSuppressionNames.csv file
if SuppSelect == 'S':
  try:
    with open(GenSuppressionFileNames,'rU') as GenSuppressionFileNames:
      GenSuppressionNames = csv.reader(GenSuppressionFileNames)
      next(GenSuppressionFileNames)
      for line in GenSuppressionNames:
        EntriesNames.add((str.title(line[0]),str.title(line[1])))
  except:
    print('..... ERROR: Unable to Load GENERAL Suppression File Names')
else:
  print('... General Suppression File Names Not Loaded')
# ---------------------- #
# Import MonthlySuppression.csv file
if SuppSelect == 'S':
  try:
    with open(MonthlySuppressionFile,'rU') as MonthlySuppressionFile:
      MonthlySuppression = csv.reader(MonthlySuppressionFile)
      next(MonthlySuppressionFile)
      for line in MonthlySuppression:
        Entries.add((str.title(line[2]),str.title(line[5])))
  except:
    print('..... ERROR: Unable to Load Montly Suppression File')
else:
  print('... Monthly Suppression File Not Loaded')

# ---------------------- #
# Import USZIPCoordinates.csv file
try:
  ZipCoordinateDict = {}
  with open(ZipCoordFile,'rU') as ZipCoord:
    ZipCoordinate = csv.reader(ZipCoord)
    for line in ZipCoordinate:
      ZipCoordinateDict[line[0]] = (line[1], line[2])
except:
  print('..... ERROR: Unable to Load Zip Dictionary File')

# ---------------------- #
# Import SCFFacilites.csv file
try:
  SCF3DigitDict = {}
  with open(SCF3DigitFile,'rU') as SCF3DigitFile:
    SCF3Digit = csv.reader(SCF3DigitFile)
    for line in SCF3Digit:
      SCF3DigitDict[line[0]] = (line[1])
except:
  print('..... ERROR: Unable to Load SCF 3-Digit Dictionary File')

# ---------------------- #
# Import DDUFacilites.csv file
try:
  DDUDict = {}
  with open(DDUFile,'rU') as DDUFile:
    DDU = csv.reader(DDUFile)
    for line in DDU:
      DDUDict[line[0]] = (line[1])
except:
  print('..... ERROR: Unable to Load DDU Dictionary File')

# ---------------------- #
# Print captured Input file
print('File Name ........................... : {}'.format(InputFile))
CentralZip = input('Enter Central Zip Code .............. : ').strip()
while str(CentralZip) not in ZipCoordinateDict:
  CentralZip = input('ERROR: Enter Zip Codes............... : ').strip()

# Capture Input (Max Radius)
if SuppSelect == 'S':
  try:
    MaxRadius = int(input('Enter MAX Radius ................[50] : ').strip())
  except:
    MaxRadius = 50
else:
  MaxRadius = 5000

# Capture Input (Max Vehicle Year)
if SuppSelect == 'S':
  try:
    MaxYear = int(input('Enter MAX Vehicle Year ........[2015] : ').strip())
  except:
    MaxYear = 2015
else:
  MaxYear = 2050

# Capture Input (Min Vehicle Year)
if SuppSelect == 'S':
  try:
    MinYear = int(input('Enter MIN Vehicle Year ........[1995] : ').strip())
  except:
    MinYear = 1995
else:
  MinYear = 1

# Capture Input (Max DelDate Year)
if SuppSelect == 'S':
  try:
    MaxSaleYear = int(input('Enter MAX DelDate Year ........[2014] : ').strip())
  except:
    MaxSaleYear = 2014
else:
  MaxSaleYear = 2050

# Capture Input (Min DelDate Year)
if SuppSelect == 'S':
  try:
    MinSaleYear = int(input('Enter MIN DelDate Year ........[2006] : ').strip())
  except:
    MinSaleYear = 2006
else:
  MinSaleYear = 1

# Capture Suppress State List
if SuppSelect == 'S':
  STATEList = input('Enter Selection List .........[State] : ')
  if STATEList != '':
    STATEList = sorted(Constants.ConvertStringToList(STATEList))
    print('..STATEList : {}'.format(STATEList))
  else:
    STATEList = []
else:
  STATEList = []

# Capture Suppress SCF List
if SuppSelect == 'S':
  SCFList = input('Enter Selection List ........[3Digit] : ')
  if SCFList != '':
    SCFList = sorted(Constants.ConvertStringToList(SCFList))
    print('....SCFList : {}'.format(SCFList))
  else:
    SCFList = []
else:
  SCFList = []

# Capture Suppress City List
if SuppSelect == 'S':
  CITYList = input('Enter Suppression List ........[City] : ')
  if CITYList != '':
    CITYList = sorted(Constants.ConvertStringToList(CITYList))
    print('...CITYList : {}'.format(CITYList))
  else:
    CITYList = []
else:
  CITYList = []

# Set TOPPercentage
if SuppSelect == 'S':
  TOPPercentage = input('Set Top % .......................[3%] : ').strip()
  try:
    TOPPercentage = int(TOPPercentage)
  except:
    TOPPercentage = 3
else:
  TOPPercentage = 0

# Import Local Suppression File for the purposes of de-duping
SuppressionFileName = input('Enter Suppression File Name ......... : ').strip()
SuppressionFile = '{}.csv'.format(SuppressionFileName)
if SuppressionFileName != '':
  try:
    with open(SuppressionFile,'rU') as SuppressionFile:
      Suppression = csv.reader(SuppressionFile)
      next(SuppressionFile)
      for line in Suppression:
        Entries.add((str.title(line[2]),str.title(line[5])))
      print('\n{}.csv File Loaded\n'.format(SuppressionFileName))
  except:
    print('ERROR: Cannot load local suppression file\n')
else:
  print('     No Suppression File Selected     ')

# Set Constants.Vendor
if SuppSelect == 'S':
  VendorSelect = str.upper(input(
    '....... (S)hopper | (P)latinum ....... '
    ).strip())
else:
  VendorSelect = ''
print()
input('       PRESS [ENTER] TO PROCEED        ')
print()

# ---------------------- #
# Compare File Header row to HeaderRowMain to determin if re-mapping is required
ExtractCSVHeader = subprocess.check_output(['head','-n','1',InputFile])
ExtractCSVHeader = ExtractCSVHeader.decode("utf-8").split(',')
ExtractCSVHeader = [x.replace("\r\n","") for x in ExtractCSVHeader]
if ExtractCSVHeader == Constants.HeaderRowMain:
  HRSelect = 'N'
else:
  HRSelect = 'Y'

# ---------------------- #
# Function to Re-Map header rows
def ReMapFunc():
  print('------------- RE-MAPPING -------------')
  global Selection
  Selection = '>>> Re-Mapped <<<.csv'
  with open(InputFile,'rU') as InputFileReMap,\
  open('>>> Re-Mapped <<<.csv','at') as ReMappedOutputFile:
    Input = csv.reader(InputFileReMap)
    Output = csv.writer(ReMappedOutputFile)
    Output.writerow(Constants.HeaderRowMain)
    FirstLine = True
    for line in tqdm(Input):
      if FirstLine:
        for OrigHRIndex in range(0,len(line)):
          Constants.MatchHeaderFields(line[OrigHRIndex], OrigHRIndex)
        FirstLine = False
      else:
        newline = []
        for NewHRIndex in range(0,len(Constants.HeaderRowMain)):
          if NewHRIndex in Constants.HeaderReMapDict:
            newline.append(eval(Constants.HeaderReMapDict[NewHRIndex]))
          else:
            newline.append('')
        Output.writerow(newline)

# ---------------------- #
# Function to normalize file
def NormalizeFunc():
  print('------------- NORMALIZING ------------')
  global CentralZip
  global CentralZipSCFFacilityReport
  global CityDictCounter
  global CleanOutput
  global CleanOutputDatabase
  global CleanOutputPhones
  global CleanOutputPurchase
  global DatabaseCounter
  global Dupes
  global DupesCounter
  global MakeDictCounter
  global MaxSaleYear
  global MDNQ
  global MDNQCounter
  global RadiusDictCounter
  global SCF3DFacilityCounter
  global DDUFacilityCounter
  global SCFDictCounter
  global SeqNumDatabase
  global SeqNumPurchase
  global StateDictCounter
  global DropDictCounter
  global SoldYearCounter
  global TOPPercentage
  global YearDictCounter
  global OutputDroplist
  global OutputDictOpenFiles
  global TOTALMailCounter
  with open(Selection, 'rU') as InputFile,\
  open('{}_UpdatedOutputMAIN.csv'.format(IPFName), 'at') as CleanOutput,\
  open('>>> Dupes <<<.csv', 'at') as Dupes,\
  open('>>> M-DNQ <<<.csv', 'at') as MDNQ,\
  open('{}_PHONES.csv'.format(IPFName), 'at') as CleanOutputPhones,\
  open('{}_UPLOAD DATA.csv'.format(IPFName), 'at') as CleanOutputDatabase,\
  open('{}_UPLOAD.csv'.format(IPFName), 'at') as CleanOutputPurchase,\
  open('{}_NITRO_LIST.csv'.format(IPFName), 'at') as CleanEmail,\
  open('{}_AddToMonthlySuppression.csv'.format(IPFName), 'at') as AppendMonthlySupp:
    CleanOutputFirstTime = True
    DatabaseFirstTime = True
    PurchaseFirstTimeAll = True
    PhonesFirstTime = True
    DupesFirstTime = True
    MDNQFirstTime = True
    MonthlySuppressionFirstTime = True
    EmailFirstTime = True
    YearDictCounter = {}
    MakeDictCounter = {}
    ModelDictCounter = {}
    SCFDictCounter = {}
    RadiusDictCounter = {}
    CityDictCounter = {}
    StateDictCounter = {}
    SCF3DFacilityCounter = {}
    DDUFacilityCounter = {}
    DropDictCounter = {}
    SoldYearCounter = {}
    OutputDroplist = []
    OutputDictOpenFiles = {}
    MDNQCounter = 0
    DupesCounter = 0
    TOTALMailCounter = 0
    Input = csv.reader(InputFile)
    next(InputFile)
    for line in tqdm(Input):
      TOTALMailCounter += 1
      if VendorSelect == 'P':
        WinningNumber = 42619 # Platinum
        line[Constants.Vendor] = 'Platinum'
      elif VendorSelect == 'S':
        WinningNumber = 40754 # Shopper
        line[Constants.Vendor] = 'Shopper'
      else:
        WinningNumber = 42619 # Default
        line[Constants.Vendor] = 'PWC'
      line[Constants.WinningNum] = WinningNumber
      VendorSelected = line[Constants.Vendor]

      # Parse FullName if First & Last Name fields are missing
      if line[Constants.FullName] != '' and \
      line[Constants.FirstName] == '' and\
      line[Constants.LastName] == '':
        try:
          ParsedFName = HumanName(str.title(line[Constants.FullName]))
          line[Constants.FirstName] = ParsedFName.first
          line[Constants.MI] = ParsedFName.middle
          line[Constants.LastName] = ParsedFName.last
        except:
          line[Constants.FullName] = ''

      # Parse Zip to Zip & Zip4 components (when possible)
      if len(str(line[Constants.Zip])) > 5 and\
      (str(line[Constants.Zip]).find('-') == 5):
        FullZip = line[Constants.Zip].split('-')
        line[Constants.Zip] = FullZip[0]
        line[Constants.Zip4] = FullZip[1]

      # Combine Zip + CRRT fields
      if line[Constants.Zip] != '' and\
      line[Constants.CRRT] != '':
        if len(str(line[Constants.Zip])) < 5:
          line[Constants.ZipCRRT] = '0{}{}'.format(
            line[Constants.Zip],
            line[Constants.CRRT]
            )
        else:
          line[Constants.ZipCRRT] = '{}{}'.format(
            line[Constants.Zip],
            line[Constants.CRRT]
            )

      # Combine Address1 + Address2
      if line[Constants.AddressComb] == '' and\
      line[Constants.Address1] != '' and\
      line[Constants.Address2] != '':
        line[Constants.AddressComb] = '{} {}'.format(
          str.title(line[Constants.Address1]),
          str.title(line[Constants.Address2])
          )
      elif line[Constants.Address1] != '' and\
      line[Constants.Address2] == '':
        line[Constants.AddressComb] = str.title(line[Constants.Address1])
      else:
        line[Constants.AddressComb] = str.title(line[Constants.AddressComb])

      # Expand Abreviated State
      if str.upper(line[Constants.State]) in Constants.USStatesDict:
        line[Constants.ExpState] = Constants.USStatesDict[str.upper(line[Constants.State])]

      # Set Drop Index from Drop Dictionary and Set CustomerID
      if line[Constants.PURL] == '':
        if str(line[Constants.ZipCRRT]) in DropDict:
          line[Constants.Drop] = DropDict[str(line[Constants.ZipCRRT])]
          if SourceSelect == 'D':
            line[Constants.CustomerID] = 'D{}'.format(
              str(Constants.SeqNumDatabase)
              )
            Constants.SeqNumDatabase += 1
          elif SourceSelect == 'P':
            line[Constants.CustomerID] = 'P{}'.format(
              str(Constants.SeqNumPurchase)
              )
            Constants.SeqNumPurchase += 1
        elif SourceSelect == 'D':
          line[Constants.Drop] = 'DATABASE'
          line[Constants.CustomerID] = 'D{}'.format(
            str(Constants.SeqNumDatabase)
            )
          Constants.SeqNumDatabase += 1
        elif SourceSelect == 'P':
          line[Constants.Drop] = 'PURCHASE'
          line[Constants.CustomerID] = 'P{}'.format(
            str(Constants.SeqNumPurchase)
            )
          Constants.SeqNumPurchase += 1

      # Parse & Clean up Phone#
      if line[Constants.MPhone] != '' and\
      len(str(line[Constants.MPhone])) > 6:
        line[Constants.Phone] = Constants.ReformatPhoneNum(line[Constants.MPhone])
      elif line[Constants.HPhone] != '' and\
      len(str(line[Constants.HPhone])) > 6:
        line[Constants.Phone] = Constants.ReformatPhoneNum(line[Constants.HPhone])
      elif line[Constants.WPhone] != '' and\
      len(str(line[Constants.WPhone])) > 6:
        line[Constants.Phone] = Constants.ReformatPhoneNum(line[Constants.WPhone])
      else:
        line[Constants.Phone] = ''

      # Re-Format Phone#
      if len(str(line[Constants.Phone])) == 10:
        line[Constants.Phone] = '({}) {}-{}'.format(
          str(line[Constants.Phone][0:3]),
          str(line[Constants.Phone][3:6]),
          str(line[Constants.Phone][6:10])
          )
      elif len(str(line[Constants.Phone])) == 7:
        line[Constants.Phone] = '{}-{}'.format(
          str(line[Constants.Phone][0:3]),
          str(line[Constants.Phone][3:7])
          )
      else:
        line[Constants.Phone] = ''

      # Set Case for data fields
      line[Constants.FullName] = str.title(line[Constants.FullName])
      line[Constants.FirstName] = str.title(line[Constants.FirstName])
      if len(str(line[Constants.MI])) == 1:
        line[Constants.MI] = str.upper(line[Constants.MI])
      elif len(str(line[Constants.MI])) > 1:
        line[Constants.MI] = str.title(line[Constants.MI])
      else:
        line[Constants.MI] = ''
      line[Constants.LastName] = str.title(line[Constants.LastName])
      line[Constants.Address1] = str.title(line[Constants.Address1])
      line[Constants.Address2] = str.title(line[Constants.Address2])
      line[Constants.City] = str.title(line[Constants.City])
      line[Constants.Make] = str.title(line[Constants.Make])
      line[Constants.Model] = str.title(line[Constants.Model])
      line[Constants.Email] = str.lower(line[Constants.Email])
      line[Constants.State] = str.upper(line[Constants.State])

      # Set VIN Length
      line[Constants.VINLen] = len(str(line[Constants.VIN]))
      if line[Constants.VINLen] < 17:
        line[Constants.VIN] = ''
      else:
        line[Constants.VIN] = str.upper(line[Constants.VIN])

      # Set SCF Facility Location
      ZipLen = len(str(line[Constants.Zip]))
      if ZipLen < 5:
        line[Constants.SCF] = (line[Constants.Zip])[:2]
      else:
        line[Constants.SCF] = (line[Constants.Zip])[:3]
      if str(line[Constants.SCF]) in SCF3DigitDict:
        line[Constants.SCF3DFacility] = SCF3DigitDict[str(line[Constants.SCF])]

      # Set Central Zip SCF Facility location
      CentralZipLen = len(str(CentralZip))
      if CentralZipLen < 5:
        CentralZipSCF3Digit = str(CentralZip[:2])
      else:
        CentralZipSCF3Digit = str(CentralZip[:3])
      if str(CentralZipSCF3Digit) in SCF3DigitDict:
        CentralZipSCFFacilityReport = SCF3DigitDict[str(CentralZipSCF3Digit)]

      # Set DDU Facility Location
      if str(line[Constants.Zip]) in DDUDict:
        line[Constants.DDUFacility] = DDUDict[str(line[Constants.Zip])]

      # Calculate Radius from CENTRAL Constants.Zip
      try:
        line[Constants.Zip] = int(line[Constants.Zip])
      except:
        line[Constants.Zip] = 9999

      # Remove Leading 0 from Constants.Zip Code
      if str(line[Constants.Zip])[:1] == 0 and\
      len(str(line[Constants.Zip])) == 4:
        line[Constants.Zip] = line[Constants.Zip][-4:]

      # Set Long & Lat Coordinates for Central Zip Code and Zip Code
      OriginZipCoord = ZipCoordinateDict[str(CentralZip)]
      if str(line[Constants.Zip]) in ZipCoordinateDict:
        line[Constants.Coordinates] = ZipCoordinateDict[str(line[Constants.Zip])]
      else:
        line[Constants.Coordinates] = ''

      # Set Constants.Radius
      if line[Constants.Coordinates] == '':
        line[Constants.Radius] = 9999.9999
      else:
        line[Constants.Radius] = vincenty(OriginZipCoord,line[Constants.Coordinates]).miles
        line[Constants.Radius] = round(float(line[Constants.Radius]),2)

      # Parse Date Field to DateTime format
      try:
        line[Constants.Date] = parse(line[Constants.Date]).date()
      except:
        line[Constants.Date] = ''

      # Apply "Blitz-DNQ" Parameters
      try:
        if len(str(line[Constants.Phone])) < 8 and\
        len(str(line[Constants.VIN])) < 17:
          line[Constants.BlitzDNQ] = 'dnq'
      except:
        line[Constants.BlitzDNQ] = ''

      # Apply Universal MAIL-DNQ Parameters
      if line[Constants.FirstName] == '' or\
      line[Constants.LastName] == '' or\
      (line[Constants.Address1] == '' and line[Constants.Address2] == '') or\
      (line[Constants.City] == '') or\
      (line[Constants.State] == '') or\
      (line[Constants.Zip] == '') or\
      float(line[Constants.Radius]) > MaxRadius:
        line[Constants.MailDNQ] = 'dnq'

      # Test Constants.Year Validity
      try:
        YearValidityTest = int(line[Constants.Year])
        if int(line[Constants.Year]) in Constants.YearDecodeDict:
          line[Constants.Year] = Constants.YearDecodeDict[int(line[Constants.Year])]
        if int(line[Constants.Year]) > MaxYear:
          line[Constants.MailDNQ] = 'dnq'
        if int(line[Constants.Year]) < MinYear and line[Constants.DelDate] == '':
          line[Constants.MailDNQ] = 'dnq'
      except:
        line[Constants.Year] = ''

      # Set 'n/a' for Constants.Make & Constants.Model blank fields
      if line[Constants.Make] == '':
        line[Constants.Make] = 'n/a'
      if line[Constants.Model] == '':
        line[Constants.Model] = 'n/a'

      # Prse & Test DelDate Validity
      try:
        line[Constants.DelDate] = parse(line[Constants.DelDate]).date()
        if int(line[Constants.DelDate].year) > MaxSaleYear or\
        int(line[Constants.DelDate].year) < MinSaleYear:
          line[Constants.MailDNQ] = 'dnq'
      except:
        line[Constants.DelDate] = ''
      if line[Constants.DelDate] != '':
        line[Constants.Dld_Year] = line[Constants.DelDate].year
        line[Constants.Dld_Month] = line[Constants.DelDate].month
        line[Constants.Dld_Day] = line[Constants.DelDate].day

      # Check Constants.Ethnicity
      CleanName = Constants.StripAndCleanName(line[Constants.LastName])
      if CleanName in Constants.CommonHispLastNameList:
        line[Constants.Ethnicity] = 'Hisp'

      # Set Adjusted KBB Value
      if line[Constants.KBB] != '':
        try:
          line[Constants.KBB] = int(line[Constants.KBB])
          if (line[Constants.KBB] * 1.2) < 3150:
            line[Constants.AdjustedKBBValue] = '${:,}'.format(3150)
          elif (line[Constants.KBB] * 1.2) > (line[Constants.KBB] + 4000):
            AdjKBB = int(line[Constants.KBB] + 4000)
            line[Constants.AdjustedKBBValue] = '${:,}'.format(AdjKBB)
          else:
            AdjKBB = int(line[Constants.KBB] * 1.2)
            line[Constants.AdjustedKBBValue] = '${:,}'.format(AdjKBB)
        except:
          line[Constants.MailDNQ] = 'dnq'

      # Validate Email Address
      if line[Constants.Email] != '':
        if not bool(re.search(r'.+@.+',line[Constants.Email],flags=re.I)):
          line[Constants.Email] = ''

      # Dedupe againts suppression files
      if str.lower(line[Constants.FirstName]) in Constants.DoNotMailSet or\
      str.lower(line[Constants.MI]) in Constants.DoNotMailSet or\
      str.lower(line[Constants.LastName]) in Constants.DoNotMailSet:
        line[Constants.MailDNQ] = 'dnq'
      if STATEList != []:
        if str.lower(line[Constants.State]) not in STATEList:
          line[Constants.MailDNQ] = 'dnq'
      if SCFList != []:
        if str(line[Constants.SCF]) not in SCFList:
          line[Constants.MailDNQ] = 'dnq'
      if CITYList != []:
        if str.lower(line[Constants.City]) in CITYList:
          line[Constants.MailDNQ] = 'dnq'

      # Generate COUNTERS
      def GenCounter(record, DictCntr):
        if str(record) not in DictCntr:
          DictCntr[str(record)] = 1
        else:
          DictCntr[str(record)] += 1
      CityRadius = '{} {} ({} Miles)'.format(
        line[Constants.City],
        line[Constants.Zip],
        line[Constants.Radius]
        )
      ZipRadius = '{} ({} Miles)'.format(
        line[Constants.Zip],
        line[Constants.Radius]
        )
      GenCounter(line[Constants.Year], YearDictCounter)
      GenCounter(line[Constants.Make], MakeDictCounter)
      GenCounter(line[Constants.SCF], SCFDictCounter)
      GenCounter(line[Constants.Radius], RadiusDictCounter)
      GenCounter(CityRadius, CityDictCounter)
      GenCounter(line[Constants.State], StateDictCounter)
      GenCounter(line[Constants.DDUFacility], DDUFacilityCounter)
      GenCounter(line[Constants.SCF3DFacility], SCF3DFacilityCounter)
      GenCounter(line[Constants.Drop], DropDictCounter)
      GenCounter(line[Constants.Dld_Year], SoldYearCounter)

      # OUTPUT Dupes and Mail-DNQ Files
      key = (str.title(line[Constants.AddressComb]), str(line[Constants.Zip]))
      keyNames = (str.title(line[Constants.FirstName]), str(line[Constants.LastName]))
      if key not in Entries and keyNames not in EntriesNames:
        if line[Constants.MailDNQ] == 'dnq':
          if MDNQFirstTime:
            OutMDNQ = csv.writer(MDNQ)
            OutMDNQ.writerow(Constants.HeaderRowMain)
            OutMDNQ.writerow(line)
            Entries.add(key)
            MDNQFirstTime = False
            MDNQCounter += 1
          else:
            OutMDNQ = csv.writer(MDNQ)
            OutMDNQ.writerow(line)
            Entries.add(key)
            MDNQCounter += 1
        else:
          if CleanOutputFirstTime:
            OutputClean = csv.writer(CleanOutput)
            OutputClean.writerow(Constants.HeaderRowMain)
            OutputClean.writerow(line)
            Entries.add(key)
            CleanOutputFirstTime = False
          else:
            OutputClean = csv.writer(CleanOutput)
            OutputClean.writerow(line)
            Entries.add(key)
      else:
        if DupesFirstTime:
          OutDupes = csv.writer(Dupes)
          OutDupes.writerow(Constants.HeaderRowMain)
          OutDupes.writerow(line)
          Entries.add(key)
          DupesFirstTime = False
          DupesCounter += 1
        else:
          OutDupes = csv.writer(Dupes)
          OutDupes.writerow(line)
          Entries.add(key)
          DupesCounter += 1

      # Output Suppression File
      if OutputFileSelect == 'Y':
        HeaderRowSuppressionStat = [
          'FirstName',
          'LastName',
          'Address',
          'City',
          'State',
          'Zip',
          'Campaign Name'
          ]
        HeaderRowSuppressionOutput = (
          line[Constants.FirstName],
          line[Constants.LastName],
          line[Constants.AddressComb],
          line[Constants.City],
          line[Constants.State],
          line[Constants.Zip],
          IPFName
          )
        if MonthlySuppressionFirstTime:
          MonthlySupp = csv.writer(AppendMonthlySupp)
          MonthlySupp.writerow(HeaderRowSuppressionStat)
          MonthlySupp.writerow(HeaderRowSuppressionOutput)
          MonthlySuppressionFirstTime = False
        else:
          MonthlySupp = csv.writer(AppendMonthlySupp)
          MonthlySupp.writerow(HeaderRowSuppressionOutput)

      # Output Phone File
      if OutputFileSelect == 'Y' and\
      line[Constants.Phone] != '' and\
      line[Constants.BlitzDNQ] != 'dnq' and\
      line[Constants.MailDNQ] != 'dnq':
        HeaderRowPhonesStat = [
          'FirstName',
          'LastName',
          'Phone',
          'Year',
          'Make',
          'Model'
          ]
        HeaderRowPhonesOutput = (
          line[Constants.FirstName],
          line[Constants.LastName],
          line[Constants.Phone],
          line[Constants.Year],
          line[Constants.Make],
          line[Constants.Model]
          )
        if PhonesFirstTime:
          OutputPhones = csv.writer(CleanOutputPhones)
          OutputPhones.writerow(HeaderRowPhonesStat)
          OutputPhones.writerow(HeaderRowPhonesOutput)
          PhonesFirstTime = False
        else:
          OutputPhones = csv.writer(CleanOutputPhones)
          OutputPhones.writerow(HeaderRowPhonesOutput)

      # Output Email/Eblast File
      if OutputFileSelect == 'Y':
        HeaderRowEmail = [
          'Customer ID',
          'FirstName',
          'LastName',
          'Address',
          'City',
          'State',
          'Zip',
          'Winning Number',
          'Position',
          'Phone',
          'TempEmail',
          'Year',
          'Make',
          'Model'
          ]
        HeaderRowEmailOutput = (
          line[Constants.CustomerID],
          line[Constants.FirstName],
          line[Constants.LastName],
          line[Constants.AddressComb],
          line[Constants.City],
          line[Constants.State],
          line[Constants.Zip],
          line[Constants.WinningNum],
          line[Constants.Drop],
          line[Constants.Phone],
          line[Constants.Email],
          line[Constants.Year],
          line[Constants.Make],
          line[Constants.Model]
          )
        if EmailFirstTime:
          CleanEmailOutput = csv.writer(CleanEmail)
          CleanEmailOutput.writerow(HeaderRowEmail)
          CleanEmailOutput.writerow(HeaderRowEmailOutput)
          EmailFirstTime = False
        else:
          CleanEmailOutput = csv.writer(CleanEmail)
          CleanEmailOutput.writerow(HeaderRowEmailOutput)

      # Output Database File
      if SourceSelect == 'D' and\
      OutputFileSelect == 'Y':
        HeaderRowDatabaseStat = [
          'Customer ID',
          'FirstName',
          'LastName',
          'Address',
          'City',
          'State',
          'Zip',
          '4Zip',
          'VIN',
          'Year',
          'Make',
          'Model',
          'Buyback_Value',
          'Winning Number',
          'Position'
          ]
        HeaderRowDatabaseOutput = (
          line[Constants.CustomerID],
          line[Constants.FirstName],
          line[Constants.LastName],
          line[Constants.AddressComb],
          line[Constants.City],
          line[Constants.State],
          line[Constants.Zip],
          line[Constants.Zip4],
          line[Constants.VIN],
          line[Constants.Year],
          line[Constants.Make],
          line[Constants.Model],
          line[Constants.AdjustedKBBValue],
          line[Constants.WinningNum],
          line[Constants.Drop]
          )
        if DatabaseFirstTime:
          OutputCleanDatabase = csv.writer(CleanOutputDatabase)
          OutputCleanDatabase.writerow(HeaderRowDatabaseStat)
          OutputCleanDatabase.writerow(HeaderRowDatabaseOutput)
          DatabaseFirstTime = False
        else:
          OutputCleanDatabase = csv.writer(CleanOutputDatabase)
          OutputCleanDatabase.writerow(HeaderRowDatabaseOutput)

      # Output Purchase File
      if SourceSelect == 'P' and\
      OutputFileSelect == 'Y':
        HeaderRowPurchaseStat = [
          'Customer ID',
          'FirstName',
          'LastName',
          'Address',
          'City',
          'State',
          'Zip',
          '4Zip',
          'VIN',
          'Year',
          'Make',
          'Model',
          'Buyback_Value',
          'DSF_WALK_SEQ',
          'Crrt',
          'Winning Number',
          'Position'
          ]
        HeaderRowPurchaseOutput = (
          line[Constants.CustomerID],
          line[Constants.FirstName],
          line[Constants.LastName],
          line[Constants.AddressComb],
          line[Constants.City],
          line[Constants.State],
          line[Constants.Zip],
          line[Constants.Zip4],
          line[Constants.VIN],
          line[Constants.Year],
          line[Constants.Make],
          line[Constants.Model],
          line[Constants.AdjustedKBBValue],
          line[Constants.DSF_WALK_SEQ],
          line[Constants.CRRT],
          line[Constants.WinningNum],
          line[Constants.Drop]
          )
        if PurchaseFirstTimeAll:
          OutputCleanPurchase = csv.writer(CleanOutputPurchase)
          OutputCleanPurchase.writerow(HeaderRowPurchaseStat)
          OutputCleanPurchase.writerow(HeaderRowPurchaseOutput)
          PurchaseFirstTimeAll = False
        else:
          OutputCleanPurchase = csv.writer(CleanOutputPurchase)
          OutputCleanPurchase.writerow(HeaderRowPurchaseOutput)

      # Output Multiple Drop Files
      if OutputFileSelect == 'Y':
        HeaderRowAppendStat = [
          'PURL',
          'FirstName',
          'LastName',
          'Address1',
          'City',
          'State',
          'Zip',
          '4Zip',
          'VIN',
          'Year',
          'Make',
          'Model',
          'Buyback_Value',
          'Crrt',
          'DSF_WALK_SEQ',
          'Customer ID',
          'Position'
          ]
        HeaderRowAppendOutput = (
          line[Constants.PURL],
          line[Constants.FirstName],
          line[Constants.LastName],
          line[Constants.Address1],
          line[Constants.City],
          line[Constants.State],
          line[Constants.Zip],
          line[Constants.Zip4],
          line[Constants.VIN],
          line[Constants.Year],
          line[Constants.Make],
          line[Constants.Model],
          line[Constants.AdjustedKBBValue],
          line[Constants.CRRT],
          line[Constants.DSF_WALK_SEQ],
          line[Constants.CustomerID],
          line[Constants.Drop]
          )
        if line[Constants.Drop] not in OutputDroplist:
          OutputDroplist.append(line[Constants.Drop])
          OutputDictOpenFiles[line[Constants.Drop]] = open('{}_{}.csv'.format(IPFName, line[Constants.Drop]), 'at')
          DropOutput = csv.writer(OutputDictOpenFiles[line[Constants.Drop]])
          DropOutput.writerow(HeaderRowAppendStat)
          DropOutput.writerow(HeaderRowAppendOutput)
        else:
          DropOutput = csv.writer(OutputDictOpenFiles[line[Constants.Drop]])
          DropOutput.writerow(HeaderRowAppendOutput)

# ---------------------- #
# Function to generate output file
def OutputFileSummaryReport():
  Report = sys.stdout
  with open('SUMMARY-REPORT_{}.html'.format(IPFName),'w') as Log:
    RadiusKeyList = sorted(RadiusDictCounter)
    NewRadiusList = []
    for item in RadiusKeyList:
      NewRadiusList.append(float(item))
    HighestRadius = Constants.ConvListToString(sorted(NewRadiusList)[-1:])
    HigherstYear = Constants.ConvListToString(sorted(YearDictCounter)[-1:])
    LowestYear = Constants.ConvListToString(sorted(YearDictCounter)[:1])
    sys.stdout = Log
    print('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.0/jquery.min.js"></script>
    <script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
    </head>
    <body>
    ''')
    print('<div class="container">')
    print('<div class="alert alert-info">')
    print('<h4 class="text-center">{}</h4>'.format(str.upper(IPFName)))
    print('</div>')
    print('<table class="table table-hover">')
    print('<tbody>')
    print('<tr><td>Summary Report Date</td><td>{}</td></tr>'.format(datetime.date.today()))
    print('<tr><td>Central Zip Code</td><td>{}</td></tr>'.format(CentralZip))
    print('<tr><td>Central Zip SCF Facility</td><td>{}</td></tr>'.format(CentralZipSCFFacilityReport))
    print('</tbody>')
    print('</table>')
    print('<p></p>')
    # ---------------------- #
    print('<table class="table table-hover">')
    print('<div class="alert alert-info">')
    print('<p class="text-center"><b>TOTAL Mail Quantity</b></p>')
    print('</div>')
    print('<thead>')
    print('<tr><th></th><th>Source</th><th>Count</th><th>Source%</th><th>RTotal</th><th>RTotal%</th></tr>')
    print('</thead>')
    print('<tbody>')
    DropRTotal = 0
    OdDropDictCounter = collections.OrderedDict(sorted(
      DropDictCounter.items(), key=lambda t: t[0]
      ))
    for key, value in OdDropDictCounter.items():
      DropRTotal = DropRTotal + value
      ValuePrcnt = Constants.ConvPercentage(value, TOTALMailCounter)
      RTotalPrcnt = Constants.ConvPercentage(DropRTotal, TOTALMailCounter)
      print('<tr><td></td><td>{}</td><td>{}</td><td>{}%</td><td>{}</td><td>{}%</td></tr>'.format(
        key,
        value,
        round(ValuePrcnt,2),
        DropRTotal,
        round(RTotalPrcnt,2)
        ))
    print('</tbody>')
    print('</table>')
    # ---------------------- #
    print('<table class="table table-hover">')
    print('<div class="alert alert-info">')
    print('<p class="text-center"><b>Quantity per State</b></p>')
    print('</div>')
    print('<thead>')
    print('<tr><th></th><th>State</th><th>Count</th><th>State%</th><th>RTotal</th><th>RTotal%</th></tr>')
    print('</thead>')
    print('<tbody>')
    StateRTotal = 0
    OdStateDictCounter = collections.OrderedDict(sorted(
      StateDictCounter.items(), key=lambda t: t[0], reverse = True
      ))
    for key, value in OdStateDictCounter.items():
      StateRTotal = StateRTotal + value
      ValuePrcnt = Constants.ConvPercentage(value, TOTALMailCounter)
      RTotalPrcnt = Constants.ConvPercentage(StateRTotal, TOTALMailCounter)
      print('<tr><td></td><td>{}</td><td>{}</td><td>{}%</td><td>{}</td><td>{}%</td></tr>'.format(
        key,
        value,
        round(ValuePrcnt,2),
        StateRTotal,
        round(RTotalPrcnt,2)
        ))
    print('</tbody>')
    print('</table>')
    # ---------------------- #
    print('<table class="table table-hover">')
    print('<div class="alert alert-info">')
    print('<p class="text-center"><b>Quantity per Destination Delivery Unit (DDU) ( > 500 )</b></p>')
    print('</div>')
    print('<thead>')
    print('<tr><th></th><th>DDU Facility</th><th>Count</th><th>DDU%</th><th>RTotal</th><th>RTotal%</th></tr>')
    print('</thead>')
    print('<tbody>')
    DDUFacilityRTotal = 0
    OdDDUFacilityCounter = collections.OrderedDict(sorted(
      DDUFacilityCounter.items(), key=lambda t: t[1], reverse = True
      ))
    for key, value in OdDDUFacilityCounter.items():
      DDUFacilityRTotal = DDUFacilityRTotal + value
      ValuePrcnt = Constants.ConvPercentage(value, TOTALMailCounter)
      RTotalPrcnt = Constants.ConvPercentage(DDUFacilityRTotal, TOTALMailCounter)
      if key == '':
        NewKey = 'Not Available'
      else:
        NewKey = key
      if value >= 500:
        print('<tr><td></td><td>{}</td><td>{}</td><td>{}%</td><td>{}</td><td>{}%</td></tr>'.format(
          NewKey,
          value,
          round(ValuePrcnt,2),
          DDUFacilityRTotal,
          round(RTotalPrcnt,2)
          ))
    print('</tbody>')
    print('</table>')
    # ---------------------- #
    print('<table class="table table-hover">')
    print('<div class="alert alert-info">')
    print('<p class="text-center"><b>Quantity per Sectional Center Facility (SCF)</b></p>')
    print('</div>')
    print('<thead>')
    print('<tr><th></th><th>SCF</th><th>Count</th><th>SCF%</th><th>RTotal</th><th>RTotal%</th></tr>')
    print('</thead>')
    print('<tbody>')
    SCFFacilityRTotal = 0
    OdSCF3DFacilityCounter = collections.OrderedDict(sorted(
      SCF3DFacilityCounter.items(), key=lambda t: t[1], reverse = True
      ))
    for key, value in OdSCF3DFacilityCounter.items():
      SCFFacilityRTotal = SCFFacilityRTotal + value
      ValuePrcnt = Constants.ConvPercentage(value, TOTALMailCounter)
      RTotalPrcnt = Constants.ConvPercentage(SCFFacilityRTotal, TOTALMailCounter)
      if key == '':
        NewKey = 'Not Available'
      else:
        NewKey = key
      print('<tr><td></td><td>{}</td><td>{}</td><td>{}%</td><td>{}</td><td>{}%</td></tr>'.format(
        NewKey,
        value,
        round(ValuePrcnt,2),
        SCFFacilityRTotal,
        round(RTotalPrcnt,2)
        ))
    print('</tbody>')
    print('</table>')
    # ---------------------- #
    print('<table class="table table-hover">')
    print('<div class="alert alert-info">')
    print('<p class="text-center"><b>Quantity per 3-Digit Zip Code Prefix Groups — SCF Sortation</b></p>')
    print('</div>')
    print('<thead>')
    print('<tr><th></th><th>3Digit</th><th>Count</th><th>3Digit%</th><th>RTotal</th><th>RTotal%</th></tr>')
    print('</thead>')
    print('<tbody>')
    SCFRTotal = 0
    OdSCFDictCounter = collections.OrderedDict(sorted(
      SCFDictCounter.items(), key=lambda t: t[1], reverse = True
      ))
    for key, value in OdSCFDictCounter.items():
      SCFRTotal = SCFRTotal + value
      ValuePrcnt = Constants.ConvPercentage(value, TOTALMailCounter)
      RTotalPrcnt = Constants.ConvPercentage(SCFRTotal, TOTALMailCounter)
      if value > 1000:
        if len(str(key)) == 2:
          print('<tr class="warning"><td></td><td>{}</td><td>{}</td><td>{}%</td><td>{}</td><td>{}%</td></tr>'.format(
            key,
            value,
            round(ValuePrcnt,2),
            SCFRTotal,
            round(RTotalPrcnt,2)
            ))
        else:
          print('<tr class="warning"><td></td><td>{}</td><td>{}</td><td>{}%</td><td>{}</td><td>{}%</td></tr>'.format(
            key,
            value,
            round(ValuePrcnt,2),
            SCFRTotal,
            round(RTotalPrcnt,2)
            ))
      else:
        if len(str(key)) == 2:
          print('<tr><td></td><td>0{}</td><td>{}</td><td>{}%</td><td>{}</td><td>{}%</td></tr>'.format(
            key,
            value,
            round(ValuePrcnt,2),
            SCFRTotal,
            round(RTotalPrcnt,2)
            ))
        else:
          print('<tr><td></td><td>{}</td><td>{}</td><td>{}%</td><td>{}</td><td>{}%</td></tr>'.format(
            key,
            value,
            round(ValuePrcnt,2),
            SCFRTotal,
            round(RTotalPrcnt,2)
            ))
    print('</tbody>')
    print('</table>')
    # ---------------------- #
    SortedSCFText = ''
    OdSCFDictCounter = collections.OrderedDict(sorted(
      SCFDictCounter.items(), key=lambda t: t[0]
      ))
    for key, value in OdSCFDictCounter.items():
      SortedSCFText = '{} {} |'.format(
        SortedSCFText,
        key
        )
    print('<!--',SortedSCFText,'-->')

    # ---------------------- #
    print('<table class="table table-hover">')
    print('<div class="alert alert-info">')
    print('<p class="text-center"><b>Year Sold Quantity</b></p>')
    print('</div>')
    print('<thead>')
    print('<tr><th></th><th>Year Sold</th><th>Count</th><th>Year Sold%</th><th>RTotal</th><th>RTotal%</th></tr>')
    print('</thead>')
    print('<tbody>')
    SoldYearRTotal = 0
    OdSoldYearCounter = collections.OrderedDict(sorted(
      SoldYearCounter.items(), key=lambda t: t[0], reverse = True
      ))
    for key, value in OdSoldYearCounter.items():
      SoldYearRTotal = SoldYearRTotal + value
      ValuePrcnt = Constants.ConvPercentage(value, TOTALMailCounter)
      RTotalPrcnt = Constants.ConvPercentage(SoldYearRTotal, TOTALMailCounter)
      if key == '':
        NewKey = 'Not Available'
      else:
        NewKey = key
      print('<tr><td></td><td>{}</td><td>{}</td><td>{}%</td><td>{}</td><td>{}%</td></tr>'.format(
        NewKey,
        value,
        round(ValuePrcnt,2),
        SoldYearRTotal,
        round(RTotalPrcnt,2)
        ))
    print('</tbody>')
    print('</table>')

    # ---------------------- #
    if len(YearDictCounter) !=  1:
      print('<table class="table table-hover">')
      print('<div class="alert alert-info">')
      print('<p class="text-center"><b>Vehicle Year Quantity</b></p>')
      print('</div>')
      print('<thead>')
      print('<tr><th></th><th>Vehicle Year</th><th>Count</th><th>Vehicle Year%</th><th>RTotal</th><th>RTotal%</th></tr>')
      print('</thead>')
      print('<tbody>')
      YearRTotal = 0
      OdYearDictCounter = collections.OrderedDict(sorted(
        YearDictCounter.items(), key=lambda t: t[0], reverse = True
        ))
      for key, value in OdYearDictCounter.items():
        YearRTotal = YearRTotal + value
        ValuePrcnt = Constants.ConvPercentage(value, TOTALMailCounter)
        RTotalPrcnt = Constants.ConvPercentage(YearRTotal, TOTALMailCounter)
        if key == '':
          NewKey = 'Not Available'
        else:
          NewKey = key
        print('<tr><td></td><td>{}</td><td>{}</td><td>{}%</td><td>{}</td><td>{}%</td></tr>'.format(
          NewKey,
          value,
          round(ValuePrcnt,2),
          YearRTotal,
          round(RTotalPrcnt,2)
          ))
      print('</tbody>')
      print('</table>')
    # ---------------------- #
    print('<table class="table table-hover">')
    print('<div class="alert alert-info">')
    print('<p class="text-center"><b>Quantity per Central Zip Radius</b></p>')
    print('</div>')
    print('<thead>')
    print('<tr><th></th><th>Radius</th><th>Count</th><th>Radius%</th><th>RTotal</th><th>RTotal%</th></tr>')
    print('</thead>')
    print('<tbody>')
    RadiusRTotal = 0
    OdRadiusDictCounter = collections.OrderedDict(sorted(
      RadiusDictCounter.items(), key=lambda t: float(t[0])
      ))
    for key, value in OdRadiusDictCounter.items():
      RadiusRTotal = RadiusRTotal + value
      ValuePrcnt = Constants.ConvPercentage(value, TOTALMailCounter)
      RTotalPrcnt = Constants.ConvPercentage(RadiusRTotal, TOTALMailCounter)
      if ValuePrcnt > TOPPercentage:
        print('<tr class="warning"><td></td><td>{} Miles</td><td>{}</td><td>{}%</td><td>{}</td><td>{}%</td></tr>'.format(
          key,
          value,
          round(ValuePrcnt,2),
          RadiusRTotal,
          round(RTotalPrcnt,2)
          ))
      else:
        print('<tr><td></td><td>{} Miles</td><td>{}</td><td>{}%</td><td>{}</td><td>{}%</td></tr>'.format(
          key,
          value,
          round(ValuePrcnt,2),
          RadiusRTotal,
          round(RTotalPrcnt,2)
          ))
    print('</tbody>')
    print('</table>')
    # ---------------------- #
    if len(MakeDictCounter) !=  1:
      print('<table class="table table-hover">')
      print('<div class="alert alert-info">')
      print('<p class="text-center"><b>Quantity per Vehicle Make ( > {}% )</b></p>'.format(TOPPercentage))
      print('</div>')
      print('<thead>')
      print('<tr><th></th><th>Make</th><th>Count</th><th>Make%</th><th>RTotal</th><th>RTotal%</th></tr>')
      print('</thead>')
      print('<tbody>')
      MakeRTotal = 0
      OdMakeDictCounter = collections.OrderedDict(sorted(
        MakeDictCounter.items(), key=lambda t: t[1], reverse = True
        ))
      for key, value in OdMakeDictCounter.items():
        MakeRTotal = MakeRTotal + value
        ValuePrcnt = Constants.ConvPercentage(value, TOTALMailCounter)
        RTotalPrcnt = Constants.ConvPercentage(MakeRTotal, TOTALMailCounter)
        if ValuePrcnt > TOPPercentage:
          print('<tr class="warning"><td></td><td>{}</td><td>{}</td><td>{}%</td><td>{}</td><td>{}%</td></tr>'.format(
            key,
            value,
            round(ValuePrcnt,2),
            MakeRTotal,
            round(RTotalPrcnt,2)
            ))
        else:
          print('<tr><td></td><td>{}</td><td>{}</td><td>{}%</td><td>{}</td><td>{}%</td></tr>'.format(
            key,
            value,
            round(ValuePrcnt,2),
            MakeRTotal,
            round(RTotalPrcnt,2)
            ))
      print('</tbody>')
      print('</table>')
    # ---------------------- #
    print('<table class="table table-hover">')
    print('<div class="alert alert-info">')
    print('<p class="text-center"><b>Quantity per City ( > {}% )</b></p>'.format(TOPPercentage))
    print('</div>')
    print('<thead>')
    print('<tr><th></th><th>City</th><th>Count</th><th>City%</th><th>RTotal</th></tr>')
    print('</thead>')
    print('<tbody>')
    CityRTotal = 0
    OdCityDictCounter = collections.OrderedDict(sorted(
      CityDictCounter.items(), key=lambda t: t[1], reverse = True
      ))
    for key, value in OdCityDictCounter.items():
      CityRTotal = CityRTotal + value
      ValuePrcnt = Constants.ConvPercentage(value, TOTALMailCounter)
      if ValuePrcnt > TOPPercentage:
        print('<tr class="warning"><td></td><td>{}</td><td>{}</td><td>{}%</td><td>{}</td></tr>'.format(
          key,
          value,
          round(ValuePrcnt,2),
          CityRTotal
          ))
    print('</tbody>')
    print('</table>')
    # ---------------------- #
    print('<table class="table table-hover">')
    print('<div class="alert alert-info">')
    print('<p class="text-center"><b>Quantity per City</b></p>')
    print('</div>')
    print('<thead>')
    print('<tr><th></th><th>City</th><th>Count</th><th>City%</th><th>RTotal</th><th>RTotal%</th></tr>')
    print('</thead>')
    print('<tbody>')
    CityRTotal = 0
    OdCityDictCounter = collections.OrderedDict(sorted(
      CityDictCounter.items(), key=lambda t: t[0]
      ))
    for key, value in OdCityDictCounter.items():
      CityRTotal = CityRTotal + value
      ValuePrcnt = Constants.ConvPercentage(value, TOTALMailCounter)
      RTotalPrcnt = Constants.ConvPercentage(CityRTotal, TOTALMailCounter)
      if ValuePrcnt > TOPPercentage:
        print('<tr class="warning"><td></td><td>{}</td><td>{}</td><td>{}%</td><td>{}</td><td>{}%</td></tr>'.format(
          key,
          value,
          round(ValuePrcnt,2),
          CityRTotal,
          round(RTotalPrcnt,2)
          ))
      else:
        print('<tr><td></td><td>{}</td><td>{}</td><td>{}%</td><td>{}</td><td>{}%</td></tr>'.format(
          key,
          value,
          round(ValuePrcnt,2),
          CityRTotal,
          round(RTotalPrcnt,2)
          ))
    print('</tbody>')
    print('</table>')
    # ---------------------- #
    print('''
    </div>
    </div>
    </body>
    </html>
    ''')
    sys.stdout = Report
  print('================ TOTAL ================ : {}'.format(TOTALMailCounter))
  print('       C  O  M  P  L  E  T  E  D       ')
  print('=======================================')
  print()
# ---------------------- #
if __name__ == '__main__':
  if HRSelect == 'Y':
    ReMapFunc()
  else:
    Selection = InputFile
  NormalizeFunc()
  if (MDNQCounter + DupesCounter) == 0:
    OutputFileSummaryReport()
  for i in OutputDictOpenFiles:
    OutputDictOpenFiles[i].close
  Constants.Upkeep()
