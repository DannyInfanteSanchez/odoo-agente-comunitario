import os
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

class Settings:
    ODOO_URL: str = os.getenv("ODOO_URL", "http://localhost:8069")
    ODOO_DB: str = os.getenv("ODOO_DB", "postgres")
    ODOO_USERNAME: str = os.getenv("ODOO_USERNAME", "admin")
    ODOO_PASSWORD: str = os.getenv("ODOO_PASSWORD", "odoo_secure_pass")
    API_BEARER_TOKEN: str = os.getenv("API_BEARER_TOKEN", "super-secret-token-for-flutter-app")

settings = Settings()
