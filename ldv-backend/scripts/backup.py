#!/usr/bin/env python3
"""
Backup and Restore utility for Sydeco SQLite database.
Handles online backups, encryption with a separate key, and retention policy.
"""
import os
import sys
import time
import sqlite3
import datetime
import shutil
from cryptography.fernet import Fernet

# Add parent directory to path so we can import config/database
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_backup_dir() -> str:
    backup_dir = os.getenv("LDV_BACKUP_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups"))
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir

def get_backup_key() -> bytes:
    key = os.getenv("LDV_BACKUP_ENCRYPTION_KEY", "").strip()
    if not key:
        if os.getenv("LDV_PRODUCTION") == "1":
            raise ValueError("LDV_BACKUP_ENCRYPTION_KEY must be set in production mode")
        # For development/testing, fallback to a derived key or warning
        print("WARNING: LDV_BACKUP_ENCRYPTION_KEY not set. Using ephemeral/testing key.", file=sys.stderr)
        key = Fernet.generate_key().decode()
    return key.encode()

def run_backup() -> str:
    """Perform online SQLite backup, encrypt it, save to backups/, and run retention cleanup."""
    import database
    
    db_path = database.get_db_path()
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}")

    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d_%H%M%S")
    backup_dir = get_backup_dir()
    
    # Determine frequency category
    # Daily is default.
    # Weekly if Sunday (weekday 6).
    # Monthly if 1st day of month.
    category = "daily"
    if now.day == 1:
        category = "monthly"
    elif now.weekday() == 6: # Sunday
        category = "weekly"
        
    temp_db_path = os.path.join(backup_dir, f"temp_backup_{date_str}.db")
    final_enc_path = os.path.join(backup_dir, f"db_backup_{category}_{date_str}.enc")

    # 1. Perform SQLite Online Backup
    src_conn = sqlite3.connect(db_path)
    dst_conn = sqlite3.connect(temp_db_path)
    try:
        src_conn.backup(dst_conn)
    finally:
        dst_conn.close()
        src_conn.close()

    # 2. Encrypt the backup database file
    key = get_backup_key()
    fernet = Fernet(key)
    with open(temp_db_path, "rb") as f:
        plaintext_data = f.read()
        
    ciphertext = fernet.encrypt(plaintext_data)
    with open(final_enc_path, "wb") as f:
        f.write(ciphertext)
        
    # Clean up unencrypted temp database file
    os.remove(temp_db_path)
    
    print(f"Encrypted backup saved to: {final_enc_path}")
    
    # Write to audit log if possible
    try:
        database.write_audit("backup.create", user_id=None, org_id=None, resource_id=category, detail=final_enc_path)
    except Exception:
        pass
        
    # 3. Apply retention policy
    enforce_retention(backup_dir)
    
    return final_enc_path

def enforce_retention(backup_dir: str):
    """Keep 7 daily, 4 weekly, and 6 monthly backups. Remove older ones."""
    # Find all backup files
    files = [f for f in os.listdir(backup_dir) if f.startswith("db_backup_") and f.endswith(".enc")]
    
    dailies = []
    weeklies = []
    monthlies = []
    
    for f in files:
        path = os.path.join(backup_dir, f)
        if "_daily_" in f:
            dailies.append(path)
        elif "_weekly_" in f:
            weeklies.append(path)
        elif "_monthly_" in f:
            monthlies.append(path)
            
    # Sort oldest first (so we delete from the beginning of the list)
    dailies.sort(key=os.path.getmtime)
    weeklies.sort(key=os.path.getmtime)
    monthlies.sort(key=os.path.getmtime)
    
    # Apply counts
    to_delete = []
    if len(dailies) > 7:
        to_delete.extend(dailies[:-7])
    if len(weeklies) > 4:
        to_delete.extend(weeklies[:-4])
    if len(monthlies) > 6:
        to_delete.extend(monthlies[:-6])
        
    for p in to_delete:
        try:
            os.remove(p)
            print(f"Retention: Deleted old backup {os.path.basename(p)}")
        except Exception as e:
            print(f"Error deleting {p}: {e}", file=sys.stderr)

def run_restore(backup_path: str, target_db_path: str, key_override: bytes = None) -> bool:
    """Decrypt backup file, verify SQLite integrity, and copy to target database path."""
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup file not found at {backup_path}")
        
    key = key_override or get_backup_key()
    fernet = Fernet(key)
    
    with open(backup_path, "rb") as f:
        ciphertext = f.read()
        
    try:
        plaintext_data = fernet.decrypt(ciphertext)
    except Exception as e:
        raise ValueError(f"Decryption failed: check backup encryption key. Error: {e}")
        
    # Write to a temp database file to verify integrity
    temp_restored_path = target_db_path + ".restore_temp"
    with open(temp_restored_path, "wb") as f:
        f.write(plaintext_data)
        
    # Verify Integrity
    try:
        conn = sqlite3.connect(temp_restored_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        status = cursor.fetchone()[0]
        conn.close()
        
        if status != "ok":
            os.remove(temp_restored_path)
            raise ValueError(f"SQLite integrity check failed: {status}")
            
    except Exception as e:
        if os.path.exists(temp_restored_path):
            os.remove(temp_restored_path)
        raise ValueError(f"Integrity check failed: {e}")
        
    # Replace live database with restored database
    # If target already exists, backup the live database file first as a safety precaution
    if os.path.exists(target_db_path):
        shutil.move(target_db_path, target_db_path + ".bak")
        
    try:
        shutil.move(temp_restored_path, target_db_path)
        # Clean up safety backup if all succeeded
        if os.path.exists(target_db_path + ".bak"):
            os.remove(target_db_path + ".bak")
        print(f"Successfully restored database to {target_db_path}")
        return True
    except Exception as e:
        # Rollback safety backup if it failed
        if os.path.exists(target_db_path + ".bak"):
            shutil.move(target_db_path + ".bak", target_db_path)
        raise e

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 backup.py [backup|restore <backup_path> <target_path>]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "backup":
        try:
            run_backup()
            print("Backup completed successfully.")
        except Exception as e:
            print(f"Backup failed: {e}", file=sys.stderr)
            sys.exit(1)
    elif cmd == "restore":
        if len(sys.argv) < 4:
            print("Usage: python3 backup.py restore <backup_path> <target_path>")
            sys.exit(1)
        b_path = sys.argv[2]
        t_path = sys.argv[3]
        try:
            run_restore(b_path, t_path)
            print("Restore completed successfully.")
        except Exception as e:
            print(f"Restore failed: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
