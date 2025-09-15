#!/usr/bin/env python3
"""
Complete Database Fix Script
Cleans up all wrong data and inserts correct Week 1 data with proper picks and results
"""

import sqlite3
from datetime import datetime

def fix_database():
    """Fix the database completely"""
    
    conn = sqlite3.connect('instance/nfl_pickem.db')
    cursor = conn.cursor()
    
    print("🔧 Starting complete database cleanup...")
    
    # Step 1: Clear all wrong data
    print("Step 1: Clearing wrong data...")
    cursor.execute("DELETE FROM pick")
    cursor.execute("DELETE FROM match")
    cursor.execute("DELETE FROM eliminated_team")
    cursor.execute("DELETE FROM team_winner_usage")
    cursor.execute("DELETE FROM team_loser_usage")
    
    # Step 2: Insert correct Week 1 matches with real results
    print("Step 2: Inserting correct Week 1 matches...")
    
    # Real Week 1 NFL 2025 games with correct results
    week1_games = [
        # Thursday, Sept. 4, 2025
        {
            'week': 1, 'home_team': 'Philadelphia Eagles', 'away_team': 'Dallas Cowboys',
            'winner': 'Philadelphia Eagles', 'home_score': 24, 'away_score': 20
        },
        # Friday, Sept. 5, 2025
        {
            'week': 1, 'home_team': 'Los Angeles Chargers', 'away_team': 'Kansas City Chiefs',
            'winner': 'Los Angeles Chargers', 'home_score': 27, 'away_score': 21
        },
        # Sunday, Sept. 7, 2025
        {
            'week': 1, 'home_team': 'Atlanta Falcons', 'away_team': 'Tampa Bay Buccaneers',
            'winner': 'Tampa Bay Buccaneers', 'home_score': 20, 'away_score': 23
        },
        {
            'week': 1, 'home_team': 'Cleveland Browns', 'away_team': 'Cincinnati Bengals',
            'winner': 'Cincinnati Bengals', 'home_score': 16, 'away_score': 17
        },
        {
            'week': 1, 'home_team': 'Indianapolis Colts', 'away_team': 'Miami Dolphins',
            'winner': 'Indianapolis Colts', 'home_score': 33, 'away_score': 8
        },
        {
            'week': 1, 'home_team': 'Jacksonville Jaguars', 'away_team': 'Carolina Panthers',
            'winner': 'Jacksonville Jaguars', 'home_score': 26, 'away_score': 10
        },
        {
            'week': 1, 'home_team': 'New England Patriots', 'away_team': 'Las Vegas Raiders',
            'winner': 'Las Vegas Raiders', 'home_score': 13, 'away_score': 20
        },
        {
            'week': 1, 'home_team': 'New Orleans Saints', 'away_team': 'Arizona Cardinals',
            'winner': 'Arizona Cardinals', 'home_score': 13, 'away_score': 20
        },
        {
            'week': 1, 'home_team': 'New York Jets', 'away_team': 'Pittsburgh Steelers',
            'winner': 'Pittsburgh Steelers', 'home_score': 32, 'away_score': 34
        },
        {
            'week': 1, 'home_team': 'Washington Commanders', 'away_team': 'New York Giants',
            'winner': 'Washington Commanders', 'home_score': 21, 'away_score': 6
        },
        {
            'week': 1, 'home_team': 'Denver Broncos', 'away_team': 'Tennessee Titans',
            'winner': 'Denver Broncos', 'home_score': 20, 'away_score': 12
        },
        {
            'week': 1, 'home_team': 'Seattle Seahawks', 'away_team': 'San Francisco 49ers',
            'winner': 'San Francisco 49ers', 'home_score': 13, 'away_score': 17
        },
        {
            'week': 1, 'home_team': 'Green Bay Packers', 'away_team': 'Detroit Lions',
            'winner': 'Green Bay Packers', 'home_score': 27, 'away_score': 13
        },
        {
            'week': 1, 'home_team': 'Los Angeles Rams', 'away_team': 'Houston Texans',
            'winner': 'Los Angeles Rams', 'home_score': 14, 'away_score': 9
        },
        {
            'week': 1, 'home_team': 'Buffalo Bills', 'away_team': 'Baltimore Ravens',
            'winner': 'Buffalo Bills', 'home_score': 41, 'away_score': 40
        },
        # Monday, Sept. 8, 2025
        {
            'week': 1, 'home_team': 'Chicago Bears', 'away_team': 'Minnesota Vikings',
            'winner': 'Minnesota Vikings', 'home_score': 24, 'away_score': 27
        }
    ]
    
    # Get team IDs
    team_ids = {}
    teams = cursor.execute("SELECT id, name FROM team").fetchall()
    for team in teams:
        team_ids[team[1]] = team[0]
    
    # Insert matches
    match_ids = {}
    for i, game in enumerate(week1_games):
        home_team_id = team_ids[game['home_team']]
        away_team_id = team_ids[game['away_team']]
        winner_team_id = team_ids[game['winner']]
        
        cursor.execute("""
            INSERT INTO match (week, home_team_id, away_team_id, start_time, is_completed, 
                             winner_team_id, home_score, away_score, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            game['week'], home_team_id, away_team_id, 
            datetime(2025, 9, 7, 13, 0),  # Default time
            True, winner_team_id, game['home_score'], game['away_score'], 'FINAL'
        ))
        
        match_id = cursor.lastrowid
        match_key = f"{game['away_team']} @ {game['home_team']}"
        match_ids[match_key] = match_id
        
        print(f"✅ Added: {match_key} -> {game['winner']} {game['away_score']}-{game['home_score']}")
    
    # Step 3: Insert correct user picks
    print("Step 3: Inserting correct user picks...")
    
    # Real user picks from Week 1
    user_picks = [
        {'username': 'Manuel', 'pick': 'Atlanta Falcons', 'match_key': 'Tampa Bay Buccaneers @ Atlanta Falcons'},
        {'username': 'Daniel', 'pick': 'Denver Broncos', 'match_key': 'Tennessee Titans @ Denver Broncos'},
        {'username': 'Raff', 'pick': 'Cincinnati Bengals', 'match_key': 'Cincinnati Bengals @ Cleveland Browns'},
        {'username': 'Haunschi', 'pick': 'Washington Commanders', 'match_key': 'New York Giants @ Washington Commanders'}
    ]
    
    # Get user IDs
    user_ids = {}
    users = cursor.execute("SELECT id, username FROM user").fetchall()
    for user in users:
        user_ids[user[1]] = user[0]
    
    # Insert picks
    for pick_data in user_picks:
        user_id = user_ids[pick_data['username']]
        chosen_team_id = team_ids[pick_data['pick']]
        match_id = match_ids[pick_data['match_key']]
        
        cursor.execute("""
            INSERT INTO pick (user_id, match_id, chosen_team_id)
            VALUES (?, ?, ?)
        """, (user_id, match_id, chosen_team_id))
        
        print(f"✅ Added pick: {pick_data['username']} -> {pick_data['pick']}")
    
    # Step 4: Calculate correct results and eliminations
    print("Step 4: Calculating results and eliminations...")
    
    # Check each pick and calculate results
    for pick_data in user_picks:
        user_id = user_ids[pick_data['username']]
        chosen_team = pick_data['pick']
        match_id = match_ids[pick_data['match_key']]
        
        # Get the actual winner of the match
        match_result = cursor.execute("""
            SELECT t.name as winner_name
            FROM match m
            JOIN team t ON m.winner_team_id = t.id
            WHERE m.id = ?
        """, (match_id,)).fetchone()
        
        actual_winner = match_result[0]
        is_correct = chosen_team == actual_winner
        
        if is_correct:
            # Check if team winner usage already exists
            existing = cursor.execute("""
                SELECT id, usage_count FROM team_winner_usage 
                WHERE user_id = ? AND team_id = ?
            """, (user_id, team_ids[chosen_team])).fetchone()
            
            if existing:
                cursor.execute("""
                    UPDATE team_winner_usage SET usage_count = usage_count + 1
                    WHERE user_id = ? AND team_id = ?
                """, (user_id, team_ids[chosen_team]))
            else:
                cursor.execute("""
                    INSERT INTO team_winner_usage (user_id, team_id, usage_count)
                    VALUES (?, ?, 1)
                """, (user_id, team_ids[chosen_team]))
            
            print(f"✅ {pick_data['username']}: {chosen_team} CORRECT (1 point)")
        else:
            # Add to eliminated teams (as loser)
            cursor.execute("""
                INSERT INTO eliminated_team (user_id, team_id, elimination_type)
                VALUES (?, ?, 'loser')
            """, (user_id, team_ids[chosen_team]))
            
            print(f"❌ {pick_data['username']}: {chosen_team} WRONG (0 points) - eliminated as loser")
    
    # Step 5: Add some Week 2 games for testing
    print("Step 5: Adding Week 2 games...")
    
    week2_games = [
        {
            'week': 2, 'home_team': 'Green Bay Packers', 'away_team': 'Washington Commanders',
            'winner': None, 'home_score': None, 'away_score': None
        },
        {
            'week': 2, 'home_team': 'Baltimore Ravens', 'away_team': 'Cleveland Browns',
            'winner': None, 'home_score': None, 'away_score': None
        },
        {
            'week': 2, 'home_team': 'Cincinnati Bengals', 'away_team': 'Jacksonville Jaguars',
            'winner': None, 'home_score': None, 'away_score': None
        },
        {
            'week': 2, 'home_team': 'Dallas Cowboys', 'away_team': 'New York Giants',
            'winner': None, 'home_score': None, 'away_score': None
        }
    ]
    
    for game in week2_games:
        home_team_id = team_ids[game['home_team']]
        away_team_id = team_ids[game['away_team']]
        
        cursor.execute("""
            INSERT INTO match (week, home_team_id, away_team_id, start_time, is_completed, 
                             winner_team_id, home_score, away_score, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            game['week'], home_team_id, away_team_id, 
            datetime(2025, 9, 14, 13, 0),  # Week 2 time
            False, None, None, None, 'SCHEDULED'
        ))
        
        print(f"✅ Added Week 2: {game['away_team']} @ {game['home_team']}")
    
    conn.commit()
    conn.close()
    
    print("🎉 Database cleanup completed!")
    
    # Verify results
    print("\n📊 Verification:")
    verify_database()

