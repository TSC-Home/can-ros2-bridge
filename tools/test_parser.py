"""Tests for DBC parser module."""

import os
import pytest
from parser import load_dbc, list_messages

DBC_PATH = os.path.join(os.path.dirname(__file__), "..", "dbc", "SensoricSolutionsOMSRace.dbc")


def test_load_dbc():
    db = load_dbc(DBC_PATH)
    assert db is not None


def test_message_count():
    db = load_dbc(DBC_PATH)
    msgs = list_messages(db)
    assert len(msgs) == 5


def test_message_names():
    db = load_dbc(DBC_PATH)
    msgs = list_messages(db)
    names = {m["name"] for m in msgs}
    assert "VelAndAngPOI" in names
    assert "AccHor" in names
    assert "Status" in names
    assert "Info" in names
    assert "StaticInfo" in names


def test_message_ids():
    db = load_dbc(DBC_PATH)
    msgs = list_messages(db)
    ids = {m["id"] for m in msgs}
    assert 1536 in ids  # VelAndAngPOI
    assert 1539 in ids  # AccHor
    assert 1547 in ids  # Status


def test_vel_signals():
    db = load_dbc(DBC_PATH)
    msgs = list_messages(db)
    vel = next(m for m in msgs if m["name"] == "VelAndAngPOI")
    assert len(vel["signals"]) == 4
    sig_names = {s["name"] for s in vel["signals"]}
    assert sig_names == {"VelXPoi", "VelYPoi", "VelAPoi", "AngSPoi"}


def test_signal_scale():
    db = load_dbc(DBC_PATH)
    msgs = list_messages(db)
    vel = next(m for m in msgs if m["name"] == "VelAndAngPOI")
    vel_x = next(s for s in vel["signals"] if s["name"] == "VelXPoi")
    assert vel_x["scale"] == 0.02
    assert vel_x["length"] == 16


def test_acc_signals():
    db = load_dbc(DBC_PATH)
    msgs = list_messages(db)
    acc = next(m for m in msgs if m["name"] == "AccHor")
    assert len(acc["signals"]) == 3


def test_status_signals():
    db = load_dbc(DBC_PATH)
    msgs = list_messages(db)
    status = next(m for m in msgs if m["name"] == "Status")
    sig_names = {s["name"] for s in status["signals"]}
    assert "Standstill" in sig_names
    assert "TempSensor" in sig_names
    assert "SampleTime" in sig_names
