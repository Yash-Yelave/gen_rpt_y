from __future__ import annotations
import logging
import sys
from datetime import datetime

# ANSI colors
COLOR_RESET = "\033[0m"
COLOR_BLUE = "\033[34m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_RED = "\033[31m"
COLOR_MAGENTA = "\033[35m"
COLOR_CYAN = "\033[36m"
COLOR_GRAY = "\033[90m"

class CustomFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        
        # Add colors based on tags
        if msg.startswith("[PLAN]"):
            msg = f"{COLOR_CYAN}{msg}{COLOR_RESET}"
        elif msg.startswith("[SEARCH]"):
            msg = f"{COLOR_BLUE}{msg}{COLOR_RESET}"
        elif msg.startswith("[SYNTHESIS]"):
            msg = f"{COLOR_MAGENTA}{msg}{COLOR_RESET}"
        elif msg.startswith("[BRANDING]"):
            msg = f"{COLOR_YELLOW}{msg}{COLOR_RESET}"
        elif msg.startswith("[VISUALS]"):
            msg = f"{COLOR_GREEN}{msg}{COLOR_RESET}"
        elif msg.startswith("[RENDER]"):
            msg = f"{COLOR_CYAN}{msg}{COLOR_RESET}"
        elif msg.startswith("[QA]"):
            msg = f"{COLOR_YELLOW}{msg}{COLOR_RESET}"
        elif msg.startswith("[ARCHIVE]"):
            msg = f"{COLOR_BLUE}{msg}{COLOR_RESET}"
        elif msg.startswith("[SUCCESS]"):
            msg = f"{COLOR_GREEN}{msg}{COLOR_RESET}"
        elif msg.startswith("[INIT]"):
            msg = f"{COLOR_MAGENTA}{msg}{COLOR_RESET}"
        elif msg.startswith("[WARNING]"):
            msg = f"{COLOR_YELLOW}{msg}{COLOR_RESET}"
        elif msg.startswith("[ERROR]") or msg.startswith("[FAIL]"):
            msg = f"{COLOR_RED}{msg}{COLOR_RESET}"
            
        return msg

def setup_logger():
    logger = logging.getLogger("gen_rpt")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(CustomFormatter("%(message)s"))
        logger.addHandler(handler)
        
    return logger

logger = setup_logger()

def log_stage(stage: str, message: str):
    logger.info(f"[{stage}] {message}")

def log_success(message: str):
    logger.info(f"[SUCCESS] {message}")

def log_warning(message: str):
    logger.info(f"[WARNING] {message}")

def log_error(message: str):
    logger.info(f"[ERROR] {message}")

def log_info(message: str):
    logger.info(message)
