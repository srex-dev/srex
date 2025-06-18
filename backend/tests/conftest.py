import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set up test environment variables
os.environ["SREX_ENV"] = "test"
os.environ["SREX_CONFIG_DIR"] = str(backend_dir / "config") 