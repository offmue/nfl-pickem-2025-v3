#!/usr/bin/env python3
"""
Complete database analysis and export for validation
"""

import sys
import os
import json
sys.path.insert(0, '.')

from app import app, db, User, Pick, Match, Team, EliminatedTeam, TeamWinnerUsage, TeamLoserUsage

def analyze_database():
    with app.app_context():
        print("=== COMPLETE DATABASE ANALYSIS ===")
        
        # 1. USERS
        print("\n1. USERS:")
        users = User.query.all()
        for user in users:
            print(f"  ID: {user.id}, Username: {user.username}")
        
        # 2. TEAMS
        print(f"\n2. TEAMS ({Team.query.count()} total):")
        teams = Team.query.all()
        for team in teams:
            print(f"  ID: {team.id}, Name: {team.name}")
        
        # 3. MATCHES
        print(f"\n3. MATCHES ({Match.query.count()} total):")
        matches = Match.query.order_by(Match.week, Match.id).all()
        for match in matches:
            home_team = db.session.get(Team, match.home_team_id)
            away_team = db.session.get(Team, match.away_team_id)
            winner_team = db.session.get(Team, match.winner_team_id) if match.winner_team_id else None
            
            print(f"  Week {match.week}: {away_team.name} @ {home_team.name}")
            print(f"    ID: {match.id}, Completed: {match.is_completed}")
            if winner_team:
                print(f"    Winner: {winner_team.name}")
            if hasattr(match, 'result') and match.result:
                print(f"    Result: {match.result}")
            print()
        
        # 4. PICKS
        print(f"\n4. PICKS ({Pick.query.count()} total):")
        picks = Pick.query.join(User).join(Match).order_by(Match.week, User.username).all()
        for pick in picks:
            user = db.session.get(User, pick.user_id)
            match = db.session.get(Match, pick.match_id)
            chosen_team = db.session.get(Team, pick.chosen_team_id)
            
            # Calculate if pick is correct
            is_correct = match.winner_team_id == pick.chosen_team_id if match.is_completed else "TBD"
            
            print(f"  Week {match.week} - {user.username}: {chosen_team.name} ({'✓' if is_correct == True else '✗' if is_correct == False else '?'})")
        
        # 5. TEAM WINNER USAGE
        print(f"\n5. TEAM WINNER USAGE ({TeamWinnerUsage.query.count()} total):")
        winner_usages = TeamWinnerUsage.query.join(User).join(Team).order_by(User.username, Team.name).all()
        for usage in winner_usages:
            user = db.session.get(User, usage.user_id)
            team = db.session.get(Team, usage.team_id)
            status = "ELIMINATED" if usage.usage_count >= 2 else f"{usage.usage_count}/2x"
            print(f"  {user.username} - {team.name}: {status}")
        
        # 6. TEAM LOSER USAGE
        print(f"\n6. TEAM LOSER USAGE ({TeamLoserUsage.query.count()} total):")
        loser_usages = TeamLoserUsage.query.join(User).join(Team).order_by(User.username, Team.name).all()
        for usage in loser_usages:
            user = db.session.get(User, usage.user_id)
            team = db.session.get(Team, usage.team_id)
            print(f"  {user.username} - {team.name}: Week {usage.week} (ELIMINATED)")
        
        # 7. ELIMINATED TEAMS
        print(f"\n7. ELIMINATED TEAMS ({EliminatedTeam.query.count()} total):")
        eliminations = EliminatedTeam.query.join(User).join(Team).order_by(User.username, Team.name).all()
        for elim in eliminations:
            user = db.session.get(User, elim.user_id)
            team = db.session.get(Team, elim.team_id)
            print(f"  {user.username} - {team.name}: {elim.elimination_type}")
        
        # 8. USER SCORES CALCULATION
        print(f"\n8. USER SCORES:")
        for user in users:
            score = user.get_score()
            print(f"  {user.username}: {score} points")
        
        # 9. DATA SOURCES DOCUMENTATION
        print(f"\n9. DATA SOURCES:")
        print("  - Week 1 Matches: Manual entry based on real NFL results")
        print("  - Week 1 Results: Real NFL scores from ESPN")
        print("  - Week 1 Picks: User-provided actual picks")
        print("  - Week 2 Matches: Test data (4 games)")
        print("  - Teams: Standard 32 NFL teams")
        print("  - Users: Test users (Manuel, Daniel, Raff, Haunschi)")
        
        # 10. VALIDATION CHECKS
        print(f"\n10. VALIDATION CHECKS:")
        
        # Check 1: Each user should have exactly 1 Week 1 pick
        week1_picks_per_user = {}
        for pick in Pick.query.join(Match).filter(Match.week == 1).all():
            user = db.session.get(User, pick.user_id)
            week1_picks_per_user[user.username] = week1_picks_per_user.get(user.username, 0) + 1
        
        print("  Week 1 picks per user:")
        for username, count in week1_picks_per_user.items():
            status = "✓" if count == 1 else f"✗ ({count})"
            print(f"    {username}: {count} {status}")
        
        # Check 2: Each user should have exactly 1 eliminated team (loser)
        loser_eliminations_per_user = {}
        for elim in EliminatedTeam.query.filter_by(elimination_type='loser').all():
            user = db.session.get(User, elim.user_id)
            loser_eliminations_per_user[user.username] = loser_eliminations_per_user.get(user.username, 0) + 1
        
        print("  Loser eliminations per user:")
        for username, count in loser_eliminations_per_user.items():
            status = "✓" if count == 1 else f"✗ ({count})"
            print(f"    {username}: {count} {status}")
        
        # Check 3: Week 1 matches should all be completed
        week1_matches = Match.query.filter_by(week=1).all()
        completed_week1 = sum(1 for m in week1_matches if m.is_completed)
        print(f"  Week 1 matches completed: {completed_week1}/{len(week1_matches)} {'✓' if completed_week1 == len(week1_matches) else '✗'}")
        
        # Check 4: All Week 1 matches should have winners
        week1_with_winners = sum(1 for m in week1_matches if m.winner_team_id)
        print(f"  Week 1 matches with winners: {week1_with_winners}/{len(week1_matches)} {'✓' if week1_with_winners == len(week1_matches) else '✗'}")

