import os
from ftplib import FTP
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
from datetime import datetime, timedelta

# FTP (File Transfer Protocol)
ftp_host = '10.1.0.37'
ftp_username = 'azureuser'
ftp_password = 'Ejqkut9p7b!'
ftp_remote_path = '/sap_auto/cust_brand_wise'

# SharePoint teams

sharepoint_site_url = 'https://hygienic.sharepoint.com/sites/SAPReportViews'
sharepoint_username = 'shrishti@hriindia.com'
sharepoint_password = 'S@04122000'
sharepoint_folder_url = '/sites/SAPReportViews/Shared Documents/cust_brand_wise_report'

local_download_path = 'downloads'
os.makedirs(local_download_path, exist_ok=True)

ftp = FTP(ftp_host)
ftp.login(ftp_username, ftp_password)
ftp.cwd(ftp_remote_path)

print("Files in FTP directory (recent only):")
files = []

def collect_file_info(line):
    parts = line.split(maxsplit = 8)
    if(len(parts) == 9 and parts[0].startswith('-')):
        name = parts[8]
        try:
            date_str = f"{parts[5]} {parts[6]} {parts[7]}"
            file_date = datetime.strptime(date_str, "%b %d %H:%M")  # fallback
            # If year not in line, we assume it's this year
            file_date = file_date.replace(year=datetime.now().year)
        except:
            file_date = datetime.now()  # fallback to now if parsing fails
        files.append((name, file_date))

ftp.retrlines('LIST', callback=collect_file_info)

# Sort files by date and pick the latest one
files.sort(key=lambda x: x[1], reverse=True)
latest_file, latest_date = files[0]
print(f"\n Latest file: {latest_file} (Modified: {latest_date})")

# Download the latest file
print('\n Downloading the latest Files')
local_file_path = os.path.join(local_download_path, latest_file)
with open(local_file_path, 'wb') as f:
    ftp.retrbinary(f'RETR {latest_file}', f.write)
    print(f"    -Downloaded: {latest_file}")

ftp.quit()

print('\n Uploading files to Sharepoint')
ctx_auth = AuthenticationContext(sharepoint_site_url)
if ctx_auth.acquire_token_for_user(sharepoint_username, sharepoint_password):
    ctx = ClientContext(sharepoint_site_url, ctx_auth)

    with open(local_file_path, 'rb') as file_content:
        target_folder = ctx.web.get_folder_by_server_relative_url(sharepoint_folder_url)
        target_file = target_folder.upload_file(latest_file, file_content.read())
        ctx.execute_query()

        print(f"    -Uploaded {latest_file}")

else:
    print("Sharepoint authentication failed.")