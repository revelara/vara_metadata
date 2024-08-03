#
#   This script was created to merge all the metadata files of the 
#   Vara Network runtimes into a single file called metadata.json
#

import requests
import json
import os

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


def read_json_files(directory):
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    json_files.sort(key=lambda x: int(os.path.splitext(x)[0]))
    return json_files


def merge_dicts(main_dict, new_dict):
    for key, value in new_dict.items():
        if key not in main_dict:
            main_dict[key] = value
        else:
            if isinstance(value, dict) and isinstance(main_dict[key], dict):
                merge_dicts(main_dict[key], value)
            elif isinstance(value, list) and isinstance(main_dict[key], list):
                # Handle lists of dictionaries with 'name' key
                existing_items = {item['name'] for item in main_dict[key] if isinstance(item, dict) and 'name' in item}
                for item in value:
                    if isinstance(item, dict) and 'name' in item:
                        if item['name'] not in existing_items:
                            main_dict[key].append(item)
                            existing_items.add(item['name'])
                        else:
                            # Merge child nodes if 'name' exists
                            for existing_item in main_dict[key]:
                                if isinstance(existing_item, dict) and existing_item.get('name') == item['name']:
                                    merge_dicts(existing_item, item)
                    elif item not in main_dict[key]:
                        main_dict[key].append(item)
            else:
                if main_dict[key] != value:
                    if not isinstance(main_dict[key], list):
                        main_dict[key] = [main_dict[key]]
                    if value not in main_dict[key]:
                        main_dict[key].append(value)


#API for get metadata based on the runtime
url = "https://vara.api.subscan.io/api/scan/runtime/metadata"
runtimes = get_runtimes_as_list()

#Empty runtimes because the YOUR_SUBSCAN_API_KEY is wrong
if not runtimes:
    print ("Please change YOUR_SUBSCAN_API_KEY with your own Subscan API Key")

#Creates a json file per each runtime
"""
for index, (key, runtime) in enumerate( runtimes.items()):
        payload = { "spec": runtime }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            with open(str(runtime)+'.json', 'w') as json_file:
                json.dump(response.json(), json_file, indent=4)
            print ("Metadata of runtime "+ str(runtime) + " saved into the file :" + str(runtime) + ".json")
        else:
            print(str(response.text))
"""


def main():

    # Eliminar el archivo metadata.json si existe
    if os.path.exists('metadata.json'):
        os.remove('metadata.json')

    directory = '.'  # Change this to your JSON directory path
    json_files = read_json_files(directory)

    if not json_files:
        print("No JSON files found in the directory.")
        return

    # Find the file with the highest number and use it as the base metadata.json
    highest_file = json_files[-1]
    print(f"The file with the highest number is: {highest_file}")

    with open(os.path.join(directory, highest_file), 'r', encoding='utf-8') as file:
        metadata = json.load(file)

    # Write the highest file content to metadata.json
    with open('metadata.json', 'w', encoding='utf-8') as file:
        json.dump(metadata, file, ensure_ascii=False, indent=4)

    # Iterate over the remaining files in descending order
    for filename in reversed(json_files[:-1]):
        with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
            new_data = json.load(file)
            merge_dicts(metadata, new_data)

        # Update metadata.json
        with open('metadata.json', 'w', encoding='utf-8') as file:
            json.dump(metadata, file, ensure_ascii=False, indent=4)

    print(f"Merged JSON data has been written to metadata.json")

if __name__ == "__main__":
    main()
