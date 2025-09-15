"""
NFL PickEm Database Sync Client
Client script to fetch and synchronize database from live application
"""

import requests
import json
import sqlite3
import os
from datetime import datetime
import tempfile
import zipfile

class DatabaseSyncClient:
    """Client for synchronizing with live NFL PickEm database"""
    
    def __init__(self, base_url: str = "https://nfl-pickem-2025-v2.onrender.com"):
        self.base_url = base_url.rstrip('/')
        self.local_db_path = 'instance/nfl_pickem.db'
        
    def get_database_status(self) -> dict:
        """Get status of the live database"""
        try:
            response = requests.get(f"{self.base_url}/api/database/status", timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to get database status: {e}")
            return {}
    
    def export_database_json(self) -> dict:
        """Export complete database as JSON"""
        try:
            print("📡 Fetching database export from live application...")
            response = requests.get(f"{self.base_url}/api/database/export", timeout=60)
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ Database export successful (exported at {data.get('export_timestamp')})")
            return data
        except Exception as e:
            print(f"❌ Failed to export database: {e}")
            return {}
    
    def download_database_file(self, save_path: str = None) -> str:
        """Download the database file directly"""
        try:
            if save_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"nfl_pickem_live_{timestamp}.db"
            
            print("📥 Downloading database file from live application...")
            response = requests.get(f"{self.base_url}/api/database/download", timeout=60)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Database downloaded to: {save_path}")
            return save_path
        except Exception as e:
            print(f"❌ Failed to download database: {e}")
            return ""
    
    def get_picks_summary(self) -> dict:
        """Get summary of all picks by week"""
        try:
            response = requests.get(f"{self.base_url}/api/database/picks/summary", timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to get picks summary: {e}")
            return {}
    
    def sync_local_database(self) -> bool:
        """Synchronize local database with live data"""
        try:
            # Get live database export
            export_data = self.export_database_json()
            if not export_data:
                return False
            
            # Ensure local directory exists
            os.makedirs('instance', exist_ok=True)
            
            # Create backup of current local database
            if os.path.exists(self.local_db_path):
                backup_path = f"{self.local_db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.local_db_path, backup_path)
                print(f"📦 Local database backed up to: {backup_path}")
            
            # Create new database from export
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            # Recreate tables and data
            tables = export_data.get('tables', {})
            
            for table_name, rows in tables.items():
                if not rows:
                    continue
                
                # Get column names from first row
                columns = list(rows[0].keys())
                
                # Create table (simplified - assumes standard structure)
                if table_name == 'user':
                    cursor.execute('''
                        CREATE TABLE user (
                            id INTEGER PRIMARY KEY,
                            username TEXT NOT NULL,
                            password TEXT NOT NULL
                        )
                    ''')
                elif table_name == 'team':
                    cursor.execute('''
                        CREATE TABLE team (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            abbreviation TEXT,
                            logo_url TEXT
                        )
                    ''')
                elif table_name == 'match':
                    cursor.execute('''
                        CREATE TABLE match (
                            id INTEGER PRIMARY KEY,
                            week INTEGER NOT NULL,
                            away_team_id INTEGER,
                            home_team_id INTEGER,
                            start_time TEXT,
                            away_score INTEGER,
                            home_score INTEGER,
                            is_finished BOOLEAN,
                            FOREIGN KEY (away_team_id) REFERENCES team (id),
                            FOREIGN KEY (home_team_id) REFERENCES team (id)
                        )
                    ''')
                elif table_name == 'pick':
                    cursor.execute('''
                        CREATE TABLE pick (
                            id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            match_id INTEGER,
                            chosen_team_id INTEGER,
                            FOREIGN KEY (user_id) REFERENCES user (id),
                            FOREIGN KEY (match_id) REFERENCES match (id),
                            FOREIGN KEY (chosen_team_id) REFERENCES team (id)
                        )
                    ''')
                elif table_name == 'eliminated_team':
                    cursor.execute('''
                        CREATE TABLE eliminated_team (
                            id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            team_id INTEGER,
                            elimination_type TEXT,
                            FOREIGN KEY (user_id) REFERENCES user (id),
                            FOREIGN KEY (team_id) REFERENCES team (id)
                        )
                    ''')
                elif table_name == 'team_winner_usage':
                    cursor.execute('''
                        CREATE TABLE team_winner_usage (
                            id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            team_id INTEGER,
                            usage_count INTEGER,
                            FOREIGN KEY (user_id) REFERENCES user (id),
                            FOREIGN KEY (team_id) REFERENCES team (id)
                        )
                    ''')
                
                # Insert data
                placeholders = ', '.join(['?' for _ in columns])
                for row in rows:
                    values = [row[col] for col in columns]
                    cursor.execute(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})", values)
            
            conn.commit()
            conn.close()
            
            print(f"✅ Local database synchronized successfully!")
            print(f"📊 Synced {len(tables)} tables with {sum(len(rows) for rows in tables.values())} total records")
            return True
            
        except Exception as e:
            print(f"❌ Database synchronization failed: {e}")
            return False
    
    def print_status_report(self):
        """Print a comprehensive status report"""
        print("=" * 60)
        print("🏈 NFL PICKEM DATABASE SYNC REPORT")
        print("=" * 60)
        
        # Get live status
        status = self.get_database_status()
        if status:
            print(f"📡 Live Database Status: {status.get('status', 'unknown')}")
            print(f"📅 Last Modified: {status.get('last_modified', 'unknown')}")
            print(f"💾 File Size: {status.get('file_size_mb', 0)} MB")
            print(f"📊 Current Week: {status.get('current_week', 0)}")
            print(f"🗓️ Weeks Available: {status.get('weeks_available', 0)}")
            print(f"🎯 Current Week Picks: {status.get('current_week_picks', 0)}")
            
            stats = status.get('statistics', {})
            print(f"👥 Users: {stats.get('user_count', 0)}")
            print(f"🏈 Teams: {stats.get('team_count', 0)}")
            print(f"🎮 Matches: {stats.get('match_count', 0)}")
            print(f"🎯 Picks: {stats.get('pick_count', 0)}")
            print(f"❌ Eliminations: {stats.get('eliminated_team_count', 0)}")
        
        # Get picks summary
        picks = self.get_picks_summary()
        if picks:
            print(f"\\n📈 Total Picks: {picks.get('total_picks', 0)}")
            picks_by_week = picks.get('picks_by_week', {})
            for week in sorted(picks_by_week.keys()):
                week_picks = picks_by_week[week]
                print(f"   Week {week}: {len(week_picks)} picks")
        
        print("=" * 60)

def main():
    """Main function for command-line usage"""
    import sys
    
    client = DatabaseSyncClient()
    
    if len(sys.argv) < 2:
        print("Usage: python database_sync_client.py [status|sync|download|picks]")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'status':
        client.print_status_report()
    elif command == 'sync':
        success = client.sync_local_database()
        if success:
            print("🎉 Database synchronization completed successfully!")
        else:
            print("❌ Database synchronization failed!")
    elif command == 'download':
        save_path = sys.argv[2] if len(sys.argv) > 2 else None
        downloaded_file = client.download_database_file(save_path)
        if downloaded_file:
            print(f"🎉 Database downloaded: {downloaded_file}")
    elif command == 'picks':
        picks = client.get_picks_summary()
        if picks:
            print(json.dumps(picks, indent=2))
    else:
        print("Unknown command. Use: status, sync, download, or picks")

if __name__ == "__main__":
    main()

