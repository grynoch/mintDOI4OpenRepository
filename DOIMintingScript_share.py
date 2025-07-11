# -*- coding: utf-8 -*-
"""
Created on Tues Dec 03 2024

@author: Tess Grynoch and Lisa Palmer

License: MIT License 
"""
#Load Libraries
import json
import requests #APIs
import re #regular expressions

#%%

#Input your Open Respository url. 
#If you do not want to submit your repository url each time, paste you url in quotes after the equal symbol. 
repository = input("Repository url (ex. https://repository.escholarship.umassmed.edu)")

#Input the item ID located on edit page of item
item = input("Item ID:") 

# 1.	Pull in data for individual record from Open Repository REST API
itemurl = repository + "/server/api/core/items/"+ item
response = requests.get(itemurl)
#print(response.json()) #For testing purposes to check what data is pulled from the repository

# 2. Edit JSON to display in standard key: value pairs
#Extract metadata element which houses all pertinent information
metadata = data["metadata"]

#Convert list to JSON format and print JSON for easier viewing.
def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

jprint(metadata)

#Turn JSON into variable data
data = json.dumps(response.json(), sort_keys=True, indent=4)

#Remove language, authority, confidence, and places child keys from JSON
#For elements that only have a single value
keysneeded = ["dc.date.issued","dc.description.abstract", "dc.identifier.uri","dc.publisher", "dc.title","dc.type"]
singles = {key: metadata[key] for key in keysneeded}

singles2 = {} #create empty dictionary for them to go in
#pair key with text from value 
for key, value in singles.items():
    x=value[0]
    for inner_key, inner_value in x.items():
        if inner_key == "value":
            singles2[key]= inner_value
            
#For elements that have multiple values (authors and orcids)
#For records with multiple authors - create a dictionary for authors called creators early and iterate on the values
#Determine the number of authors by calculating the length of (number of elements in) "dc.contributor.author"
authorcount = len(metadata["dc.contributor.author"])

#create a vector with author numbers to pull from for numbering
authornumbers = list(map(str, (list(range(1,authorcount+1)))))

#if there is a single author we can treat it as an element with a single value
authors = {}
if authorcount == 1:
    for key, value in metadata["dc.contributor.author"][0].items():
        if key == "value":
            authors["dc.contributor.author"]= value
            
#replace each dc.contributor.author with dc.contributor.author# with the number
# being the author order #test out when we have multiple authors
if authorcount > 1 :
    for i in authornumbers:
        x= int(i) - 1
        for key, value in metadata["dc.contributor.author"][x].items():
            if key == "value":
                authors["dc.contributor.author"+i]= value
                
# Create list of dc.contributor.author keys based on author count
dcauthorkeys = []
if authorcount > 1 :
    for i in authornumbers:
        dcauthorkeys.append("dc.contributor.author" + i)
else:
    dcauthorkeys.append("dc.contributor.author")

#Solution for multiple orcids #not yet tested on multi-author record
#if there is a single orcid id we can treat it as an element with a single value

if "dc.identifier.orcid" in metadata.keys():
    orcid = {}
    if authorcount == 1:
        for key, value in metadata["dc.identifier.orcid"][0].items():
            if key == "value":
                orcid["dc.identifier.orcid"]= value        
    if authorcount > 1 :
        PrintORCIDs = re.findall(r'\d\d\d\d-\d\d\d\d-\d\d\d\d-\d\d\d\d', json.dumps(metadata))

#merge singles, authors, and orcid dictionaries together
# define function to combine two dictionaries
def Merge(dict1, dict2):
  for i in dict2.keys():
      dict1[i]=dict2[i]
  return dict1

doimetadata = Merge(singles2, authors)
if authorcount==1 and "dc.identifier.orcid" in metadata.keys():
    doimetadata = Merge(doimetadata, orcid)

# 3. Transform relevant JSON fields to DataCite JSON standards 
    
#transform is the function to add a parent level to the dictionary using an 
# existing key in the dictionary
def transform(dct, affected_keys):
    new_dct = dct.copy()
    for new_key, keys in affected_keys.items():
        new_dct[new_key] = {key: new_dct.pop(key) for key in keys}
    return new_dct

  data2 = doimetadata
  
#Select only the fields needed for DataCite metadata
#Create dictionary for authors
authors = {key:{key: data2[key]} for key in dcauthorkeys}
for i in dcauthorkeys:
    field = authors[i].pop(i)
    authors[i]["name"] = field
