#!/usr/bin/env python3
"""
Manual NFL Game Validation Script
For testing and emergency validation of game results
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_validator import NFLGameValidator
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Manually validate NFL game results')
    parser.add_argument('--week', type=int, help='Validate specific week (1-18)')
    parser.add_argument('--current', action='store_true', help='Validate current week')
    parser.add_argument('--all', action='store_true', help='Validate all incomplete weeks')
    parser.add_argument('--year', type=int, default=2025, help='NFL season year (default: 2025)')
    
    args = parser.parse_args()
    
    validator = NFLGameValidator()
    
    if args.week:
        logger.info(f"Validating Week {args.week}")
        success = validator.validate_week(args.week, args.year)
        if success:
            logger.info(f"✅ Week {args.week} validation completed successfully")
        else:
            logger.error(f"❌ Week {args.week} validation failed")
            sys.exit(1)
    
    elif args.current:
        logger.info("Validating current week")
        success = validator.validate_current_week()
        if success:
            logger.info("✅ Current week validation completed successfully")
        else:
            logger.error("❌ Current week validation failed")
            sys.exit(1)
    
    elif args.all:
        logger.info("Validating all incomplete weeks")
        success = validator.validate_all_incomplete_weeks()
        if success:
            logger.info("✅ All weeks validation completed successfully")
        else:
            logger.error("❌ Some weeks validation failed")
            sys.exit(1)
    
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python manual_validation.py --week 2")
        print("  python manual_validation.py --current")
        print("  python manual_validation.py --all")

if __name__ == "__main__":
    main()

