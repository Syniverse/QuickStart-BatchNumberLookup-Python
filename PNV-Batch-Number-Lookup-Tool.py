# ABA-example.py
# tested in python 3.6
# implements Phone Number Scrub via ABA and MSS

# uses one non-standard Python Library -> Requests
# see http://docs.python-requests.org/en/master/
# zlib is used to decompress the output file

import time
import zlib
import requests
import sys
import os


# this will be your access token
access_token = ''
company_id = ''

print("\n###Starting Pre Validation Checks###")

print("\n---No of arguments entered", len(sys.argv) - 1, "out of 3")

for arg in sys.argv:
    #print(arg)
    
    if len(sys.argv) != 4:
        print("\n---Error in argument list")
        print("\n---Usage $python PNV-Batch-number-Lookup-Tool.py <INPUT FILE NAME> <Feature Set> <File Retention in Days>")
        print("\n---Valid values for feature set: fs1, fs2, fs3, fs5 or fs23")
        print("\n---File Retention Days should be 1 to 7 only")
        print("\n---Example: $python PNV-Batch-number-Lookup-Tool.py phonenumbers.txt fs1 1")
        sys.exit()
    
    else:
        #Command line arguments passed and processed 
        python_script_name = sys.argv[0].strip()
        input_file_name = sys.argv[1].strip()
        feature_set = 'NIS-Scrub-v3-' + sys.argv[2].strip()
        fs = sys.argv[2].strip()
        file_expiry = int(sys.argv[3])

#Validating the command line arguments 
#command line argument validation for Inputfilename, feature set and file expiry
#allowed values are input file with .txt extention, feature set allowed are fs1, fs2, fs3, fs5 or fs23
#allwed values for file expiry are between 1 and 7
 
if len(sys.argv) == 4:
    if (input_file_name[-4:] != ".txt"):
        print("\n---ERROR:Input file not provided or Invalid file type, check for .txt file extention")
        sys.exit()
    else:
        print("\n---Input File:", input_file_name)
    
    '''    
    if (not fs == "fs1" or fs == "fs2" or fs == "fs3" or fs == "fs5" or fs == "fs23"):
        print("\n---ERROR: Feature_set not provided or Invalid, allowed values are fs1, fs2, fs3, fs5 or fs23 only")
        sys.exit()
    else:
        print("\n---Feature set entered is :",fs)
    '''
    if (fs == "fs1" or fs == "fs2" or fs == "fs3" or fs == "fs5" or fs == "fs23"):
        print("\n---Feature set entered is :",fs)
    else:
        print("\n---ERROR: Feature_set not provided or Invalid, allowed values are fs1, fs2, fs3, fs5 or fs23 only")
        sys.exit()
              
    if (file_expiry < 1 or file_expiry > 7 ):
        print("\n---File Retention Days:", file_expiry)
        print("\n---ERROR: File Retention days to retain input file & output files, are between 1 to 7 only")
        sys.exit()
    else:
        print("\n---File Retention Days:", file_expiry)

# As an example in input file, it contains the following MDNs
#+18132633923
#+18135041457
#+18139551760
# i.e. full phone number including leading + and international code
# I have only included 3 numbers, but it can contain up to 5 million
# the only difference to the below code would be that you have to wait
# for over an hour.
        
#Get the count of no of MDNs in input file
with open(input_file_name) as f:
    for i, l in enumerate(f):
        count = i + 1
print("\n###Pre Validation Checks Completed###")
#Begin the Batch Scrub Process for the MDNs in Input file 
print ('\n### Starting Engines ###\n')

       
## Step 1: We will create the input file in Media Storage
print ('\nCreating file in Media Storage')

create_file_url = 'https://api.syniverse.com/mediastorage/v1/files'

###----###
create_file_payload = {'fileName': '', 'fileTag': '', 'fileFolder': '', 'appName': '', 'expire_time': file_expiry,
                       'checksum': '', 'file_fullsize': '2000000'}

create_file_headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json', 'ext_trx_id':'392','ext_reseller_cust_id':'492','int-companyid': company_id}

create_file_response = requests.post(create_file_url, json=create_file_payload, headers=create_file_headers)

print(create_file_headers)
print ('\ncreate file response status code: ' + str(create_file_response.status_code))
print ('\nmss create response body: ' + create_file_response.text)

