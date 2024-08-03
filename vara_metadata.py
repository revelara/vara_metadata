#
#   This script was created to merge all the metadata files of the 
#   Vara Network runtimes into a single file called metadata.json
#

import requests
import json

# Replace with your actual subscan API key
api_key = "ac5cf1251493454991e62c483bceea8f"  

# Define the headers
headers = {
    "x-api-key": api_key,
    "Content-Type": "application/json"
}

def get_runtimes_as_list():
    #API for listing runtimes
    url = "https://vara.api.subscan.io/api/scan/runtime/list"
    payload = { }
    response = requests.post(url, headers=headers, json=payload)
    runtimes_list = response.json().get('data', {}).get('list', [])

    # Create a dictionary with 'spec_version' as keys
    spec_versions = {i: runtime['spec_version'] for i, runtime in enumerate(runtimes_list)}

    # Returns the dictionary
    return spec_versions



#API for get metadata based on the runtime
url = "https://vara.api.subscan.io/api/scan/runtime/metadata"
runtimes = get_runtimes_as_list()

#Empty runtimes because the YOUR_SUBSCAN_API_KEY is wrong
if not runtimes:
    print ("Please change YOUR_SUBSCAN_API_KEY with your own Subscan API Key")

#Creates a json file per each runtime
for index, (key, runtime) in enumerate( runtimes.items()):
        payload = { "spec": runtime }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            with open(str(runtime)+'.json', 'w') as json_file:
                json.dump(response.json(), json_file, indent=4)
            print ("Metadata of runtime "+ str(runtime) + " saved into the file :" + str(runtime) + ".json")
        else:
            print(str(response.text))
