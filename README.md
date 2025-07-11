# Mint DOI for Open Repository
Created by Tess Grynoch and Lisa Palmer

Script for minting a draft DOI with the DataCite API using metadata from an Open Repository instance (**DSpace 7**) via the Open Repository API. To use this version of the script, you can clone this repository or download the source code from the most recent release.

To access the **DSpace 5** version of this script, please see the [DSpace 5 branch](https://github.com/grynoch/mintDOI4OpenRepository/tree/DSpace5) or [DSpace 5 release](https://github.com/grynoch/mintDOI4OpenRepository/releases/tag/v1.0.0).

## Requirements:
- Python 3 (with json, requests, and re libraries)
- Administrative access to the item(s) in Open Repository you want to create DOIs for
- Username and password for a DataCite account associated with the repository you are minting DOIs for

## Inputs:
We have tried to generalize this version of the script as much as possible so it can have broader applications. We've left many variables as inputs which you can update in the script if you do not want to input them every time. The only input we use in the UMass Chan version of the script is the item ID.

- repository = Repository url (ex. https://repository.escholarship.umassmed.edu)
- item = Item ID located on the edit page of an item
- affiliationName = Institutional affiliation for authors. Assumes all authors are affiliated with the same institution. Authors who are not affiliated with the institution need to have their affiliation manually updated in the DataCite record. (ex. University of Massachusetts Chan Medical School)
- affiliationRORID = Affiliation ROR ID. Get from [https://ror.org/](https://ror.org/). (ex. https://ror.org/0464eyp60)
- `data3["prefix"]` = DOI prefix for repository
- authorization = Authorization key from [https://support.datacite.org/reference/post_dois](https://support.datacite.org/reference/post_dois)

## Metadata Fields
Depending on the fields in your Open Repository instance and what fields you would like to import into your DataCite metadata, you may need to edit the code, comment out fields you do not use, or add fields you wish to import into your DataCite metadata. All edits would take place in step 3.

Open Repository metadata fields used in this script:
- dc.contributor.author
- dc.identifier.orcid
- dc.date.issued
- dc.description.abstract
- dc.identifier.uri
- dc.publisher
- dc.title
- dc.type

Following DataCite fields are considered the same across all items and added through the script:
- language = en
- lang for description = en
- descriptionType = Abstract
- affiliation name
- affiliationIdentifier
- affiliationIdentifierScheme = ROR
- affiliation schemeUri = https://ror.org

## Output Files:
- item.json = edited JSON from Open Repository.
- DataCiteUpload.json = JSON file uploaded to DataCite.
- DataCiteDoiMetadata.json = JSON response from DataCite after posting new draft DOI.
- newdoiReminder_#####.txt = Text file with new draft DOI to add to the Open Repository item and make the DOI findable, handle of the item, and any ORCIDs that needed to be added to the DataCite metadata if there were multiple authors. File name has item number at the end to help keep track of files if you are minting a number of DOIs in a batch.

## Notes: 
We recommend creating test DOIs on the DataCite testing server first to make sure the metadata is being uploaded correctly. When you're ready to create DOIs on the DataCite production server, change the url in step 4 to "https://api.datacite.org/dois" and use your assigned prefix for the production server.

This script can also be modified to make the DOI findable when the metadata is first uploaded to DataCite by including the attribute "event" with value "publish" in the payload (DataCiteUpload.json) before the prefix field.

For more information about minting DOIs using the DataCite API visit [DataCite's developer documentation](https://support.datacite.org/docs/api-create-dois).

For the Open Repository (DSpace) REST API:
**For DSpace 7**, put a /server/#/server/api after your repository url to be directed to the HAL Browser and view the [DSpace 7 REST API documentation on GitHub](https://github.com/DSpace/RestContract/blob/main/README.md).

**For DSpace 5**, put a /rest after your repository url to be directed to the correct page.

## License
Licensed under MIT License.
