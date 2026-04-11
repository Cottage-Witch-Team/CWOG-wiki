import json
import re
from abc import ABC, abstractmethod
from typing import Any

import ftb_snbt_lib as slib
import yaml

from scripts.core.entities import ConfigDocument, SourceFile


class BaseParser(ABC):
    supported_extensions: set[str] = set()

    @abstractmethod
    def parse(self, source_file: SourceFile) -> ConfigDocument:
        pass


class JsonParser(BaseParser):
    supported_extensions = {".json"}

    def parse(self, source_file: SourceFile) -> ConfigDocument:
        text = source_file.path.read_text(encoding="utf-8")
        data = json.loads(text)

        return ConfigDocument(
            title=source_file.stem,
            source_type="json",
            content=data,
            raw_text=text,
        )


class SnbtParser(BaseParser):
    supported_extensions = {".snbt"}

    def parse(self, source_file: SourceFile) -> ConfigDocument:
        text = source_file.path.read_text(encoding="utf-8")
        data = json.loads(json.dumps(slib.loads(text)))

        return ConfigDocument(
            title=source_file.stem,
            source_type="json",
            content=data,
            raw_text=text,
        )


class YamlParser(BaseParser):
    supported_extensions = {".yml", ".yaml"}

    def parse(self, source_file: SourceFile) -> ConfigDocument:
        text = source_file.path.read_text(encoding="utf-8")
        data = yaml.safe_load(text)

        return ConfigDocument(
            title=source_file.stem,
            source_type="yaml",
            content=data,
            raw_text=text,
        )


class JsParser(BaseParser):
    supported_extensions = {".js"}

    def parse(self, source_file: SourceFile, get_list: str | None = None) -> ConfigDocument:
        text = source_file.path.read_text(encoding="utf-8")

        data = {"raw": text}

        if get_list:
            data = data | {"list": self.__get_js_list_from_text(text, get_list)}

        return ConfigDocument(
            title=source_file.stem,
            source_type="js",
            content=data,
            raw_text=text,
        )

    def __get_js_list_from_text(self, text: str, search_string: str) -> list[Any] | None:
        search_string = re.escape(search_string)
        match = re.search(search_string + r"\s*=\s*\[(.*?)]", text, re.DOTALL)

        return re.findall(r'"(.*?)"', match.group(1)) if match else None
