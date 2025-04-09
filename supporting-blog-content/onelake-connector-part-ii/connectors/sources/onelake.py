"""OneLake connector to retrieve data from datalakes"""

from functools import partial

from azure.identity import ClientSecretCredential
from azure.storage.filedatalake import DataLakeServiceClient

from connectors.source import BaseDataSource

ACCOUNT_NAME = "onelake"


class OneLakeDataSource(BaseDataSource):
    """OneLake"""

    name = "OneLake"
    service_type = "onelake"
    incremental_sync_enabled = True

    def __init__(self, configuration):
        """Set up the connection to the azure base client

        Args:
            configuration (DataSourceConfiguration): Object of DataSourceConfiguration class.
        """
        super().__init__(configuration=configuration)
        self.tentant_id = self.configuration["tentant_id"]
        self.client_id = self.configuration["client_id"]
        self.client_secret = self.configuration["client_secret"]
        self.workspace_name = self.configuration["workspace_name"]
        self.data_path = self.configuration["data_path"]

    @classmethod
    def get_default_configuration(cls):
        """Get the default configuration for OneLake

        Returns:
            dictionary: Default configuration
        """
        return {
            "tentant_id": {
                "label": "OneLake tenant id",
                "order": 1,
                "type": "str",
            },
            "client_id": {
                "label": "OneLake client id",
                "order": 2,
                "type": "str",
            },
            "client_secret": {
                "label": "OneLake client secret",
                "order": 3,
                "type": "str",
                "sensitive": True,  # Hide sensitive data like passwords or secrets
            },
            "workspace_name": {
                "label": "OneLake workspace name",
                "order": 4,
                "type": "str",
            },
            "data_path": {
                "label": "OneLake data path",
                "tooltip": "Path in format <DataLake>.Lakehouse/files/<Folder path>",
                "order": 5,
                "type": "str",
            },
            "account_name": {
                "tooltip": "In the most cases is 'onelake'",
                "default_value": ACCOUNT_NAME,
                "label": "Account name",
                "order": 6,
                "type": "str",
            },
        }

    async def ping(self):
        """Verify the connection with OneLake"""

        self._logger.info("Generating file system client...")

        try:
            await self._get_directory_paths(self.configuration["data_path"])
            self._logger.info("Connection to OneLake successful")

        except Exception:
            self._logger.exception("Error while connecting to OneLake.")
            raise

    def _get_account_url(self):
        """Get the account URL for OneLake

        Returns:
            str: Account URL
        """

        return f"https://{self.configuration['account_name']}.dfs.fabric.microsoft.com"

    def _get_token_credentials(self):
        """Get the token credentials for OneLake

        Returns:
            obj: Token credentials
        """

        tentant_id = self.configuration["tentant_id"]
        client_id = self.configuration["client_id"]
        client_secret = self.configuration["client_secret"]

        try:
            return ClientSecretCredential(tentant_id, client_id, client_secret)
        except Exception as e:
            self._logger.error(f"Error while getting token credentials: {e}")
            raise

    def _get_service_client(self):
        """Get the service client for OneLake

        Returns:
            obj: Service client
        """

        try:
            return DataLakeServiceClient(
                account_url=self._get_account_url(),
                credential=self._get_token_credentials(),
            )
        except Exception as e:
            self._logger.error(f"Error while getting service client: {e}")
            raise

    def _get_file_system_client(self):
        """Get the file system client for OneLake

        Returns:
            obj: File system client
        """
        try:
            return self._get_service_client().get_file_system_client(
                self.configuration["workspace_name"]
            )
        except Exception as e:
            self._logger.error(f"Error while getting file system client: {e}")
            raise

    def _get_directory_client(self):
        """Get the directory client for OneLake

        Returns:
            obj: Directory client
        """

        try:
            return self._get_file_system_client().get_directory_client(
                self.configuration["data_path"]
            )
        except Exception as e:
            self._logger.error(f"Error while getting directory client: {e}")
            raise

    async def _get_file_client(self, file_name):
        """Get file client from OneLake

        Args:
            file_name (str): name of the file

        Returns:
            obj: File client
        """

        try:
            return self._get_directory_client().get_file_client(file_name)
        except Exception as e:
            self._logger.error(f"Error while getting file client: {e}")
            raise

    async def _get_directory_paths(self, directory_path):
        """List directory paths from data lake

        Args:
            directory_path (str): Directory path

        Returns:
            list: List of paths
        """

        try:
            paths = self._get_file_system_client().get_paths(path=directory_path)

            return paths
        except Exception as e:
            self._logger.error(f"Error while getting directory paths: {e}")
            raise

    async def format_file(self, file_client):
        """Format file_client to be processed

        Args:
            file_client (obj): File object

        Returns:
            dict: Formatted file
        """

        try:
            file_properties = file_client.get_file_properties()

            return {
                "_id": f"{file_client.file_system_name}_{file_properties.name.split('/')[-1]}",
                "name": file_properties.name.split("/")[-1],
                "created_at": file_properties.creation_time.isoformat(),
                "_timestamp": file_properties.last_modified.isoformat(),
                "size": file_properties.size,
            }
        except Exception as e:
            self._logger.error(
                f"Error while formatting file or getting file properties: {e}"
            )
            raise

    async def download_file(self, file_client):
        """Download file from OneLake

        Args:
            file_client (obj): File client

        Returns:
            generator: File stream
        """

        try:
            download = file_client.download_file()
            stream = download.chunks()

            for chunk in stream:
                yield chunk
        except Exception as e:
            self._logger.error(f"Error while downloading file: {e}")
            raise

    async def get_content(self, file_name, doit=None, timestamp=None):
        """Obtains the file content for the specified file in `file_name`.

        Args:
            file_name (obj): The file name to process to obtain the content.
            timestamp (timestamp, optional): Timestamp of blob last modified. Defaults to None.
            doit (boolean, optional): Boolean value for whether to get content or not. Defaults to None.

        Returns:
            str: Content of the file or None if not applicable.
        """

        if not doit:
            return

        file_client = await self._get_file_client(file_name)
        file_properties = file_client.get_file_properties()
        file_extension = self.get_file_extension(file_name)

        doc = {
            "_id": f"{file_client.file_system_name}_{file_properties.name}",  # workspacename_data_path
            "name": file_properties.name.split("/")[-1],
            "_timestamp": file_properties.last_modified,
            "created_at": file_properties.creation_time,
        }

        can_be_downloaded = self.can_file_be_downloaded(
            file_extension=file_extension,
            filename=file_properties.name,
            file_size=file_properties.size,
        )

        if not can_be_downloaded:
            return doc

        extracted_doc = await self.download_and_extract_file(
            doc=doc,
            source_filename=file_properties.name.split("/")[-1],
            file_extension=file_extension,
            download_func=partial(self.download_file, file_client),
        )

        return extracted_doc if extracted_doc is not None else doc

    async def prepare_files(self, doc_paths):
        """Prepare files for processing

        Args:
            doc_paths (list): List of paths extracted from OneLake

        Yields:
            tuple: File document and partial function to get content
        """

        for path in doc_paths:
            file_name = path.name.split("/")[-1]
            field_client = await self._get_file_client(file_name)

            yield self.format_file(field_client)

    async def get_docs(self, filtering=None):
        """Get documents from OneLake and index them

        Yields:
            tuple: dictionary with meta-data of each file and a partial function to get the file content.
        """

        directory_paths = await self._get_directory_paths(
            self.configuration["data_path"]
        )

        async for file in self.prepare_files(directory_paths):
            file_dict = await file
            yield file_dict, partial(self.get_content, file_dict["name"])
