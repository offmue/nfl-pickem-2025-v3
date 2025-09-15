#!/usr/bin/env python3
"""
Import complete NFL 2025 schedule into database
"""

import sys
import os
import pandas as pd
from datetime import datetime, timezone
sys.path.insert(0, '.')

from app import app, db, Match, Team

def import_complete_schedule():
    """Import complete NFL 2025 schedule from Excel file"""
    with app.app_context():
        
        # Read the official NFL schedule
        excel_file = '/home/ubuntu/NFL_2025_Official_Schedule_With_Results.xlsx'
        
        if not os.path.exists(excel_file):
            print(f"❌ Excel file not found: {excel_file}")
            return
        
        # Read the Complete_Schedule sheet
        df = pd.read_excel(excel_file, sheet_name='Complete_Schedule')
        
        print(f"📊 Found {len(df)} games in Excel file")
        
        # Get all teams for mapping
        teams = {team.name: team for team in Team.query.all()}
        
        # Track statistics
        added_count = 0
        updated_count = 0
        skipped_count = 0
        
        for index, row in df.iterrows():
            try:
                week = int(row['week'])
                home_team_name = str(row['home_team']).strip()
                away_team_name = str(row['away_team']).strip()
                
                # Find teams in database
                home_team = teams.get(home_team_name)
                away_team = teams.get(away_team_name)
                
                if not home_team:
                    print(f"⚠️  Home team not found: {home_team_name}")
                    skipped_count += 1
                    continue
                    
                if not away_team:
                    print(f"⚠️  Away team not found: {away_team_name}")
                    skipped_count += 1
                    continue
                
                # Check if match already exists
                existing_match = Match.query.filter_by(
                    week=week,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id
                ).first()
                
                if existing_match:
                    # Update existing match if needed
                    updated = False
                    
                    # Update completion status if specified
                    if 'completed' in row and pd.notna(row['completed']):
                        completed = bool(row['completed'])
                        if existing_match.is_completed != completed:
                            existing_match.is_completed = completed
                            updated = True
                    
                    # Update winner if specified
                    if 'winner_team' in row and pd.notna(row['winner_team']) and str(row['winner_team']) != 'nan':
                        winner_name = str(row['winner_team']).strip()
                        winner_team = teams.get(winner_name)
                        if winner_team and existing_match.winner_team_id != winner_team.id:
                            existing_match.winner_team_id = winner_team.id
                            updated = True
                    
                    # Update start time if specified
                    if 'datetime' in row and pd.notna(row['datetime']):
                        try:
                            if isinstance(row['datetime'], str):
                                start_time = datetime.fromisoformat(row['datetime'].replace('Z', '+00:00'))
                            else:
                                start_time = row['datetime']
                            
                            if existing_match.start_time != start_time:
                                existing_match.start_time = start_time
                                updated = True
                        except:
                            pass  # Skip invalid datetime
                    
                    if updated:
                        updated_count += 1
                    else:
                        skipped_count += 1
                    
                else:
                    # Create new match
                    new_match = Match(
                        week=week,
                        home_team_id=home_team.id,
                        away_team_id=away_team.id,
                        is_completed=False
                    )
                    
                    # Set completion status if specified
                    if 'completed' in row and pd.notna(row['completed']):
                        new_match.is_completed = bool(row['completed'])
                    
                    # Set winner if specified
                    if 'winner_team' in row and pd.notna(row['winner_team']) and str(row['winner_team']) != 'nan':
                        winner_name = str(row['winner_team']).strip()
                        winner_team = teams.get(winner_name)
                        if winner_team:
                            new_match.winner_team_id = winner_team.id
                    
                    # Set start time if specified
                    if 'datetime' in row and pd.notna(row['datetime']):
                        try:
                            if isinstance(row['datetime'], str):
                                new_match.start_time = datetime.fromisoformat(row['datetime'].replace('Z', '+00:00'))
                            else:
                                new_match.start_time = row['datetime']
                        except:
                            pass  # Skip invalid datetime
                    
                    db.session.add(new_match)
                    added_count += 1
                
            except Exception as e:
                print(f"❌ Error processing row {index}: {e}")
                print(f"   Row data: {row.to_dict()}")
                skipped_count += 1
                continue
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"✅ Schedule import completed!")
            print(f"   Added: {added_count} new matches")
            print(f"   Updated: {updated_count} existing matches")
            print(f"   Skipped: {skipped_count} matches")
            
            # Verify total matches
            total_matches = Match.query.count()
            print(f"   Total matches in database: {total_matches}")
            
            # Show matches per week
            print(f"\n📊 Matches per week:")
            for week in range(1, 19):
                week_count = Match.query.filter_by(week=week).count()
                print(f"   Week {week:2d}: {week_count:2d} matches")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error committing changes: {e}")

def create_missing_weeks_from_template():
    """Create missing weeks 3-18 with template data"""
    with app.app_context():
        
        # Template games for weeks 3-18 (will be updated weekly with real matchups)
        template_games = [
            # Week has 16 games typically, some weeks have 15 or 17
            # This is a simplified template - real matchups will be updated weekly
        ]
        
        print("📝 Creating template matches for weeks 3-18...")
        
        # Get all teams
        teams = list(Team.query.all())
        
        added_count = 0
        
        for week in range(3, 19):  # Weeks 3-18
            existing_count = Match.query.filter_by(week=week).count()
            
            if existing_count == 0:
                # Create template matches for this week
                # In a real scenario, these would be the actual NFL schedule
                # For now, create placeholder matches that will be updated
                
                # Create 16 template matches per week (typical NFL week)
                for i in range(0, min(16, len(teams)), 2):
                    if i + 1 < len(teams):
                        home_team = teams[i]
                        away_team = teams[i + 1]
                        
                        template_match = Match(
                            week=week,
                            home_team_id=home_team.id,
                            away_team_id=away_team.id,
                            is_completed=False,
                            start_time=None  # Will be set when real schedule is available
                        )
                        
                        db.session.add(template_match)
                        added_count += 1
                        
                        if added_count % 16 == 0:  # 16 games per week
                            break
        
        try:
            db.session.commit()
            print(f"✅ Created {added_count} template matches for weeks 3-18")
            print("⚠️  These are placeholder matches and need to be updated with real NFL schedule")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating template matches: {e}")

if __name__ == '__main__':
    print("🏈 Importing complete NFL 2025 schedule...")
    import_complete_schedule()
    
    # Check if we need to create template matches for missing weeks
    with app.app_context():
        total_matches = Match.query.count()
        if total_matches < 200:  # NFL season has ~272 games
            print(f"\n⚠️  Only {total_matches} matches found. Creating template matches...")
            create_missing_weeks_from_template()

