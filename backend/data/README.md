# Backend Data Directory

This directory contains application data storage for the PRO-PAD backend.

## Directory Structure

```
backend/data/
├── audit/          # Audit logs and activity tracking
├── policy/         # Policy settings and configurations
└── settings/       # UI and application settings
```

## File Formats

- All data is stored in JSON format for easy portability
- Automatic backups are created before updates
- Audit logs include timestamps and user information

## Data Files

### Audit Directory
- `audit_log.json` - Main audit log file
- `audit_log.json.backup_*` - Timestamped backups

### Policy Directory
- `settings.json` - Policy settings
- `targets.json` - Revenue targets
- `interventions.json` - Policy interventions

### Settings Directory
- `ui_settings.json` - UI customization settings
- `variables.json` - Variable configurations
- `system.json` - System settings

## Security Notes

- This directory should be included in backups
- Consider implementing encryption for sensitive data
- Regular cleanup of old backup files is recommended
