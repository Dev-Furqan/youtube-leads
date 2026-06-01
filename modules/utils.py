import os
import json
import logging
from datetime import datetime

# Define base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
THUMBNAILS_DIR = os.path.join(DATA_DIR, "thumbnails")
EXPORTS_DIR = os.path.join(DATA_DIR, "exports")
RAW_API_DIR = os.path.join(DATA_DIR, "raw_api")
PROCESSED_CHANNELS_FILE = os.path.join(DATA_DIR, "processed_channels.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# In-memory log buffer for Streamlit UI
class StreamlitLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = []

    def emit(self, record):
        log_entry = self.format(record)
        self.logs.append(log_entry)
        # Cap at 500 lines to prevent memory leaks
        if len(self.logs) > 500:
            self.logs.pop(0)

    def get_logs(self):
        return "\n".join(self.logs)

    def clear(self):
        self.logs.clear()

streamlit_log_handler = StreamlitLogHandler()

def setup_directories():
    """Ensure all required directories exist."""
    for directory in [DATA_DIR, THUMBNAILS_DIR, EXPORTS_DIR, RAW_API_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)

def setup_logging():
    """Setup logging to file and memory buffer."""
    setup_directories()
    
    logger = logging.getLogger("yt_lead_bot")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if already set up
    if not logger.handlers:
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
        
        # File handler
        log_file = os.path.join(DATA_DIR, "bot.log")
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Streamlit memory handler
        streamlit_log_handler.setFormatter(formatter)
        logger.addHandler(streamlit_log_handler)
        
        # Also console handler for debug
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger

logger = setup_logging()

def load_config():
    """Load configuration from config.json."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config.json: {e}")
    return {}

def save_config(config_data):
    """Save configuration to config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        logger.info("Configuration updated successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to save config.json: {e}")
        return False

def load_processed_channels():
    """Load list of already processed channel IDs."""
    if os.path.exists(PROCESSED_CHANNELS_FILE):
        try:
            with open(PROCESSED_CHANNELS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load processed channels: {e}")
    return {}

def mark_channel_processed(channel_id, channel_name):
    """Add a channel ID to the processed list with metadata."""
    processed = load_processed_channels()
    processed[channel_id] = {
        "channel_name": channel_name,
        "processed_at": datetime.now().isoformat()
    }
    try:
        with open(PROCESSED_CHANNELS_FILE, "w", encoding="utf-8") as f:
            json.dump(processed, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save processed channel {channel_id}: {e}")

def clear_processed_channels():
    """Clear the duplicate tracker file."""
    try:
        if os.path.exists(PROCESSED_CHANNELS_FILE):
            os.remove(PROCESSED_CHANNELS_FILE)
            logger.info("Duplicate tracker cleared.")
        return True
    except Exception as e:
        logger.error(f"Failed to clear processed channels file: {e}")
        return False

def get_streamlit_logs():
    """Get buffered logs as a string."""
    return streamlit_log_handler.get_logs()

def clear_streamlit_logs():
    """Clear memory logs."""
    streamlit_log_handler.clear()
