# SyniverseSDC-BatchAutomation
Python example for Batch Job Automation using the Syniverse Developer Community

Syniverse Developer Centre (SDC) is at https://developer.syniverse.com

### Requires
- Syniverse Developer Community (SDC) Account
- SDC Subscription to Phone Number Verification
- SDC Application created with Batch Automation, Media Storage and Phone Number Verification enabled for the App.
- Access Token for application

Detailed instructions can be found at https://developer.syniverse.com & https://sdcdocumentation.syniverse.com/index.php

- Python installed (version 3.6 used in the example, use verion 3.9 for newer version-change file name where relevant.)
- time, zlib, csv, sys, os, requests module's should be installed ($pip install <module name>)

File Name:PNV-Batch-Number-Lookup-Tool.py



### Provide Access token in the script
- Open the script in a Text File or Python Editor Tool
- provide the Bearer Token that you are authorized to use under the attribute access_token = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

### Command to run the script/tool


$ python <Script_Name> <input_file> <feature_set> <file_retention_days>
- Script_Name = PNV-Batch-Number-Lookup-Tool.py
- input_file = <InputFileName>.txt Data File with Phone Numbers to Scrub in ASCII Text format (phone numbers within the file should be mentioned in E164 format eg.,+1831325XXXX)
- feature_set =  fs1,  fs2, fs3, fs23
- file_retention_days = anywhere between 1 and 7

Eg., In order to run from command line:
- $ python PNV-Batch-Number-Lookup-Tool.py phonenumbers.txt fs1 1

    
### How to identify output files
- All the output files, are generated in the same directory.
- The following files are created only when there is a success, error or retry output,
- else the files will not be created. 

--PNV-Scrub-Retry-<InputFileName>.txt
  
--PNV-Scrub-Success-<InputFileName>.zip
  
--PNV-Scrub-Error-<InputFileName>.txt
  

- you will need to take back up of these files before you can start the next process.
  else the files will be overwritten.
 
