"""
Application configuration for the Healthcare / Medical Records system.
"""

class Config:
    """
    Base configuration class.
    """
    DEBUG: bool = False
    TESTING: bool = False
    DATABASE_URL: str = "sqlite:///./medical_records.db"
    SECRET_KEY: str = "supersecretkey_for_dev_do_not_use_in_prod"

    # TODO: Use Copilot Agent Mode to refactor this class to load configurations dynamically from environment variables or a .env file.

class DevelopmentConfig(Config):
    """
    Development specific configuration.
    """
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./dev_medical_records.db"
    # TODO: Add specific development-only settings, e.g., logging level, external API keys for testing.

class ProductionConfig(Config):
    """
    Production specific configuration.
    """
    DATABASE_URL: str = "postgresql://user:password@host:port/prod_medical_records"
    SECRET_KEY: str = "${PROD_SECRET_KEY}" # Should be loaded from environment
    # TODO: Refactor using @workspace context to ensure all production security best practices are applied (e.g., proper secret management).
    # TODO: Implement robust logging configurations for production environments.

class TestingConfig(Config):
    """
    Testing specific configuration.
    """
    TESTING: bool = True
    DATABASE_URL: str = "sqlite:///./test_medical_records.db"
    # TODO: Use Copilot to add configuration for in-memory databases for faster tests.

# A simple way to get the current configuration based on an environment variable
def get_config(env: str = "development"):
    if env == "production":
        return ProductionConfig
    elif env == "testing":
        return TestingConfig
    else:
        return DevelopmentConfig

# Example usage:
# current_config = get_config(os.environ.get("FLASK_ENV", "development"))
