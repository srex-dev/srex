import logging
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Any

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure audit logger
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# Create file handler
audit_file = log_dir / "audit.log"
file_handler = logging.FileHandler(audit_file)
file_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handler to logger
audit_logger.addHandler(file_handler)

def log_security_event(
    event_type: str,
    user: str,
    action: str,
    details: Dict[str, Any],
    success: bool = True
) -> None:
    """Log a security-related event."""
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user": user,
        "action": action,
        "details": details,
        "success": success
    }
    
    audit_logger.info(json.dumps(event)) 