authors = transform(authors, {"creators": dcauthorkeys})
#Create dictionary for all other fields taking into account items 
# without an orcid and/or items with multiple authors 
if ('dc.identifier.orcid' in data2.keys() and authorcount == 1):
    data2 = {key: data2[key] for key in data2.keys() 
             & {'dc.date.issued','dc.description.abstract',
                'dc.identifier.uri','dc.publisher','dc.title',
                'dc.type','dc.identifier.orcid'}}
else: 
  data2 = {key: data2[key] for key in data2.keys() 
       & {'dc.date.issued','dc.description.abstract',
          'dc.identifier.uri','dc.publisher','dc.title',
          'dc.type'}} 
#Combine the two dictionaries using Merge function defined below 
def Merge(dict1, dict2):
  for i in dict2.keys():
      dict1[i]=dict2[i]
  return dict1
data2 = Merge(authors, data2) 

#Rename keys to DataCite keys and add consistent fields 
field = data2.pop("dc.publisher")
data2["publisher"] = field
field = data2.pop("dc.title")
data2["title"] = field
field = data2.pop("dc.date.issued")
data2["publicationYear"] = field
field = data2.pop("dc.description.abstract")
data2["description"] = field
field = data2.pop("dc.identifier.uri")
data2["url"] = field
#create language field and set to English
data2["language"] = "en"
field = data2.pop("dc.type")
data2["resourceTypeGeneral"] = field
if 'dc.identifier.orcid' in data2.keys():
    field = data2.pop("dc.identifier.orcid")
    data2["nameIdentifier"] = field
#set language field for abstract to English and descriptionType as abstract
data2["lang"] = "en"
data2["descriptionType"] = "Abstract"
#Update publication year from a full date in ISO to just year
year = data2["publicationYear"]
data2["publicationYear"] = year[0:4]
#Create url from handle
handle = data2["url"].split('/')
handle = "https://repository.escholarship.umassmed.edu/handle/20.500.14038/" + handle[4]
data2["url"] = handle
#print(data2)

#%%
#Update author info. Differentiate personal and organizational names and
# split personal names into given name and family name 
#Personal authors are identified as having a comma and corporate authors as non-comma
for i in dcauthorkeys:
    if "," in data2["creators"][i]["name"]:
        data2["creators"][i]["nameType"] = "Personal"
        fullname = data2["creators"][i]["name"].split(', ')
        data2["creators"][i]["givenName"] = fullname[1]
        data2["creators"][i]["familyName"] = fullname[0]  
    else:
        data2["creators"][i]["nameType"] = "Organizational"
        data2["creators"][i]["givenName"] = ""
        data2["creators"][i]["familyName"] = ""
#print(data2)

#%%
#Map document types to resourceTypeGeneral and resourceType
#Removing resource type for Dataset, Preprint, and report because they
#are redundant
#Everything else in given the general type of Text
data2["resourceType"] = data2["resourceTypeGeneral"]

if data2["resourceTypeGeneral"] == "Doctoral Dissertation":
    data2["resourceTypeGeneral"] = "Dissertation"
elif data2["resourceTypeGeneral"] == "Master's Thesis":
    data2["resourceTypeGeneral"] = "Dissertation"
elif data2["resourceTypeGeneral"] == "Newsletter":
    data2["resourceTypeGeneral"] = "Text"
elif data2["resourceTypeGeneral"] == "Poster":
    data2["resourceType"] = "Conference Poster"
    data2["resourceTypeGeneral"] = "Text"
elif data2["resourceTypeGeneral"] == "Presentation":
    data2["resourceType"] = "Conference Presentation"
    data2["resourceTypeGeneral"] = "Text"
elif data2["resourceTypeGeneral"] == "Other":
    data2["resourceTypeGeneral"] = "Text"
elif data2["resourceTypeGeneral"] == "Podcast":
    data2["resourceType"] = "Podcast"
    data2["resourceTypeGeneral"] = "Sound"
elif data2["resourceTypeGeneral"] == "Video":
    data2["resourceType"] = "Video"
    data2["resourceTypeGeneral"] = "Audiovisual"
elif data2["resourceType"] == "Dataset": 
    data2.pop("resourceType")
elif data2["resourceType"] == "Preprint":
    data2.pop("resourceType")
elif data2["resourceType"] == "Report":
    data2.pop("resourceType")
