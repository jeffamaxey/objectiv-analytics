"""
Copyright 2021 Objectiv B.V.
"""

import os
from typing import NamedTuple, Optional

# All settings that are controlled through environment variables are listed at the top here, for a
# complete overview.
# Most of these settings should not be accessed by the constants here, but through the functions defined
# below (e.g. get_config_output())

SCHEMA_EXTENSION_EVENT = os.environ.get('SCHEMA_EXTENSION_EVENT')
SCHEMA_EXTENSION_CONTEXT = os.environ.get('SCHEMA_EXTENSION_CONTEXT')

# Whether to run in sync mode (default) or async-mode.
_ASYNC_MODE = os.environ.get('ASYNC_MODE', '') == 'true'

# ### Postgres values.
# We define some default values here. DO NOT put actual passwords in here
_PG_DATABASE_NAME = os.environ.get('POSTGRES_DB', 'objectiv')
_PG_HOSTNAME = os.environ.get('POSTGRES_HOSTNAME', 'localhost')
_PG_PORT = os.environ.get('POSTGRES_PORT', '5432')
_PG_USER = os.environ.get('POSTGRES_USER', 'objectiv')
_PG_PASSWORD = os.environ.get('POSTGRES_PASSWORD', '0bj3ctiv')

# ### AWS S3 values, for writing data to S3.
# default access keys to an empty string, otherwise the boto library will default ot user defaults.
_AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
_AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
_AWS_REGION = os.environ.get('AWS_REGION', 'eu-west-1')
_AWS_BUCKET = os.environ.get('AWS_BUCKET', '')
_AWS_S3_PREFIX = os.environ.get('AWS_S3_PREFIX', 'test-prefix')

# ### Setting for outputting data to the filesystem
_JSON_OUTPUT_DIR = os.environ.get('JSON_OUTPUT_DIR')

# Maximum number of events that a worker will process in a single batch
WORKER_BATCH_SIZE = 200
# Time to sleep, if there is no work to do for the workers
WORKER_SLEEP_SECONDS = 5


class AwsOutputConfig(NamedTuple):
    access_key_id: str
    secret_access_key: str
    region: str
    bucket: str
    s3_prefix: str


class FileSystemOutputConfig(NamedTuple):
    path: str


class PostgresConfig(NamedTuple):
    hostname: str
    port: int
    database_name: str
    user: str
    password: str


class OutputConfig(NamedTuple):
    postgres: Optional[PostgresConfig]
    aws: Optional[AwsOutputConfig]
    file_system: Optional[FileSystemOutputConfig]


class CollectorConfig(NamedTuple):
    async_mode: bool
    output: OutputConfig


def get_config_output_aws() -> Optional[AwsOutputConfig]:
    if _AWS_REGION and _AWS_ACCESS_KEY_ID and _AWS_SECRET_ACCESS_KEY and _AWS_BUCKET and _AWS_S3_PREFIX:
        return AwsOutputConfig(
            access_key_id=_AWS_ACCESS_KEY_ID,
            secret_access_key=_AWS_SECRET_ACCESS_KEY,
            region=_AWS_REGION,
            bucket=_AWS_BUCKET,
            s3_prefix=_AWS_S3_PREFIX
        )
    return None


def get_config_output_file_system() -> Optional[FileSystemOutputConfig]:
    if _JSON_OUTPUT_DIR:
        return FileSystemOutputConfig(path=_JSON_OUTPUT_DIR)
    return None


def get_config_postgres() -> Optional[PostgresConfig]:
    return PostgresConfig(
        hostname=_PG_HOSTNAME,
        port=int(_PG_PORT),
        database_name=_PG_DATABASE_NAME,
        user=_PG_USER,
        password=_PG_PASSWORD
    )


def get_config_output() -> OutputConfig:
    """ Get the Collector's output settings. Raises an error if none of the outputs are configured. """
    output_config = OutputConfig(
        postgres=get_config_postgres(),
        aws=get_config_output_aws(),
        file_system=get_config_output_file_system()
    )
    if not output_config.postgres and not output_config.aws and not output_config.file_system:
        raise Exception('No output configured. At least configure either Postgres, S3 or FileSystem '
                        'output.')
    return output_config


# creating these configuration structures is not heavy, but it's pointless to do it for each request.
# so we have some super simple caching here
# TODO: initialize configuration at startup
_CACHED_COLLECTOR_CONFIG: Optional[OutputConfig] = None


def get_collector_config() -> CollectorConfig:
    """ Get the Collector Configuration. Cached after first invocation """
    global _CACHED_COLLECTOR_CONFIG
    if not _CACHED_COLLECTOR_CONFIG:
        _CACHED_COLLECTOR_CONFIG = CollectorConfig(
            async_mode=_ASYNC_MODE,
            output=get_config_output()
        )
    return _CACHED_COLLECTOR_CONFIG
