import yaml
from pathlib import Path


class YamlConfig:
    def __init__(self):
        self._config_file = Path("config.yml")

    def get_value(self, key: str) -> any:
        data = self._read_config()
        if key in data:
            return data[key]

        return None

    def add_value(self, key, value):
        data = self._read_config()
        if key not in data:
            data[key] = value
        self._write_config(data)

    def update_value(self, key: str, value) -> None:
        data = self._read_config()
        if key in data:
            data[key] = value
        self._write_config(data)

    def delete_value(self, key: str) -> None:
        data = self._read_config()
        if key in data:
            del data[key]
        self._write_config(data)

    def _write_config(self, data: dict) -> None:
        with open(self._config_file, "w") as file:
            yaml.dump(data, file)

    def _read_config(self) -> dict:
        if not self._config_file.is_file():
            self._write_config(data={})
        with open(self._config_file, "r") as file:
            return yaml.safe_load(file)
