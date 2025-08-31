from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # This tells Pydantic to load variables from a .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # SendGrid
    SENDGRID_API_KEY: str = ""
    SENDER_EMAIL: str = ""

    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

# Create a single instance of the settings to be used throughout the app
settings = Settings()