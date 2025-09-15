
import sqlite3
import shutil
import os
from datetime import datetime

def auto_backup_database():
    """Automatisches Backup vor kritischen Operationen"""
    if not os.path.exists("nfl_pickem.db"):
        return None
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "db_backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    backup_path = f"{backup_dir}/nfl_pickem_backup_{timestamp}.db"
    shutil.copy2("nfl_pickem.db", backup_path)
    
    # Nur die letzten 10 Backups behalten
    backups = sorted([f for f in os.listdir(backup_dir) if f.endswith(".db")])
    while len(backups) > 10:
        oldest = backups.pop(0)
        os.remove(f"{backup_dir}/{oldest}")
    
    return backup_path

# Integration in Flask App
def safe_database_operation(operation_func):
    """Wrapper für sichere Datenbank-Operationen"""
    backup_path = auto_backup_database()
    try:
        result = operation_func()
        return result
    except Exception as e:
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, "nfl_pickem.db")
            print(f"❌ Error occurred, database restored from {backup_path}")
        raise e