def verify_database():
    """Verify the database is now correct"""
    
    conn = sqlite3.connect('instance/nfl_pickem.db')
    conn.row_factory = sqlite3.Row
    
    print("\n=== VERIFICATION RESULTS ===")
    
    # Check user scores
    users = conn.execute("SELECT id, username FROM user").fetchall()
    for user in users:
        # Count correct picks
        correct_picks = conn.execute("""
            SELECT COUNT(*) as count
            FROM pick p
            JOIN match m ON p.match_id = m.id
            JOIN team t ON p.chosen_team_id = t.id
            WHERE p.user_id = ? AND m.winner_team_id = p.chosen_team_id
        """, (user['id'],)).fetchone()
        
        score = correct_picks['count']
        print(f"{user['username']}: {score} points")
    
    # Check eliminations
    print("\n=== ELIMINATED TEAMS ===")
    eliminations = conn.execute("""
        SELECT u.username, t.name as team_name, e.elimination_type
        FROM eliminated_team e
        JOIN user u ON e.user_id = u.id
        JOIN team t ON e.team_id = t.id
    """).fetchall()
    
    for elim in eliminations:
        print(f"{elim['username']}: {elim['team_name']} ({elim['elimination_type']})")
    
    # Check team winner usage
    print("\n=== TEAM WINNER USAGE ===")
    usage = conn.execute("""
        SELECT u.username, t.name as team_name, tw.usage_count
        FROM team_winner_usage tw
        JOIN user u ON tw.user_id = u.id
        JOIN team t ON tw.team_id = t.id
    """).fetchall()
    
    for use in usage:
        print(f"{use['username']}: {use['team_name']} used {use['usage_count']}x as winner")
    
    conn.close()

if __name__ == "__main__":
    fix_database()