def export_database_to_json():
    """Export complete database to JSON for manual inspection"""
    with app.app_context():
        export_data = {
            'users': [],
            'teams': [],
            'matches': [],
            'picks': [],
            'team_winner_usage': [],
            'team_loser_usage': [],
            'eliminated_teams': []
        }
        
        # Export Users
        for user in User.query.all():
            export_data['users'].append({
                'id': user.id,
                'username': user.username,
                'score': user.get_score()
            })
        
        # Export Teams
        for team in Team.query.all():
            export_data['teams'].append({
                'id': team.id,
                'name': team.name
            })
        
        # Export Matches
        for match in Match.query.all():
            home_team = db.session.get(Team, match.home_team_id)
            away_team = db.session.get(Team, match.away_team_id)
            winner_team = db.session.get(Team, match.winner_team_id) if match.winner_team_id else None
            
            export_data['matches'].append({
                'id': match.id,
                'week': match.week,
                'home_team': home_team.name,
                'away_team': away_team.name,
                'winner_team': winner_team.name if winner_team else None,
                'completed': match.is_completed,
                'result': getattr(match, 'result', None),
                'start_time': str(match.start_time) if match.start_time else None
            })
        
        # Export Picks
        for pick in Pick.query.all():
            user = db.session.get(User, pick.user_id)
            match = db.session.get(Match, pick.match_id)
            chosen_team = db.session.get(Team, pick.chosen_team_id)
            
            is_correct = match.winner_team_id == pick.chosen_team_id if match.is_completed else None
            
            export_data['picks'].append({
                'id': pick.id,
                'user': user.username,
                'week': match.week,
                'chosen_team': chosen_team.name,
                'is_correct': is_correct,
                'match_description': f"{db.session.get(Team, match.away_team_id).name} @ {db.session.get(Team, match.home_team_id).name}"
            })
        
        # Export Team Winner Usage
        for usage in TeamWinnerUsage.query.all():
            user = db.session.get(User, usage.user_id)
            team = db.session.get(Team, usage.team_id)
            
            export_data['team_winner_usage'].append({
                'user': user.username,
                'team': team.name,
                'usage_count': usage.usage_count,
                'status': 'ELIMINATED' if usage.usage_count >= 2 else f'{usage.usage_count}/2x'
            })
        
        # Export Team Loser Usage
        for usage in TeamLoserUsage.query.all():
            user = db.session.get(User, usage.user_id)
            team = db.session.get(Team, usage.team_id)
            
            export_data['team_loser_usage'].append({
                'user': user.username,
                'team': team.name,
                'week': usage.week,
                'status': 'ELIMINATED'
            })
        
        # Export Eliminated Teams
        for elim in EliminatedTeam.query.all():
            user = db.session.get(User, elim.user_id)
            team = db.session.get(Team, elim.team_id)
            
            export_data['eliminated_teams'].append({
                'user': user.username,
                'team': team.name,
                'elimination_type': elim.elimination_type
            })
        
        # Save to file
        with open('database_export.json', 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nDatabase exported to database_export.json")
        return export_data

if __name__ == '__main__':
    analyze_database()
    export_database_to_json()

