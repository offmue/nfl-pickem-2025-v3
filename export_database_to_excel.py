#!/usr/bin/env python3
"""
Export complete database to Excel for manual inspection
"""

import sys
import os
import pandas as pd
from datetime import datetime
sys.path.insert(0, '.')

from app import app, db, User, Pick, Match, Team, EliminatedTeam, TeamWinnerUsage, TeamLoserUsage

def export_database_to_excel():
    """Export complete database to Excel with multiple sheets"""
    with app.app_context():
        
        # Create Excel writer
        excel_file = 'NFL_PickEm_Database_Complete.xlsx'
        writer = pd.ExcelWriter(excel_file, engine='openpyxl')
        
        # 1. USERS Sheet
        users_data = []
        for user in User.query.all():
            users_data.append({
                'ID': user.id,
                'Username': user.username,
                'Score': user.get_score(),
                'Created': getattr(user, 'created_at', 'N/A')
            })
        
        users_df = pd.DataFrame(users_data)
        users_df.to_excel(writer, sheet_name='Users', index=False)
        
        # 2. TEAMS Sheet
        teams_data = []
        for team in Team.query.all():
            teams_data.append({
                'ID': team.id,
                'Name': team.name
            })
        
        teams_df = pd.DataFrame(teams_data)
        teams_df.to_excel(writer, sheet_name='Teams', index=False)
        
        # 3. MATCHES Sheet
        matches_data = []
        for match in Match.query.order_by(Match.week, Match.id).all():
            home_team = db.session.get(Team, match.home_team_id)
            away_team = db.session.get(Team, match.away_team_id)
            winner_team = db.session.get(Team, match.winner_team_id) if match.winner_team_id else None
            
            matches_data.append({
                'ID': match.id,
                'Week': match.week,
                'Away_Team': away_team.name,
                'Home_Team': home_team.name,
                'Matchup': f"{away_team.name} @ {home_team.name}",
                'Winner': winner_team.name if winner_team else 'TBD',
                'Completed': match.is_completed,
                'Start_Time': str(match.start_time) if match.start_time else 'TBD',
                'Result': getattr(match, 'result', 'N/A')
            })
        
        matches_df = pd.DataFrame(matches_data)
        matches_df.to_excel(writer, sheet_name='Matches', index=False)
        
        # 4. PICKS Sheet
        picks_data = []
        for pick in Pick.query.join(User).join(Match).order_by(Match.week, User.username).all():
            user = db.session.get(User, pick.user_id)
            match = db.session.get(Match, pick.match_id)
            chosen_team = db.session.get(Team, pick.chosen_team_id)
            
            # Calculate if pick is correct
            is_correct = None
            if match.is_completed and match.winner_team_id:
                is_correct = match.winner_team_id == pick.chosen_team_id
            
            # Get opposing team (the "loser" pick)
            if match.home_team_id == pick.chosen_team_id:
                opposing_team = db.session.get(Team, match.away_team_id)
            else:
                opposing_team = db.session.get(Team, match.home_team_id)
            
            picks_data.append({
                'ID': pick.id,
                'User': user.username,
                'Week': match.week,
                'Matchup': f"{db.session.get(Team, match.away_team_id).name} @ {db.session.get(Team, match.home_team_id).name}",
                'Chosen_Winner': chosen_team.name,
                'Implied_Loser': opposing_team.name,
                'Actual_Winner': db.session.get(Team, match.winner_team_id).name if match.winner_team_id else 'TBD',
                'Is_Correct': 'YES' if is_correct == True else 'NO' if is_correct == False else 'TBD',
                'Points': 1 if is_correct == True else 0 if is_correct == False else 0
            })
        
        picks_df = pd.DataFrame(picks_data)
        picks_df.to_excel(writer, sheet_name='Picks', index=False)
        
        # 5. TEAM WINNER USAGE Sheet
        winner_usage_data = []
        for usage in TeamWinnerUsage.query.join(User).join(Team).order_by(User.username, Team.name).all():
            user = db.session.get(User, usage.user_id)
            team = db.session.get(Team, usage.team_id)
            
            winner_usage_data.append({
                'User': user.username,
                'Team': team.name,
                'Usage_Count': usage.usage_count,
                'Max_Usage': 2,
                'Status': 'ELIMINATED' if usage.usage_count >= 2 else f'{usage.usage_count}/2x',
                'Can_Use_Again': 'NO' if usage.usage_count >= 2 else 'YES'
            })
        
        winner_usage_df = pd.DataFrame(winner_usage_data)
        winner_usage_df.to_excel(writer, sheet_name='Team_Winner_Usage', index=False)
        
        # 6. TEAM LOSER USAGE Sheet
        loser_usage_data = []
        for usage in TeamLoserUsage.query.join(User).join(Team).order_by(User.username, Team.name).all():
            user = db.session.get(User, usage.user_id)
            team = db.session.get(Team, usage.team_id)
            match = db.session.get(Match, usage.match_id) if hasattr(usage, 'match_id') else None
            
            loser_usage_data.append({
                'User': user.username,
                'Team': team.name,
                'Week': usage.week,
                'Match_ID': getattr(usage, 'match_id', 'N/A'),
                'Status': 'ELIMINATED (1x max)',
                'Can_Use_Again': 'NO'
            })
        
        loser_usage_df = pd.DataFrame(loser_usage_data)
        loser_usage_df.to_excel(writer, sheet_name='Team_Loser_Usage', index=False)
        
        # 7. ELIMINATED TEAMS Sheet
        eliminated_data = []
        for elim in EliminatedTeam.query.join(User).join(Team).order_by(User.username, Team.name).all():
            user = db.session.get(User, elim.user_id)
            team = db.session.get(Team, elim.team_id)
            
            eliminated_data.append({
                'User': user.username,
                'Team': team.name,
                'Elimination_Type': elim.elimination_type,
                'Reason': 'Used as loser (1x max)' if elim.elimination_type == 'loser' else 'Used as winner (2x max)'
            })
        
        eliminated_df = pd.DataFrame(eliminated_data)
        eliminated_df.to_excel(writer, sheet_name='Eliminated_Teams', index=False)
        
        # 8. SUMMARY Sheet
        summary_data = []
        
        # User scores
        for user in User.query.all():
            summary_data.append({
                'Category': 'User Score',
                'User': user.username,
                'Value': user.get_score(),
                'Details': f'{user.get_score()} points'
            })
        
        # Week 1 validation
        week1_picks = Pick.query.join(Match).filter(Match.week == 1).count()
        summary_data.append({
            'Category': 'Validation',
            'User': 'ALL',
            'Value': week1_picks,
            'Details': f'{week1_picks} Week 1 picks (should be 4)'
        })
        
        # Week 1 matches
        week1_matches = Match.query.filter_by(week=1).count()
        week1_completed = Match.query.filter_by(week=1, is_completed=True).count()
        summary_data.append({
            'Category': 'Validation',
            'User': 'ALL',
            'Value': f'{week1_completed}/{week1_matches}',
            'Details': f'Week 1 matches completed'
        })
        
        # Eliminations per user
        for user in User.query.all():
            elim_count = EliminatedTeam.query.filter_by(user_id=user.id, elimination_type='loser').count()
            summary_data.append({
                'Category': 'Eliminations',
                'User': user.username,
                'Value': elim_count,
                'Details': f'{elim_count} teams eliminated as losers (should be 1)'
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # 9. VALIDATION CHECKS Sheet
        validation_data = []
        
        # Check 1: Each user should have exactly 1 Week 1 pick
        for user in User.query.all():
            pick_count = Pick.query.join(Match).filter(Match.week == 1, Pick.user_id == user.id).count()
            validation_data.append({
                'Check': 'Week 1 Picks',
                'User': user.username,
                'Expected': 1,
                'Actual': pick_count,
                'Status': 'PASS' if pick_count == 1 else 'FAIL',
                'Details': f'User should have exactly 1 Week 1 pick'
            })
        
        # Check 2: Each user should have exactly 1 loser elimination
        for user in User.query.all():
            elim_count = EliminatedTeam.query.filter_by(user_id=user.id, elimination_type='loser').count()
            validation_data.append({
                'Check': 'Loser Eliminations',
                'User': user.username,
                'Expected': 1,
                'Actual': elim_count,
                'Status': 'PASS' if elim_count == 1 else 'FAIL',
                'Details': f'User should have exactly 1 team eliminated as loser'
            })
        
        # Check 3: Week 1 matches validation
        week1_matches = Match.query.filter_by(week=1).all()
        for match in week1_matches:
            has_winner = match.winner_team_id is not None
            validation_data.append({
                'Check': 'Week 1 Match Winners',
                'User': 'SYSTEM',
                'Expected': 'Winner assigned',
                'Actual': 'Winner assigned' if has_winner else 'No winner',
                'Status': 'PASS' if has_winner else 'FAIL',
                'Details': f'Match {match.id}: {db.session.get(Team, match.away_team_id).name} @ {db.session.get(Team, match.home_team_id).name}'
            })
        
        validation_df = pd.DataFrame(validation_data)
        validation_df.to_excel(writer, sheet_name='Validation_Checks', index=False)
        
        # Save the Excel file
        writer.close()
        
        print(f"✅ Database exported to {excel_file}")
        print(f"📊 Sheets created:")
        print(f"   - Users ({len(users_data)} entries)")
        print(f"   - Teams ({len(teams_data)} entries)")
        print(f"   - Matches ({len(matches_data)} entries)")
        print(f"   - Picks ({len(picks_data)} entries)")
        print(f"   - Team_Winner_Usage ({len(winner_usage_data)} entries)")
        print(f"   - Team_Loser_Usage ({len(loser_usage_data)} entries)")
        print(f"   - Eliminated_Teams ({len(eliminated_data)} entries)")
        print(f"   - Summary ({len(summary_data)} entries)")
        print(f"   - Validation_Checks ({len(validation_data)} entries)")
        
        return excel_file

if __name__ == '__main__':
    export_database_to_excel()

