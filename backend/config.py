"""
Configuration management for the backend service.
Loads and validates environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration"""
    
    # Pocket Option Configuration
    POCKET_OPTION_SSID = os.getenv('POCKET_OPTION_SSID')
    POCKET_OPTION_UID = int(os.getenv('POCKET_OPTION_UID', '0'))
    POCKET_OPTION_IS_DEMO = os.getenv('POCKET_OPTION_IS_DEMO', '1') == '1'
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', 'binary-fc0fb')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json')
    
    # Application Configuration
    UPDATE_THROTTLE_SECONDS = float(os.getenv('UPDATE_THROTTLE_SECONDS', '1.0'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    HEALTH_CHECK_PORT = int(os.getenv('HEALTH_CHECK_PORT', '8080'))
    
    # Reconnection Configuration
    RECONNECT_DELAY_SECONDS = 5
    MAX_RECONNECT_ATTEMPTS = 10
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        errors = []
        
        if not cls.POCKET_OPTION_SSID:
            errors.append("POCKET_OPTION_SSID environment variable is required")
        
        if not os.path.exists(cls.GOOGLE_APPLICATION_CREDENTIALS):
            errors.append(f"Firebase credentials file not found: {cls.GOOGLE_APPLICATION_CREDENTIALS}")
        
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return True


# Validate configuration on import
Config.validate()
