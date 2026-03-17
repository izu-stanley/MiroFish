"""
Configuration management
Loads from .env in project root
"""

import os
from dotenv import load_dotenv

# Path: MiroFish/.env (relative to backend/app/config.py)
project_root_env = os.path.join(os.path.dirname(__file__), '../../.env')

if os.path.exists(project_root_env):
    load_dotenv(project_root_env, override=True)
else:
    load_dotenv(override=True)


class Config:
    """Flask config"""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mirofish-secret-key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # JSON: allow non-ASCII (no \uXXXX escaping)
    JSON_AS_ASCII = False
    
    # Cursor Agent CLI - main brain (replaces Ollama/LLM)
    CURSOR_AGENT_PATH = os.environ.get('CURSOR_AGENT_PATH', 'cursor-agent')
    CURSOR_AGENT_TIMEOUT = int(os.environ.get('CURSOR_AGENT_TIMEOUT', '300'))

    # Local mode only - no Zep Cloud, no Ollama
    USE_LOCAL_MODE = True
    
    # File upload
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'md', 'txt', 'markdown'}
    
    # Text processing
    DEFAULT_CHUNK_SIZE = 500
    DEFAULT_CHUNK_OVERLAP = 50

    # Max entities for simulation agents
    MAX_ENTITY_LIMIT = int(os.environ.get('MAX_ENTITY_LIMIT', '50'))
    
    # OASIS simulation
    OASIS_DEFAULT_MAX_ROUNDS = int(os.environ.get('OASIS_DEFAULT_MAX_ROUNDS', '300'))
    OASIS_SIMULATION_DATA_DIR = os.path.join(os.path.dirname(__file__), '../uploads/simulations')
    
    # OASIS platform actions
    OASIS_TWITTER_ACTIONS = [
        'CREATE_POST', 'LIKE_POST', 'REPOST', 'FOLLOW', 'DO_NOTHING', 'QUOTE_POST'
    ]
    OASIS_REDDIT_ACTIONS = [
        'LIKE_POST', 'DISLIKE_POST', 'CREATE_POST', 'CREATE_COMMENT',
        'LIKE_COMMENT', 'DISLIKE_COMMENT', 'SEARCH_POSTS', 'SEARCH_USER',
        'TREND', 'REFRESH', 'DO_NOTHING', 'FOLLOW', 'MUTE'
    ]
    
    # Default language for prompts, profiles, and reports (en = English, zh = Chinese)
    DEFAULT_LANGUAGE = os.environ.get('MIROFISH_DEFAULT_LANGUAGE', 'en')
    
    # Report Agent
    REPORT_AGENT_MAX_TOOL_CALLS = int(os.environ.get('REPORT_AGENT_MAX_TOOL_CALLS', '15'))
    REPORT_AGENT_MAX_REFLECTION_ROUNDS = int(os.environ.get('REPORT_AGENT_MAX_REFLECTION_ROUNDS', '15'))
    REPORT_AGENT_TEMPERATURE = float(os.environ.get('REPORT_AGENT_TEMPERATURE', '0.5'))
    
    # Local graph storage
    LOCAL_GRAPH_STORAGE_DIR = os.path.join(os.path.dirname(__file__), '../uploads/local_graphs')
    
    @classmethod
    def validate(cls):
        """Validate required config"""
        errors = []
        import shutil
        agent = shutil.which(cls.CURSOR_AGENT_PATH)
        if not agent:
            errors.append(
                f"cursor-agent not found (CURSOR_AGENT_PATH={cls.CURSOR_AGENT_PATH}). "
                "Install: curl https://cursor.com/install -fsS | bash"
            )
        return errors

