#!/usr/bin/env python3
"""
Fix eliminations for all players based on their Week 1 picks.
Every pick means choosing a winner AND eliminating the opposing team as loser.
"""

import sys
import os
sys.path.insert(0, '.')

from app import app, db, User, Pick, Match, Team, EliminatedTeam, TeamWinnerUsage, TeamLoserUsage

def fix_all_eliminations():
    with app.app_context():
        print("=== FIXING ALL PLAYER ELIMINATIONS ===")
        
        # Clear existing eliminations and usage
        print("Clearing existing eliminations and usage...")
        EliminatedTeam.query.delete()
        TeamWinnerUsage.query.delete()
        TeamLoserUsage.query.delete()
        db.session.commit()
        
        # Get all Week 1 picks
        week1_picks = Pick.query.join(Match).filter(Match.week == 1).all()
        
        print(f"Processing {len(week1_picks)} Week 1 picks...")
        
        for pick in week1_picks:
            user = User.query.get(pick.user_id)
            match = Match.query.get(pick.match_id)
            chosen_team = Team.query.get(pick.chosen_team_id)
            
            # Determine opposing team
            if match.home_team_id == pick.chosen_team_id:
                opposing_team_id = match.away_team_id
            else:
                opposing_team_id = match.home_team_id
            
            opposing_team = Team.query.get(opposing_team_id)
            
            print(f"\n{user.username}: {chosen_team.name} vs {opposing_team.name}")
            
            # Add winner usage
            winner_usage = TeamWinnerUsage.query.filter_by(
                user_id=user.id, 
                team_id=chosen_team.id
            ).first()
            
            if not winner_usage:
                winner_usage = TeamWinnerUsage(
                    user_id=user.id,
                    team_id=chosen_team.id,
                    usage_count=1
                )
                db.session.add(winner_usage)
                print(f"  Added winner usage: {chosen_team.name} (1x)")
            else:
                winner_usage.usage_count += 1
                print(f"  Updated winner usage: {chosen_team.name} ({winner_usage.usage_count}x)")
            
            # Add loser usage
            loser_usage = TeamLoserUsage(
                user_id=user.id,
                team_id=opposing_team_id,
                week=match.week,
                match_id=match.id
            )
            db.session.add(loser_usage)
            print(f"  Added loser usage: {opposing_team.name}")
            
            # Add loser elimination
            loser_elimination = EliminatedTeam(
                user_id=user.id,
                team_id=opposing_team_id,
                elimination_type='loser'
            )
            db.session.add(loser_elimination)
            print(f"  Added loser elimination: {opposing_team.name}")
            
            # Check if winner should be eliminated (if pick was wrong)
            if match.is_completed and match.winner_team_id != pick.chosen_team_id:
                # Wrong pick - eliminate chosen team as winner
                winner_elimination = EliminatedTeam(
                    user_id=user.id,
                    team_id=chosen_team.id,
                    elimination_type='winner'
                )
                db.session.add(winner_elimination)
                print(f"  Added winner elimination: {chosen_team.name} (wrong pick)")
        
        db.session.commit()
        print("\n=== ELIMINATION FIX COMPLETED ===")
        
        # Verify results
        print("\n=== VERIFICATION ===")
        for user in User.query.all():
            eliminations = EliminatedTeam.query.filter_by(user_id=user.id).all()
            winner_usages = TeamWinnerUsage.query.filter_by(user_id=user.id).all()
            loser_usages = TeamLoserUsage.query.filter_by(user_id=user.id).all()
            
            print(f"\n{user.username}:")
            print(f"  Eliminations: {len(eliminations)}")
            for elim in eliminations:
                team = Team.query.get(elim.team_id)
                print(f"    {team.name} ({elim.elimination_type})")
            
            print(f"  Winner usages: {len(winner_usages)}")
            for usage in winner_usages:
                team = Team.query.get(usage.team_id)
                print(f"    {team.name} ({usage.usage_count}x)")
            
            print(f"  Loser usages: {len(loser_usages)}")
            for usage in loser_usages:
                team = Team.query.get(usage.team_id)
                print(f"    {team.name}")

if __name__ == '__main__':
    fix_all_eliminations()

