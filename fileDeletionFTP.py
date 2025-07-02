import os
from ftplib import FTP
from datetime import timedelta, datetime

# setting up file
today_date = datetime.now().strftime("%Y-%m-%d")
log_filename = f"ftp_cleanup_{today_date}.log"

# Creating a log file which will show file status
def log(message):
    print(message)
    with open(log_filename, "a") as log_file:
        log_file.write(message + "\n")

# FTP credentials
FTP_HOST = "10.0.0.36"
FTP_USER = "newftpuser"
FTP_PASSWORD = "password123"

if not all([FTP_HOST, FTP_USER, FTP_PASSWORD]):
    log("Error: One or more variables [FTP_HOST, FTP_USER, FTP_PASSWOPD] are not set.")
    exit(1)

# All the directories which files should be removed.

FTP_DIRECTORY = [
    "/FGBOM", "/PRODUCTION", "/SALES", "/SALES_STOCK_REP",
    "/SITE_MASTER", "/STO", "/STO_PENDING", "/VERDIS"
]

daysToKeep = 7
deleted_Date = datetime.now() - timedelta(days=daysToKeep)

# Connect to FTP

try:
    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASSWORD)
    log(f"Connected to server: {FTP_HOST}")
except Exception as conn_err:
    log(f"Connection has been failed: {conn_err}")
    exit(1)

# list the files which you want to delete, i.e. put it in array

delete_files = []

for directory in FTP_DIRECTORY:
    try:
        ftp.cwd(directory)
        log(f"\nScanning directory: {directory}")
        files = ftp.nlst()

        delete_count = 0
        keep_count = 0

        for file in files:
            try:
                size = ftp.size(file)
                if size is None:
                    continue

                mdtm_response = ftp.sendcmd(f"MDTM {file}")
                modified_time_str = mdtm_response[4:].strip()
                modified_time = datetime.strptime(modified_time_str, "%Y%m%d%H%M%S")

                if modified_time < deleted_Date:
                    log(f"Will delete: {file} (Last Modified: {modified_time})")
                    delete_files.append((directory, file))
                    delete_count += 1
                else:
                    log(f"Keeping: {file} (Last Modified: {modified_time})")
                    keep_count += 1

            except Exception as file_err:
                log(f"Error checking file {file}: {file_err}")

            log(f"Summary for {directory}: {delete_count} file(s) to delete, {keep_count} file(s) to keep")

    except Exception as dir_err:
        log(f"Error accessing directory {directory}: {dir_err}")

# Deletion of files

log("\nStarting deletion of old files...\n")
for directory, file in delete_files:
    try:
        ftp.cwd(directory)
        ftp.delete(file)
        log(f"Deleted: {file} from {directory}")
    except Exception as delete_err:
        log(f"Error deleting file {file} from {directory}: {delete_err}")

# Close the FTP connection
ftp.quit()
log("FTP connection closed.") 
  