else: data2["resourceTypeGeneral"] = "Text"

#%%
#Add parent values and order to create structure of final json file for upload to DataCite
data3 = data2
data3 = transform(data3, {"titles":["title"]})
data3 = transform(data3, {"descriptions":["lang","description","descriptionType"]})
if 'resourceType' in data3.keys():
    data3 = transform(data3, {"types":["resourceType", "resourceTypeGeneral"]})
else:
    data3 = transform(data3, {"types":["resourceTypeGeneral"]})
  
#Create affiliation dictionary and append
#Assumes all authors are affiliated with the same institution
#Authors who are not affiliated with the institution need to have their affiliation manually updated in the DataCite record
affiliationName = input("Institutional affiliation for authors. Assumes all authors are affiliated with the same institution. Authors who are not affiliated with the institution need to have their affiliation manually updated in the DataCite record")
affiliationRORID = input("Affiliation ROR ID. Get from https://ror.org/. (ex. https://ror.org/0464eyp60)")
affiliation = {"affiliation": {
                        "affiliationIdentifier": affiliationRORID,
                        "affiliationIdentifierScheme": "ROR",
                        "name": affiliationName,
                        "schemeUri": "https://ror.org/"
                    }}
for i in dcauthorkeys:
    data3["creators"][i] = Merge(data3["creators"][i], affiliation)

#Add ORCID to creator if applicable
if 'nameIdentifier' in data3.keys():
    orcidurl = "https://orcid.org/" + data2["nameIdentifier"]
    orcid = {"nameIdentifiers": {
                                "schemeUri": "https://orcid.org",
                                "nameIdentifier": orcidurl,
                                "nameIdentifierScheme": "ORCID"}}  
    data3["creators"]["dc.contributor.author"] = Merge(data3["creators"]["dc.contributor.author"], orcid)
    del data3["nameIdentifier"]

#Remove creator group keys  
data3["creators"] = [data3["creators"].pop(key) for key in dcauthorkeys]

#Add type and prefix
data3["type"] = "dois"
#Test prefix #Use production prefix when ready to mint draft DOIs on the production server
data3["prefix"] = input("DOI prefix for repository")
data3 = transform(data3, {"attributes":["prefix","creators","titles","publisher",
                                        "publicationYear","language","types",
                                        "descriptions","url"]})
#Make data the first key
data3 = transform(data3, {"data":["type","attributes"]})
#print(data5)

#%%
#Write JSON file called DataCiteUpload
data3json = json.dumps(data3, indent = 4)
with open('DataCiteUpload.json', 'w') as file:

    # write
    file.write(data3json)
#%%
# 4. Use DataCite REST API to mint Draft DOI
data4 = open('DataCiteUpload.json')

# url for testing server
url = "https://api.test.datacite.org/dois"
# url for production server
# url = "https://api.datacite.org/dois"

authorization = input("Authorization key from https://support.datacite.org/reference/post_dois")

payload = data4.read()
headers = {"content-type": "application/json",
    "authorization": authorization
}

response = requests.post(url, data=payload, headers=headers)

print(response.text)

#%%
#Save the json to check the response
with open('DataCiteDoiMetadata.json', 'w') as file:

    # write
    file.write(response.text)
    
#%%
# 5. Pull DataCite DOI for item using DataCite REST API response
#Start with DataCiteDoiMetadata.json which was the response.text
with open('DataCiteDoiMetadata.json','r') as file:
  # read JSON data
  data5 = json.load(file)
  newdoi = data5["data"]["id"] #new doi variable to upload to Open Repository 
  handle = data5["data"]["attributes"]["url"] #url for item in Open Repository

#Print reminder text in Python and save as text file with item id
if (authorcount > 1 and 'dc.identifier.orcid' in dataedit):
    print("Add " + newdoi + " to " + handle + "and add the following ORCID iD(s) to their corresponding author(s): " + ', '.join(map(str, PrintORCIDs))) 
else:
    print("Add " + newdoi + " to " + handle)
if (authorcount > 1 and 'dc.identifier.orcid' in dataedit):
    Reminder = "Add " + newdoi + " to " + handle + "and add the following ORCID iD(s) to their corresponding author(s): " + ', '.join(map(str, PrintORCIDs))
else:
    Reminder = "Add " + newdoi + " to " + handle
ReminderFileName = "newdoiReminder_" + item + ".txt" 
with open(ReminderFileName, 'w') as file:
    file.write(Reminder)

