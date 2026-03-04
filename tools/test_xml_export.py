"""Tests for XML export module."""

import os
import tempfile
import pytest
from lxml import etree
from parser import load_dbc, list_messages
from xml_export import export_config

DBC_PATH = os.path.join(os.path.dirname(__file__), "..", "dbc", "SensoricSolutionsOMSRace.dbc")


def _make_mappings():
    db = load_dbc(DBC_PATH)
    return [
        {"message": msg, "signal": sig, "topic": f"/{msg['name'].lower()}/{sig['name'].lower()}"}
        for msg in list_messages(db) for sig in msg["signals"]
    ]


@pytest.fixture()
def xml_path():
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
        path = f.name
    yield path
    os.unlink(path)


def test_export_creates_file(xml_path):
    export_config(_make_mappings(), xml_path)
    assert os.path.getsize(xml_path) > 0


def test_export_valid_xml(xml_path):
    export_config(_make_mappings(), xml_path)
    assert etree.parse(xml_path).getroot().tag == "bridge"


def test_export_message_count(xml_path):
    export_config(_make_mappings(), xml_path)
    assert len(etree.parse(xml_path).findall(".//message")) == 5


def test_export_signal_attributes(xml_path):
    export_config(_make_mappings(), xml_path)
    for sig in etree.parse(xml_path).findall(".//signal"):
        for attr in ("name", "start_bit", "length", "topic", "scale"):
            assert attr in sig.attrib


def test_export_empty_mappings(xml_path):
    export_config([], xml_path)
    assert len(etree.parse(xml_path).findall(".//message")) == 0


def test_roundtrip_bridge_can_read(xml_path):
    """Verify exported XML matches bridge config parser format."""
    export_config(_make_mappings(), xml_path)
    for msg in etree.parse(xml_path).findall(".//message"):
        assert int(msg.get("id")) > 0
        for sig in msg.findall("signal"):
            assert int(sig.get("start_bit")) >= 0
            assert int(sig.get("length")) > 0
            assert float(sig.get("scale")) > 0
            assert sig.get("topic").startswith("/")
