import os
import sys
import tempfile
import sqlite3
from cryptography.fernet import Fernet

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scripts.backup as backup_module

def test_backup_restore_cycle():
    # 1. Setup temporary directories and files
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_live.db")
        backup_dir = os.path.join(tmpdir, "backups")
        restore_target_path = os.path.join(tmpdir, "test_restored.db")
        
        os.environ["LDV_DB_PATH"] = db_path
        os.environ["LDV_BACKUP_DIR"] = backup_dir
        
        # Generate a test backup key
        backup_key = Fernet.generate_key()
        os.environ["LDV_BACKUP_ENCRYPTION_KEY"] = backup_key.decode()
        
        # 2. Create initial database and insert mock data
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT)")
        conn.execute("INSERT INTO users (email) VALUES ('test@example.com')")
        conn.commit()
        conn.close()
        
        # Verify it works
        conn = sqlite3.connect(db_path)
        assert conn.execute("SELECT email FROM users").fetchone()[0] == "test@example.com"
        conn.close()
        
        # 3. Perform backup
        backup_file = backup_module.run_backup()
        assert os.path.exists(backup_file)
        
        # Verify that backup file is encrypted (should not open as SQLite)
        try:
            conn = sqlite3.connect(backup_file)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sqlite_master")
            cursor.fetchall()
            conn.close()
            assert False, "Encrypted backup file should not be a valid SQLite database"
        except sqlite3.DatabaseError:
            pass # Expected
            
        # 4. Modify live database (e.g. simulate data loss or corruption)
        conn = sqlite3.connect(db_path)
        conn.execute("DELETE FROM users")
        conn.commit()
        assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
        conn.close()
        
        # 5. Restore backup to a new target database path
        success = backup_module.run_restore(backup_file, restore_target_path)
        assert success
        assert os.path.exists(restore_target_path)
        
        # 6. Verify restored database has the original data
        conn_restored = sqlite3.connect(restore_target_path)
        row = conn_restored.execute("SELECT email FROM users").fetchone()
        assert row is not None
        assert row[0] == "test@example.com"
        conn_restored.close()
        
        print("Backup and restore test PASSED.")

if __name__ == "__main__":
    test_backup_restore_cycle()
