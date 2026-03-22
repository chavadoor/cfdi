import os
import bz2
import urllib.request
import frappe
import sqlite3

CATALOGS_URL = "https://github.com/phpcfdi/resources-sat-catalogs/releases/latest/download/catalogs.db.bz2"

def get_catalogs_db_path():
    """Returns the local path to the SQLite catalogs database, downloading it if necessary."""
    site_path = frappe.get_site_path()
    db_dir = os.path.join(site_path, "private", "files", "sat_catalogs")
    
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    db_path = os.path.join(db_dir, "catalogs.db")
    
    if not os.path.exists(db_path):
        download_and_extract_catalogs(db_path)
        
    return db_path

def download_and_extract_catalogs(destination_path):
    """Downloads the bz2 compressed SQLite DB and extracts it."""
    bz2_path = destination_path + ".bz2"
    
    frappe.logger().info(f"Downloading SAT catalogs from {CATALOGS_URL}")
    try:
        urllib.request.urlretrieve(CATALOGS_URL, bz2_path)
    except Exception as e:
        frappe.log_error(f"Failed to download SAT catalogs: {e}")
        raise
        
    frappe.logger().info("Extracting SAT catalogs database...")
    try:
        with bz2.BZ2File(bz2_path, 'rb') as source, open(destination_path, 'wb') as dest:
            for data in iter(lambda: source.read(100 * 1024), b''):
                dest.write(data)
    except Exception as e:
        frappe.log_error(f"Failed to extract SAT catalogs: {e}")
        raise
    finally:
        if os.path.exists(bz2_path):
            os.remove(bz2_path)
            
    frappe.logger().info("SAT catalogs database downloaded and extracted successfully.")

def get_sqlite_connection():
    """Returns a sqlite3 connection to the SAT catalogs database."""
    db_path = get_catalogs_db_path()
    return sqlite3.connect(db_path)
