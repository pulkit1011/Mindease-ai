import json

import pytest

from services import safety_service as s


@pytest.mark.parametrize("text", [
    "I want to kill myself", "i dont want to live anymore", "I've been thinking about suicide",
    "I want to end my life", "thinking of ending it all", "everyone would be better off dead",
    "I keep wanting to hurt myself", "I want to die"])
def test_self_harm_detected_as_high_risk(text):
    r = s.assess_message(text)
    assert r.is_high_risk and r.category == "self_harm"


@pytest.mark.parametrize("text,cat", [("someone is trying to hurt me", "immediate_danger"),
                                      ("I am not safe at home", "immediate_danger"),
                                      ("my senior keeps threatening me in the hostel", "abuse"),
                                      ("I was sexually harassed", "abuse")])
def test_danger_and_abuse_detected(text, cat):
    r = s.assess_message(text)
    assert r.is_high_risk and r.category == cat


def test_severe_distress_and_medical_requests_are_not_high_risk_but_handled():
    assert s.assess_message("I feel completely hopeless").level == "elevated"
    for t in ("Do I have depression?", "Which antidepressant should I take?", "can you diagnose me"):
        r = s.assess_message(t)
        assert r.level == "boundary" and not r.is_high_risk


@pytest.mark.parametrize("text", [
    "I'm stressed about my exam tomorrow", "This assignment is killing me", "I'm dying to see my results",
    "I could die of embarrassment", "I need to cut myself some slack", "I'm so tired today",
    "Can you suggest a study timetable?", "I want to die laughing at that meme", "", None])
def test_ordinary_messages_do_not_trigger(text):
    assert s.assess_message(text).level == "none"


def test_self_harm_has_priority_over_other_categories():
    assert s.assess_message("I feel hopeless and want to kill myself").category == "self_harm"


def test_high_risk_response_is_compassionate_honest_and_not_routine():
    text = s.build_response(s.assess_message("I want to end my life"), resources=[])
    low = text.lower()
    assert "emergency services" in low and "trusted person" in low
    assert "have not contacted anyone" in low and "nobody is monitoring" in low
    assert "study timetable" not in low and "breathing exercise" not in low


def test_boundary_response_refuses_diagnosis():
    text = s.build_response(s.assess_message("which medication should I take"), resources=[])
    assert "can't diagnose" in text.lower()


def test_resources_file_is_valid_and_honest():
    data = s.load_resources()
    assert data["resources"]
    for r in data["resources"]:
        assert {"id", "name", "contact", "source_url", "verified_on", "verification_status"} <= set(r)
        if r["verification_status"] == "verified":
            assert r["source_url"] and r["verified_on"]
    assert not any(s.is_verified(r) for r in data["resources"] if not r["verified_on"])


def test_unverified_resources_are_labelled_in_responses():
    text = s.build_response(s.assess_message("I want to die"))
    assert "not yet verified" in text


def test_resources_load_failure_is_graceful(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    assert s.load_resources(bad)["resources"] == []
    assert s.load_resources(tmp_path / "missing.json")["resources"] == []
    assert "No verified support numbers" in s.format_resources([])


def test_custom_resources_can_be_updated_without_code(tmp_path):
    p = tmp_path / "r.json"
    p.write_text(json.dumps({"resources": [{"name": "Local line", "contact": "000", "verification_status": "verified",
                                            "source_url": "https://example.org", "verified_on": "2026-01-01"}]}))
    text = s.format_resources(s.load_resources(p)["resources"])
    assert "Local line" in text and "not yet verified" not in text
