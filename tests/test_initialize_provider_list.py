import importlib.util
import sys
import types
import json
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_module(relative, stubs=None, name="tested_module"):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(sys.modules, stubs or {}):
        spec.loader.exec_module(module)
    return module


def settings_stubs():
    settings = types.ModuleType("openplotterSettings")
    for name in ("conf", "platform", "language"):
        setattr(settings, name, types.SimpleNamespace())
    return {"openplotterSettings": settings, "ujson": json}


import tempfile


class FreshSettingsTest(unittest.TestCase):
    def module_for(self, directory):
        stubs = settings_stubs()
        stubs["openplotterSettings"].platform.Platform = lambda: types.SimpleNamespace(
            skDir=directory
        )
        return load_module("openplotterSignalkInstaller/editSettings.py", stubs)

    def test_add_first_connection_to_settings_without_providers(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "settings.json"
            path.write_text(json.dumps({"other": "preserve"}))
            settings = self.module_for(temp).EditSettings()
            self.assertFalse(settings.connectionIdExists("test"))
            self.assertTrue(
                settings.setNetworkConnection(
                    "test", "NMEA0183", "TCP", "localhost", "10110"
                )
            )
            result = json.loads(path.read_text())
            self.assertEqual(result["other"], "preserve")
            self.assertEqual(result["pipedProviders"][0]["id"], "test")

    def test_unreadable_json_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "settings.json"
            path.write_text("not valid JSON")
            settings = self.module_for(temp).EditSettings()
            self.assertEqual(settings.data, "")
            self.assertEqual(path.read_text(), "not valid JSON")

    def test_existing_providers_are_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "settings.json"
            path.write_text(json.dumps({"pipedProviders": [{"id": "existing"}]}))
            settings = self.module_for(temp).EditSettings()
            self.assertTrue(settings.connectionIdExists("existing"))
            self.assertEqual(len(settings.data["pipedProviders"]), 1)


if __name__ == "__main__":
    unittest.main()