#if the response is not 201 then exit
if (str(create_file_response.status_code) != '201' ):
    print("\nError in File creation, Exiting")
    sys.exit()

    
## Step 2: We will upload the input file to Media Storage
print ('\nUploading input file to Media Storage')

# get the file_id, company id from the create file response
file_id = create_file_response.json()['file_id']
company_id = create_file_response.json()['company-id']

# the URL to use in the request also comes from the create file response
upload_uri = create_file_response.json()['file_uri']

###----###
upload_headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/octet-stream',
                  'int-companyid': company_id, 'ext_trx_id':'392','ext_reseller_cust_id':'492'}

upload_data = open(input_file_name, 'rb').read()

upload_file_response = requests.post(upload_uri, data=upload_data, headers=upload_headers)

print ('\nupload response status code: ' + str(upload_file_response.status_code))
print ('\nupload response: ' + upload_file_response.text)

#if the response is not 201 then exit
if (str(upload_file_response.status_code) != '201' ):
    print("\nError in File Upload, Exiting")
    sys.exit()

## Step 3: Schedule the batch job in Batch Automation
print ('\nScheduling the Number Verification batch job in Batch Automation')

schedule_job_url = 'https://api.syniverse.com/aba/v1/schedules'

###----###
schedule_job_headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}

###---###
schedule_job_payload = {"schedule": { "jobId" : feature_set, "name" : "PNVScrub", "inputFileId" : file_id,
                                       "fileRetentionDays" : file_expiry, "scheduleRetentionDays" : file_expiry,
                                       "outputFileNamingExpression" : "DS1-NIS-Scrub-output.txt",
                                       "outputFileFolder" : "/opt/apps/aba/output",
                                       "outputFileHeaderType": "basic"
                                      }}

schedule_job_response = requests.post(schedule_job_url, json=schedule_job_payload,
                                       headers=schedule_job_headers)

print ('\nScheduling response status code: ' + str(schedule_job_response.status_code))
print ('\nScheduling response: ' + schedule_job_response.text)

#if the response is not 201 then exit
if (str(schedule_job_response.status_code) != '201' ):
    print("\nError in File Scheduling, Exiting")
    sys.exit()


## Step 4: Wait for job to complete.
# this approach keeps it simple.
# An exercise for the reader would be to either
# 1) implement a loop that checks for when the job is complete
# 2) implement the callback url so details are only received once the job is complete

#while loop ------
#time.sleep(50)
#timeout = time.time() + 60*5 #five minutes
print ('\nRetrieving batch job execution details')


## Step 5: Get batch job execution details (hoping that job has completed)
while True:
    # we get the schedule id from the response when we scheduled the batch job
    # the response is nested json so we need two keys
    print ('\nWaiting for job to complete')

    schedule_id = schedule_job_response.json()['schedule']['id']

    # we create the URL to retrieve the batch job execution details
    check_execution_url = '/'.join(['https://api.syniverse.com/aba/v1/schedules', schedule_id, 'executions'])

    check_execution_headers = {'Authorization': 'Bearer ' + access_token}

    check_execution_response = requests.get(check_execution_url, headers=check_execution_headers)

    sc = check_execution_response.json()['executions'][0]['status']
    if (sc == "COMPLETE"):
        print ('\nGet batch job details status code: ' + str(check_execution_response.status_code))
        print ('\nGet batch job details response: ' + check_execution_response.text)
        break
    else:
        time.sleep(30)
        print("\nSleeping for 30 Seconds")

#-exit while loop here

## Step 6: We download the results from Media Storage
download_output_headers ={'Authorization': 'Bearer ' + access_token, 'int-companyid': company_id, 'ext_trx_id':'392','ext_reseller_cust_id':'492'}

