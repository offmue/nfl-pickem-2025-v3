#!/usr/bin/env python3
"""
Fix elimination logic based on PLAYER CHOICES, not game results.
- Chosen losers are eliminated (1x max)
- Chosen winners are partially used (1/2x max)
- Real NFL results only affect points, not eliminations
"""

import sys
import os
sys.path.insert(0, '.')

from app import app, db, User, Pick, Match, Team, EliminatedTeam, TeamWinnerUsage, TeamLoserUsage

def fix_elimination_logic():
    with app.app_context():
        print("=== FIXING ELIMINATION LOGIC (PLAYER CHOICES ONLY) ===")
        
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
            user = db.session.get(User, pick.user_id)
            match = db.session.get(Match, pick.match_id)
            chosen_team = db.session.get(Team, pick.chosen_team_id)
            
            # Determine opposing team (the chosen loser)
            if match.home_team_id == pick.chosen_team_id:
                opposing_team_id = match.away_team_id
            else:
                opposing_team_id = match.home_team_id
            
            opposing_team = db.session.get(Team, opposing_team_id)
            
            print(f"\n{user.username}: Chose {chosen_team.name} as WINNER, {opposing_team.name} as LOSER")
            
            # Add winner usage (1/2x used)
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
                print(f"  Added winner usage: {chosen_team.name} (1/2x used)")
            else:
                winner_usage.usage_count += 1
                print(f"  Updated winner usage: {chosen_team.name} ({winner_usage.usage_count}/2x used)")
            
            # Add loser usage (1x max - ELIMINATED)
            loser_usage = TeamLoserUsage(
                user_id=user.id,
                team_id=opposing_team_id,
                week=match.week,
                match_id=match.id
            )
            db.session.add(loser_usage)
            print(f"  Added loser usage: {opposing_team.name} (ELIMINATED)")
            
            # Add loser elimination (chosen as loser = eliminated)
            loser_elimination = EliminatedTeam(
                user_id=user.id,
                team_id=opposing_team_id,
                elimination_type='loser'
            )
            db.session.add(loser_elimination)
            print(f"  Added loser elimination: {opposing_team.name}")
            
            # Check if winner should be eliminated (if used 2x already)
            if winner_usage.usage_count >= 2:
                winner_elimination = EliminatedTeam(
                    user_id=user.id,
                    team_id=chosen_team.id,
                    elimination_type='winner'
                )
                db.session.add(winner_elimination)
                print(f"  Added winner elimination: {chosen_team.name} (used 2x)")
        
        db.session.commit()
        print("\n=== ELIMINATION LOGIC FIX COMPLETED ===")
        
        # Verify results
        print("\n=== VERIFICATION ===")
        for user in User.query.all():
            eliminations = EliminatedTeam.query.filter_by(user_id=user.id).all()
            winner_usages = TeamWinnerUsage.query.filter_by(user_id=user.id).all()
            loser_usages = TeamLoserUsage.query.filter_by(user_id=user.id).all()
            
            print(f"\n{user.username}:")
            print(f"  Eliminations: {len(eliminations)}")
            for elim in eliminations:
                team = db.session.get(Team, elim.team_id)
                print(f"    {team.name} ({elim.elimination_type})")
            
            print(f"  Winner usages: {len(winner_usages)}")
            for usage in winner_usages:
                team = db.session.get(Team, usage.team_id)
                status = "ELIMINATED" if usage.usage_count >= 2 else f"{usage.usage_count}/2x"
                print(f"    {team.name} ({status})")
            
            print(f"  Loser usages: {len(loser_usages)}")
            for usage in loser_usages:
                team = db.session.get(Team, usage.team_id)
                print(f"    {team.name} (ELIMINATED)")

if __name__ == '__main__':
    fix_elimination_logic()

