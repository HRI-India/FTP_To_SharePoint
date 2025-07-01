# FTP to SharePoint File Transfer Script

FTP - File Transfer Protocol in which files are transferred automatically between two server.
This Python script automates the process of downloading files from an FTP server and uploading them to a specific folder in a SharePoint or Microsoft Teams site.

## Features

- Connects to a secure FTP server
- Lists and downloads files to a local folder
- Authenticates and uploads the files to a SharePoint or Teams document library
- Displays status messages for each step

## Requirements

- Python 3.6 or higher
- Required Python packages:
  - `office365-rest-python-client` (for SharePoint operations)

### Install dependencies:
```bash
pip install office365-rest-python-client
