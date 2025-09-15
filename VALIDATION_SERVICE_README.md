# NFL PickEm Validation Service

## Overview
The NFL PickEm application includes an automatic game validation service that fetches real NFL game results from ESPN and updates the database accordingly.

## Features

### Automatic Validation
- **Real-time Updates**: Fetches game results from ESPN API
- **Scheduled Validation**: Runs automatically at set intervals
- **Point Calculation**: Updates user points based on correct predictions
- **Team Elimination**: Manages team usage limits and eliminations

### Validation Schedule
- **Every 30 minutes**: During game days (validates current week)
- **Daily at midnight**: Comprehensive validation of all incomplete weeks
- **Tuesday 2 AM**: Final weekly validation (after Monday Night Football)

## Components

### 1. game_validator.py
Main validation service with the following classes and functions:

#### NFLGameValidator Class
- `get_espn_scoreboard(week, year)`: Fetches ESPN scoreboard data
- `parse_espn_game_result(game_data)`: Parses ESPN game results
- `update_game_result(conn, match_id, result_data)`: Updates database with results
- `calculate_user_points(conn, week)`: Calculates and updates user points
- `update_team_eliminations(conn, week)`: Updates team elimination status
- `validate_week(week, year)`: Validates all games for a specific week
- `validate_current_week()`: Validates the current NFL week
- `validate_all_incomplete_weeks()`: Validates all weeks with incomplete games

#### Scheduler Functions
- `run_validation_service()`: Main service loop with scheduled tasks
- `start_validation_service_thread()`: Starts validation service in background thread

### 2. manual_validation.py
Manual validation script for testing and emergency use:

```bash
# Validate specific week
python manual_validation.py --week 2

# Validate current week
python manual_validation.py --current

# Validate all incomplete weeks
python manual_validation.py --all
```

### 3. Integration with Flask App
The validation service is automatically started when the Flask application runs:

```python
# In app.py
from game_validator import start_validation_service_thread
validation_thread = start_validation_service_thread()
```

## Data Sources

### ESPN API
- **Base URL**: `https://site.api.espn.com/apis/site/v2/sports/football/nfl`
- **Scoreboard Endpoint**: `/scoreboard?seasontype=2&week={week}&year={year}`
- **Data Format**: JSON with game details, scores, and completion status

### Database Updates
The service updates the following database tables:

#### matches
- `result`: Game result string (e.g., "Eagles 24 - Cowboys 20")
- `completed`: Boolean flag indicating game completion
- `winner`: Winning team name

#### picks
- `is_correct`: Boolean indicating if prediction was correct
- `points`: Points awarded (1 for correct, 0 for incorrect)

#### team_winner_usage
- `usage_count`: Number of times team was picked as winner

#### eliminated_teams
- `elimination_type`: 'winner' (2x usage) or 'loser' (1x wrong pick)

## Error Handling

### Robust Error Management
- **API Failures**: Graceful handling of ESPN API timeouts or errors
- **Database Errors**: Transaction rollback on database failures
- **Parsing Errors**: Skip malformed game data without crashing
- **Logging**: Comprehensive logging for debugging and monitoring

### Fallback Mechanisms
- **Fuzzy Matching**: Handles slight team name differences between ESPN and database
- **Retry Logic**: Automatic retries for temporary network issues
- **Manual Override**: Manual validation script for emergency situations

## Monitoring

### Log Files
- **Location**: `/home/ubuntu/nfl-pickem-final-corrected/game_validator.log`
- **Format**: Timestamp, log level, message
- **Content**: Validation results, errors, and service status

### Log Examples
```
2025-09-14 15:30:01 - INFO - Starting validation for Week 2
2025-09-14 15:30:02 - INFO - Successfully fetched ESPN data for Week 2
2025-09-14 15:30:03 - INFO - Updated match 15: Eagles 24 - Cowboys 20
2025-09-14 15:30:04 - INFO - User Manuel: Cowboys -> ❌ (0 points)
2025-09-14 15:30:05 - INFO - Eliminated Cowboys as loser for user Manuel
2025-09-14 15:30:06 - INFO - Successfully validated Week 2: 1 games updated
```

## Configuration

### Environment Variables
- **Database Path**: Configurable via `db_path` parameter
- **ESPN API**: Uses public ESPN API (no authentication required)
- **Timezone**: Handles timezone conversions for game times

### Customization
- **Validation Frequency**: Modify schedule in `run_validation_service()`
- **Team Name Mapping**: Add custom team name mappings for ESPN compatibility
- **Point System**: Modify point calculation logic in `calculate_user_points()`

## Deployment

### Production Setup
1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Database Setup**: Ensure SQLite database is properly initialized
3. **Service Start**: Validation service starts automatically with Flask app
4. **Monitoring**: Monitor log files for service health

### Development Testing
```bash
# Test specific week validation
python manual_validation.py --week 1

# Test current week validation
python manual_validation.py --current

# Check service logs
tail -f game_validator.log
```

## Troubleshooting

### Common Issues

#### ESPN API Errors
- **Symptom**: "Failed to fetch ESPN data"
- **Solution**: Check internet connectivity, ESPN API status
- **Workaround**: Use manual validation script

#### Database Lock Errors
- **Symptom**: "Database is locked"
- **Solution**: Ensure only one validation process is running
- **Workaround**: Restart Flask application

#### Team Name Mismatches
- **Symptom**: "No matching game found"
- **Solution**: Check team name consistency between ESPN and database
- **Workaround**: Add fuzzy matching rules

### Emergency Procedures

#### Manual Result Entry
If automatic validation fails, results can be manually entered:

1. **Stop Validation Service**: Restart Flask app without validation
2. **Manual Database Update**: Use SQL commands to update results
3. **Run Point Calculation**: Use manual validation script
4. **Restart Service**: Resume automatic validation

#### Service Recovery
If validation service crashes:

1. **Check Logs**: Review `game_validator.log` for errors
2. **Restart Flask App**: Service will restart automatically
3. **Manual Catch-up**: Run `python manual_validation.py --all`

## Security

### API Security
- **No Authentication**: ESPN API is public, no credentials stored
- **Rate Limiting**: Built-in delays to respect ESPN API limits
- **Error Isolation**: API failures don't affect main application

### Database Security
- **Local Access**: Validation service runs locally with database
- **Transaction Safety**: All updates use database transactions
- **Backup Friendly**: Service doesn't interfere with database backups