outputDetailField = check_execution_response.json()['executions'][0]['outputFileId']
if(outputDetailField != 'EMPTY_FILE'):
	print ('\nDownloading the Success Output file')

	# In this simple example we trust that
	# 1) the job is complete
	# 2) it was successful
	# 3) we only download the output file

	# We get the output file URI from the execution details response.
	# the JSON response include both nested JSON and a list

	output_file_uri = check_execution_response.json()['executions'][0]['outputFileURI']

	#print("\n", output_file_uri)

	download_output_response = requests.get(output_file_uri, headers=download_output_headers, allow_redirects=True)
	download_output_response.raise_for_status() #ensure we notice for bad status

	#if the response is not 201 then exit
	if (str(download_output_response.status_code) != '200' ):
		print("\nError in File Download, Exiting")
		sys.exit()

	path = os.getcwd()
	file = path + '\PNV-Scrub-Success-' + input_file_name[:-4] + '.zip'
	success_file = file
	tempzip = open(file, "wb")
	tempzip.write(download_output_response.content)
	tempzip.close()

	#print("\nDownload Output Response:",download_output_response.text)
	#----before decompressing write to a file download_output_response.content
	#---if there is a error file or retry file you need to download that also.
	#print attribute "recordSuccessCount":1705436,"recordRetryCount":0,"recordErrorCount":531,

	output_data = zlib.decompress(download_output_response.content, zlib.MAX_WBITS|32)

	print ('\nDownload output status code: ' + str(download_output_response.status_code))
	#print ('Download output response: \n' + str(output_data))
else:
    print("\nThere is no output File to download")

#Step 7: We download the error file from Media Storage
#Downloading Error File
            
# In this simple example we trust that
# 1) the job is complete
# 2) some MDNs records it had errors
# 3) we only download the error file

# We get the error file URI from the execution details response.
# the JSON response include both nested JSON and a list
               
errorDetailField = check_execution_response.json()['executions'][0]['errorDetailFileId']

if(errorDetailField != 'EMPTY_FILE'):
    print("\nDownloading Error File")       
    error_file_uri = check_execution_response.json()['executions'][0]['errorDetailFileURI']

    #print("\n", error_file_uri)
    #print("\ndownload output headers",download_output_headers)
    #print("\n")

    download_error_response = requests.get(error_file_uri, headers=download_output_headers, allow_redirects=True)
    download_error_response.raise_for_status() #ensure we notice for bad status

    path = os.getcwd()
    file = path + '\PNV-Scrub-Error-' + input_file_name
    error_file = file
    etempzip = open(file, "wb")
    etempzip.write(download_error_response.content)
    etempzip.close()
    print ('\nDownload error file status code: ' + str(download_error_response.status_code))
    
#error_output_data = zlib.decompress(download_error_response.content, zlib.MAX_WBITS|32)

#print ('Download output response: \n' + str(error_output_data))
else:
    print("\nThere is no Error File to download")
    
#Step 8: We download the retry file from Media Storage
#Downloading Retry File
            
# In this simple example we trust that
# 1) the job is not complete
# 2) some MDNs records had retrys
# 3) we only download the retry file

# We get the retry file URI from the execution details response.
# the JSON response include both nested JSON and a list    

retryFile = check_execution_response.json()['executions'][0]['retryFileId']

if(retryFile != 'EMPTY_FILE'):
    print("\nDownloading Retry File")       
    retry_file_uri = check_execution_response.json()['executions'][0]['retryFileURI']

    print("\n", retry_file_uri)

    download_retry_response = requests.get(retry_file_uri, headers=download_output_headers, allow_redirects=True)
    download_retry_response.raise_for_status() #ensure we notice for bad status

    path = os.getcwd()
    file = path + '\PNV-Scrub-Retry-' + input_file_name
    retry_file = file
    rtempzip = open(file, "wb")
    rtempzip.write(download_retry_response.content)
    rtempzip.close()
    print ('\nDownload retry file status code: ' + str(download_retry_response.status_code))
else:
    print("\nThere is no Retry File to download")

#Step9 printing the success, error and retry count count, files and their location
# in this step we presume the engine has completed its execution
success_count = check_execution_response.json()['executions'][0]['recordSuccessCount']
error_count = check_execution_response.json()['executions'][0]['recordErrorCount']
retry_count = check_execution_response.json()['executions'][0]['recordRetryCount']
    

print("\n---Number of MDNs in Input File :",count)        
print("\n---Number of Success Count      :",success_count)
print("\n---Number of Error Count        :",error_count)
print("\n---Number of retry Count        :",retry_count)

#printing the files to refer in the appropriate directory
print ("\n---Please check the output files in the same directory where the script is running:", os.getcwd())

#print the name of output files
if (success_count > 0):
    print ("\n---Success File Location: ", success_file)
if (error_count > 0):
    print ("\n---Error File Location: ", error_file)
if (retry_count > 0):
    print ("\n---Retry File Location: ", retry_file)

print("\n###Job Completed###")    
## End
