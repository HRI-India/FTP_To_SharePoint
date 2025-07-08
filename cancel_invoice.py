import os
from ftplib import FTP
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
from datetime import datetime

# === FTP Configuration ===
ftp_host = '10.1.0.37'
ftp_username = 'azureuser'
ftp_password = 'Ejqkut9p7b!'
ftp_remote_path = '/sap_auto/cancel_invoice'

# === SharePoint Configuration ===
sharepoint_site_url = 'https://hygienic.sharepoint.com/sites/SAPReportViews'
sharepoint_username = 'shrishti@hriindia.com'
sharepoint_password = 'S@04122000'
library_name = "Shared Documents"
folder_root = "SAP Reports"  # Folder inside "Shared Documents"

# === Local Download Path ===
local_download_path = 'downloads'
os.makedirs(local_download_path, exist_ok=True)

# === Step 1: Connect to FTP and Get Latest File ===
ftp = FTP(ftp_host)
ftp.login(ftp_username, ftp_password)
ftp.cwd(ftp_remote_path)

files = []

def collect_file_info(line):
    parts = line.split(maxsplit=8)
    if len(parts) == 9 and parts[0].startswith('-'):
        name = parts[8]
        try:
            date_str = f"{parts[5]} {parts[6]} {parts[7]}"
            file_date = datetime.strptime(date_str, "%b %d %H:%M").replace(year=datetime.now().year)
        except:
            file_date = datetime.now()
        files.append((name, file_date))

ftp.retrlines('LIST', callback=collect_file_info)
ftp.quit()

if not files:
    exit("No files found on FTP server.")

files.sort(key=lambda x: x[1], reverse=True)
latest_file, latest_date = files[0]
print(f"Latest file found: {latest_file} on {latest_date}")

local_file_path = os.path.join(local_download_path, latest_file)
with open(local_file_path, 'wb') as f:
    ftp = FTP(ftp_host)
    ftp.login(ftp_username, ftp_password)
    ftp.cwd(ftp_remote_path)
    ftp.retrbinary(f'RETR {latest_file}', f.write)
    ftp.quit()

# === SharePoint Helper ===
def create_folder_if_not_exists(ctx, parent_url, folder_name):
    try:
        folder = ctx.web.get_folder_by_server_relative_url(parent_url)
        ctx.load(folder.folders)
        ctx.execute_query()
    except Exception as e:
        print(f"Error accessing folder '{parent_url}': {e}")
        return None

    existing_folders = [f.properties["Name"] for f in folder.folders]
    if folder_name not in existing_folders:
        try:
            print(f"Creating folder '{folder_name}' under '{parent_url}'...")
            folder.folders.add(folder_name)
            ctx.execute_query()
        except Exception as e:
            print(f"Error creating folder '{folder_name}': {e}")
            return None

    return f"{parent_url}/{folder_name}"

# === Step 2: Upload to SharePoint ===
month_folder = latest_date.strftime("%B")   # e.g., July
year_folder = latest_date.strftime("%Y")    # e.g., 2025

ctx_auth = AuthenticationContext(sharepoint_site_url)
if ctx_auth.acquire_token_for_user(sharepoint_username, sharepoint_password):
    ctx = ClientContext(sharepoint_site_url, ctx_auth)

    # Base path: library root + custom folder
    base_path = f"/sites/SAPReportViews/{library_name}/{folder_root}"

    # Create Year folder
    year_path = create_folder_if_not_exists(ctx, base_path, year_folder)
    if not year_path:
        exit("Failed to ensure year folder.")

    # Create Month folder
    month_path = create_folder_if_not_exists(ctx, year_path, month_folder)
    if not month_path:
        exit("Failed to ensure month folder.")

    # Upload the file
    upload_folder = ctx.web.get_folder_by_server_relative_url(month_path)
    with open(local_file_path, 'rb') as file_content:
        upload_folder.upload_file(latest_file, file_content.read()).execute_query()

    print(f"Uploaded '{latest_file}' to SharePoint folder: {month_path}")
else:
    print("Failed to authenticate to SharePoint.")