import os

from dotenv import load_dotenv


class EnvironmentVariables:
    def __init__(self) -> None:
        _ = load_dotenv(override=True)

    @property
    def DATABASE_URL(self) -> str:
        database_url = os.getenv("DATABASE_URL")
        assert database_url, "DATABASE_URL should not be empty."
        return str(database_url)

    @property
    def MINIMUM_POOL_SIZE(self) -> int:
        return int(os.getenv("MINIMUM_POOL_SIZE") or 1)

    @property
    def MAXIMUM_POOL_SIZE(self) -> int:
        return int(os.getenv("MAXIMUM_POOL_SIZE") or 1)

    @property
    def DEPLOY_MODE(self) -> str:
        deploy_mode = os.getenv("DEPLOY_MODE") or "PRODUCTION"
        return str(deploy_mode)


environment_variables = EnvironmentVariables()
