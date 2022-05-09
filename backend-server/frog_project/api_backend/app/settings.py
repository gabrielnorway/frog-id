from .secrets import Secrets


class Settings:
    # Database ip/hostname
    database_hostname = "db"
    # Database name
    database_name = "frog_db"

    # Default users
    default_users = [
        {"username": "admin", "password": Secrets.admin_user_password, "is_admin": True},
        {"username": "frog", "password": "kermit"}
    ]


