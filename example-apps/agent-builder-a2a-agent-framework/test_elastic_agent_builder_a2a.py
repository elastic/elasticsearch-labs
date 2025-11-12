import unittest
from unittest.mock import patch
from dotenv import load_dotenv
import os
import asyncio
from pathlib import Path
import importlib.util


class test_main_function(unittest.TestCase):
    def setUp(self):
        # Replace placeholder values with .env values
        load_dotenv()

        self.test_file = Path("elastic_agent_builder_a2a.py")
        self.backup_file = Path("elastic_agent_builder_a2a.py.backup")

        if self.test_file.exists():
            self.original_content = self.test_file.read_text()
            self.backup_file.write_text(self.original_content)

        self.es_agent_url = os.getenv("ES_AGENT_URL")
        self.es_api_key = os.getenv("ES_API_KEY")
        content = self.test_file.read_text()
        modified_content = content.replace(
            "<YOUR-ELASTIC-AGENT-BUILDER-URL>", self.es_agent_url
        )
        modified_content = modified_content.replace(
            "<YOUR-ELASTIC-API-KEY>", self.es_api_key
        )
        self.test_file.write_text(modified_content)

        # Import the modified module
        spec = importlib.util.spec_from_file_location(
            "elastic_agent_builder_a2a", self.test_file
        )
        self.user_input_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.user_input_module)

    def tearDown(self):
        if self.backup_file.exists():
            self.test_file.write_text(self.backup_file.read_text())
            self.backup_file.unlink()

    @patch("builtins.input", return_value="hello world")
    @patch("builtins.print")
    def test_main_input(self, mock_print, mock_input):
        # Run test
        asyncio.run(self.user_input_module.main())
        mock_print.assert_called_with("Hello World! 🌎")


if __name__ == "__main__":
    unittest.main()
