import os
from ftplib import FTP
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext

# FTP (File Transfer Protocol)
ftp_host = '10.1.0.37'
ftp_username = 'azureuser'
ftp_password = ' '
ftp_remote_path = '/sap_auto/daily_collection'

# SharePoint teams

sharepoint_site_url = 'https://hygienic.sharepoint.com/sites/DataWarehouse'
sharepoint_username = 'shrishti@hriindia.com'
sharepoint_password = ' '
sharepoint_folder_url = '/sites/DataWarehouse/Shared Documents/Data Warehouse Discussions'

local_download_path = 'downloads'
os.makedirs(local_download_path, exist_ok=True)

ftp = FTP(ftp_host)
ftp.login(ftp_username, ftp_password)
ftp.cwd(ftp_remote_path)

print("Files in FTP directory:")
files = []

def collect_file_info(line):
    parts = line.split(maxsplit = 8)
    if(len(parts) == 9 and parts[0].startswith('-')):
        size = int(parts[4])
        name = parts[8]
        files.append((name, size))
        size_kb = round(size/1024, 2)
        print(f"   • {name} ({size_kb} KB)")

ftp.retrlines('LIST', callback=collect_file_info)

print('\n Downloading Files')
for name, size in files:
    local_file_path = os.path.join(local_download_path, name)
    with open(local_file_path, 'wb') as f:
        ftp.retrbinary(f'RETR {name}', f.write)
        print(f"    -Downloaded: {name}")

ftp.quit()

print('\n Uploading files to Sharepoint')
ctx_auth = AuthenticationContext(sharepoint_site_url)
if ctx_auth.acquire_token_for_user(sharepoint_username, sharepoint_password):
    ctx = ClientContext(sharepoint_site_url, ctx_auth)

    for name in os.listdir(local_download_path):
        local_file_path = os.path.join(local_download_path, name)
        with open(local_file_path, 'rb') as file_content:
            target_folder = ctx.web.get_folder_by_server_relative_url(sharepoint_folder_url)
            target_file = target_folder.upload_file(name, file_content.read())
            ctx.execute_query()

            print(f"    -Uploaded {name}")

else:
    print("Sharepoint authentication failed.")