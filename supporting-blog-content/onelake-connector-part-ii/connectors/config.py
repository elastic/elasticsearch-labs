#
# Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
# or more contributor license agreements. Licensed under the Elastic License 2.0;
# you may not use this file except in compliance with the Elastic License 2.0.
#

import os

from envyaml import EnvYAML

from connectors.logger import logger

DEFAULT_ELASTICSEARCH_MAX_RETRIES = 5
DEFAULT_ELASTICSEARCH_RETRY_INTERVAL = 10

DEFAULT_MAX_FILE_SIZE = 10485760  # 10MB


def load_config(config_file):
    logger.info(f"Loading config from {config_file}")
    yaml_config = EnvYAML(config_file, flatten=False).export()
    nested_yaml_config = {}
    for key, value in yaml_config.items():
        _nest_configs(nested_yaml_config, key, value)
    configuration = dict(_merge_dicts(_default_config(), nested_yaml_config))
    _ent_search_config(configuration)

    return configuration


def add_defaults(config, default_config=None):
    if default_config is None:
        default_config = _default_config()
    configuration = dict(_merge_dicts(default_config, config))
    return configuration


# Left - in Enterprise Search; Right - in Connectors
config_mappings = {
    "elasticsearch.host": "elasticsearch.host",
    "elasticsearch.username": "elasticsearch.username",
    "elasticsearch.password": "elasticsearch.password",
    "elasticsearch.headers": "elasticsearch.headers",
    "log_level": "service.log_level",
}

# Enterprise Search uses Ruby and is in lower case always, so hacking it here for now
# Ruby-supported log levels: 'debug', 'info', 'warn', 'error', 'fatal', 'unknown'
# Python-supported log levels: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'NOTSET'
log_level_mappings = {
    "debug": "DEBUG",
    "info": "INFO",
    "warn": "WARNING",
    "error": "ERROR",
    "fatal": "CRITICAL",
    "unknown": "NOTSET",
}


def _default_config():
    return {
        "elasticsearch": {
            "host": "http://localhost:9200",
            "username": "elastic",
            "password": "changeme",
            "ssl": True,
            "verify_certs": True,
            "bulk": {
                "queue_max_size": 1024,
                "queue_max_mem_size": 25,
                "queue_refresh_interval": 1,
                "queue_refresh_timeout": 600,
                "display_every": 100,
                "chunk_size": 1000,
                "max_concurrency": 5,
                "chunk_max_mem_size": 5,
                "max_retries": DEFAULT_ELASTICSEARCH_MAX_RETRIES,
                "retry_interval": DEFAULT_ELASTICSEARCH_RETRY_INTERVAL,
                "concurrent_downloads": 10,
                "enable_operations_logging": False,
            },
            "max_retries": DEFAULT_ELASTICSEARCH_MAX_RETRIES,
            "retry_interval": DEFAULT_ELASTICSEARCH_RETRY_INTERVAL,
            "retry_on_timeout": True,
            "request_timeout": 120,
            "max_wait_duration": 120,
            "initial_backoff_duration": 1,
            "backoff_multiplier": 2,
            "log_level": "info",
            "feature_use_connectors_api": True,
        },
        "service": {
            "idling": 30,
            "heartbeat": 300,
            "preflight_max_attempts": 10,
            "preflight_idle": 30,
            "max_errors": 20,
            "max_errors_span": 600,
            "max_concurrent_content_syncs": 1,
            "max_concurrent_access_control_syncs": 1,
            "max_file_download_size": DEFAULT_MAX_FILE_SIZE,
            "job_cleanup_interval": 300,
            "log_level": "INFO",
        },
        "sources": {
            "onelake": "connectors.sources.onelake:OneLakeDataSource",
            "azure_blob_storage": "connectors.sources.azure_blob_storage:AzureBlobStorageDataSource",
            "box": "connectors.sources.box:BoxDataSource",
            "confluence": "connectors.sources.confluence:ConfluenceDataSource",
            "dir": "connectors.sources.directory:DirectoryDataSource",
            "dropbox": "connectors.sources.dropbox:DropboxDataSource",
            "github": "connectors.sources.github:GitHubDataSource",
            "gmail": "connectors.sources.gmail:GMailDataSource",
            "google_cloud_storage": "connectors.sources.google_cloud_storage:GoogleCloudStorageDataSource",
            "google_drive": "connectors.sources.google_drive:GoogleDriveDataSource",
            "graphql": "connectors.sources.graphql:GraphQLDataSource",
            "jira": "connectors.sources.jira:JiraDataSource",
            "microsoft_teams": "connectors.sources.microsoft_teams:MicrosoftTeamsDataSource",
            "mongodb": "connectors.sources.mongo:MongoDataSource",
            "mssql": "connectors.sources.mssql:MSSQLDataSource",
            "mysql": "connectors.sources.mysql:MySqlDataSource",
            "network_drive": "connectors.sources.network_drive:NASDataSource",
            "notion": "connectors.sources.notion:NotionDataSource",
            "onedrive": "connectors.sources.onedrive:OneDriveDataSource",
            "oracle": "connectors.sources.oracle:OracleDataSource",
            "outlook": "connectors.sources.outlook:OutlookDataSource",
            "postgresql": "connectors.sources.postgresql:PostgreSQLDataSource",
            "redis": "connectors.sources.redis:RedisDataSource",
            "s3": "connectors.sources.s3:S3DataSource",
            "salesforce": "connectors.sources.salesforce:SalesforceDataSource",
            "servicenow": "connectors.sources.servicenow:ServiceNowDataSource",
            "sharepoint_online": "connectors.sources.sharepoint_online:SharepointOnlineDataSource",
            "sharepoint_server": "connectors.sources.sharepoint_server:SharepointServerDataSource",
            "slack": "connectors.sources.slack:SlackDataSource",
            "zoom": "connectors.sources.zoom:ZoomDataSource",
        },
    }


