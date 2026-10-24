from pydantic_settings import BaseSettings , SettingsConfigDict

class Setting(BaseSettings):
    APP_NAME:str = "AI CHAT BOT"
    GEMINI_API_KEY:str 
    DATABASE_URL:str
    
    model_config=SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    
settings = Setting()