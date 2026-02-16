from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool=False

class DevConfig(GlobalConfig):
    model_config = {
        "env_prefix": "DEV_"
    }


class TestConfig(GlobalConfig):
    DATABASE_URL: str = 'sqlite:///test.db' 
    DB_FORCE_ROLL_BACK: bool= True
    model_config = {
        "env_prefix": "TEST_"
    }

class ProdConfig(GlobalConfig):
    
    model_config = {
        "env_prefix": "PROD_"
    }

@lru_cache()
def get_config(env_state: str):

    configs = {
        "dev": DevConfig, 
        'prod': ProdConfig, 
        'test': TestConfig
    }
    return configs[env_state]()

env_state = BaseConfig().ENV_STATE or 'dev'
config = get_config(env_state)