def _ent_search_config(configuration):
    if "ENT_SEARCH_CONFIG_PATH" not in os.environ:
        return
    logger.info("Found ENT_SEARCH_CONFIG_PATH, loading ent-search config")
    ent_search_config = EnvYAML(os.environ["ENT_SEARCH_CONFIG_PATH"])
    for es_field in config_mappings.keys():
        if es_field not in ent_search_config:
            continue

        connector_field = config_mappings[es_field]
        es_field_value = ent_search_config[es_field]

        if es_field == "log_level":
            if es_field_value not in log_level_mappings:
                msg = f"Unexpected log level: {es_field_value}. Allowed values: {', '.join(log_level_mappings.keys())}"
                raise ValueError(msg)
            es_field_value = log_level_mappings[es_field_value]

        _nest_configs(configuration, connector_field, es_field_value)

        logger.debug(f"Overridden {connector_field}")


def _nest_configs(configuration, field, value):
    """
    Update configuration field value taking into account the nesting.

    Configuration is a hash of hashes, so we need to dive inside to do proper assignment.

    E.g. _nest_config({}, "elasticsearch.bulk.queuesize", 20) will result in the following config:
    {
        "elasticsearch": {
            "bulk": {
                "queuesize": 20
            }
        }
    }
    """
    subfields = field.split(".")
    last_key = subfields[-1]

    current_leaf = configuration
    for subfield in subfields[:-1]:
        if subfield not in current_leaf:
            current_leaf[subfield] = {}
        current_leaf = current_leaf[subfield]

    if isinstance(current_leaf.get(last_key), dict):
        current_leaf[last_key] = dict(_merge_dicts(current_leaf[last_key], value))
    else:
        current_leaf[last_key] = value


def _merge_dicts(hsh1, hsh2):
    for k in set(hsh1.keys()).union(hsh2.keys()):
        if k in hsh1 and k in hsh2:
            if isinstance(hsh1[k], dict) and isinstance(
                hsh2[k], dict
            ):  # only merge objects
                yield (k, dict(_merge_dicts(hsh1[k], hsh2[k])))
            else:
                yield (k, hsh2[k])
        elif k in hsh1:
            yield (k, hsh1[k])
        else:
            yield (k, hsh2[k])


class DataSourceFrameworkConfig:
    """
    The configs that will be exposed to DataSource instances.
    This abstraction prevents DataSource instances from having access to all configuration, while also
    preventing them from requiring substantial changes to access new configs that may be added.
    """

    def __init__(self, max_file_size):
        """
        Should not be called directly. Use the Builder.
        """
        self.max_file_size = max_file_size

    class Builder:
        def __init__(self):
            self.max_file_size = DEFAULT_MAX_FILE_SIZE

        def with_max_file_size(self, max_file_size):
            self.max_file_size = max_file_size
            return self

        def build(self):
            return DataSourceFrameworkConfig(self.max_file_size)
