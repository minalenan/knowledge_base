# https://jyotiskabhattacharjee.medium.com/guide-to-deleting-emails-using-google-gmail-apis-252e4a98572 for context
#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import traceback
import requests
import base64
import urllib.parse
import sys
import getopt


# In[1]:


# The access token comes from Google OAuth 2.0 Playground
accessToken = "ya29.a0AVA9y1t3j3FdWem5iKawXnrm_vuu1eoHRXpGfdJ84Mo2J-UmblnCE15c2d8ycvXrILV4Z-lmRx7Lg6OcYn0k1qQQ7ZaVpSKDsuJSaY7K0VR3GEtOKhLLDtFfB6yOPbDZdrmZIqdBy5wN-xXzuONStfOkqIH4aCgYKATASARMSFQE65dr8GUng9Su4vVW-CiJP8c8uNw0163"
# The query string can be exactly the same as on the Gmail client
queryString = "category:promotions after:2022/01/01 before:2022/05/31"

# These URLs work for my personal email with the "me" parameter as a user
getEmailUrl = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
deleteBatchEmailUrl = "https://gmail.googleapis.com/gmail/v1/users/me/messages/batchDelete"

# email counter
counter = 0

# Dry run option
# True means no deletion is performed
dryRun = False

# Verbose logging option
# True means extra log messages will be printed out
verboseLogging = False

# In[ ]:


# Generate a list of email IDs from the url generated from search query
def findEmails(accessToken, queryString):
    global dryRun, verboseLogging
    headers = {
      "Authorization": "Bearer {}".format(accessToken),
      "Content-Type": "application/json"
    }
    if queryString:
        url = getEmailUrl + "?q=" + str(urllib.parse.quote(queryString, safe=""))
    else:
        print("Danger! No queryString is provided. Cannot proceed. Exiting")
        sys.exit(2)
    if verboseLogging:    
        print("Getting emails... getEmailUrl = " + url)
    response = requests.get(url, headers=headers)
    if verboseLogging:    
        print(response.json())
    emailIds = []
    if response.json().get("messages"):
        for i in response.json().get("messages"):
            emailIds.append(i.get("id"))
    if verboseLogging:
        print("getEmail API Response:")
        print(emailIds)        
    return(emailIds)
    


# In[ ]:


# Delete emails from the email
def deleteEmails(accessToken, emailIds):
    global dryRun, verboseLogging
    headers = {
          "Authorization": "Bearer {}".format(accessToken),
          "Content-Type": "application/json",
          "Accept": "application/json"
        }
    payload = """{}""".format({"ids": emailIds})
    if verboseLogging:
        print("Deleting {} emails", len(payload))
        print("API Payload:")
        print(payload)
    if dryRun:
        print("Dry run mode. Nothing is deleted.")
        return()
    else:
        response = requests.post(deleteBatchEmailUrl, headers=headers, data=payload)
        return(response)


def strToBoolean(str):
    ret = False
    if str:
        if str.strip().lower() == "true":
            ret = True
    return ret

# In[ ]:

# Main function
# Get parameters from command line
# Since the findEmails will return only 100 at a time, we need to delete and loop through the rest, until all is gone.
def main(argv):
    global counter, accessToken, queryString, dryRun, verboseLogging
    counter = 0
    try:
        opts, args = getopt.getopt(argv,"hq:t:d:v:",["queryString=", "accessToken=", "dryRun=", "verboseLogging="])
    except getopt.GetoptError:
        print("gmail_bulk_delete_using_api.py -q <queryString> -t <accessToken> -d <dryRun> -v <verboseLogging>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("gmail_bulk_delete_using_api.py -q <queryString> -t <accessToken> -d <dryRun> -v <verboseLogging>")
            sys.exit()
        elif opt in ("-q", "--queryString"):
            queryString = arg.strip()
        elif opt in ("-t", "--accessToken"):
            accessToken = arg.strip()
        elif opt in ("-d", "--dryrun"):
            dryRun = strToBoolean(arg)
        elif opt in ("-v", "--verboseLogging"):
            print(arg)
            verboseLogging = strToBoolean(arg)
            print(verboseLogging)

    print("\n")
    print("The program has started with the following parameters.")
    print("queryString = ", queryString)
    print("accessToken = ", accessToken)
    print("dryRun = ", dryRun)
    print("verboseLogging = ", verboseLogging)
    print("\n")



    # sys.exit(2)

    while True:
        try:
            emailIds = findEmails(accessToken, queryString)
            if emailIds:
                counter = counter + len(emailIds)
                deleteEmails(accessToken, emailIds)
                print("counter=" + str(counter))
                if not dryRun:
                    print("deleted emails=" + str(len(emailIds)))
                print("\n")
            else:
                print("Completed! Total deleted emails=" + str(counter))
                break
        except requests.ConnectionError as e:
            print(e)
        except requests.HTTPError as e:
            status_code = e.response.status_code
            if (status_code == 401):
                print("Authentication is invalid. Please authenticate again at Google OAuth 2.0 Playground, https://developers.google.com/oauthplayground/")        
            print(e)
        except:
            traceback.print_exc()
            print("Exception occurred")
            break

if __name__ == "__main__":
    main(sys.argv[1:])


# In[ ]:




