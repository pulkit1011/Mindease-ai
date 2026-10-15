"""Safety module: rule-based detection of high-risk messages plus fixed responses.

IMPORTANT LIMITATIONS: this is a transparent keyword/pattern check. It is NOT a
clinically validated risk assessment, it will miss some crises (spelling, slang,
indirect language) and will sometimes flag harmless text. It deliberately errs on
the side of showing support information. It runs BEFORE any AI model and works
with no internet or API key."""
import json
import re
from dataclasses import dataclass
from typing import Optional

from config import RESOURCES_PATH

CATEGORIES_HIGH = ("self_harm", "immediate_danger", "abuse")

_PATTERNS = {
    "self_harm": [
        r"\b(kill|killing|hurt|hurting|harm|harming|injure|injuring)\s+(my\s*self)\b",
        r"\bcut(ting)?\s+my\s*self\b(?!\s+(some\s+)?(slack|off|short))",
        r"\bsuicid(e|al)\b",
        r"\bend(ing)?\s+(my\s+(own\s+)?life|it\s+all)\b",
        r"\btake\s+my\s+own\s+life\b",
        r"\b(want|wanna|wish|going|plan(ning)?|ready)\s+to\s+die\b(?!\s+(of|from|laughing))",
        r"\bdo\s?n'?t\s+want\s+to\s+(live|be\s+alive|exist)\b",
        r"\bbetter\s+off\s+(dead|without\s+me)\b",
        r"\bno\s+reason\s+to\s+live\b",
        r"\bself[\s-]?harm\b",
    ],
    "immediate_danger": [
        r"\bin\s+(immediate\s+|real\s+)?danger\b",
        r"\b(i\s*am|i'?m)\s+not\s+safe\b",
        r"\bsomeone\s+is\s+(trying\s+to\s+)?(hurt|kill|attack)(ing)?\s+me\b",
        r"\b(he|she|they)\s+(is|are|will|'ll)?\s*(going\s+to\s+)?(kill|beat)\s+me\b",
        r"\bwant\s+to\s+(kill|hurt)\s+(someone|somebody|him|her|them|people)\b",
    ],
    "abuse": [
        r"\b(abus(e|ed|es|ing)|molest(ed|ing)?|raped?|sexually\s+harass(ed|ing)?|assault(ed)?)\b",
        r"\b(beat(s|ing)?|hit(s|ting)?|threaten(s|ed|ing)?|stalk(s|ed|ing)?|blackmail(s|ed|ing)?)\s+me\b",
        r"\bragging\b",
    ],
    "severe_distress": [
        r"\b(can'?t|cannot)\s+(go\s+on|cope|take\s+it\s+any\s*more|do\s+this\s+any\s*more)\b",
        r"\bhopeless\b",
        r"\bworthless\b",
        r"\bpanic\s+attacks?\b",
        r"\bfalling\s+apart\b",
    ],
    "medical_request": [
        r"\bdiagnos(e|is|ed)\b",
        r"\bdo\s+i\s+have\s+(depression|anxiety|adhd|bipolar|ocd|ptsd)\b",
        r"\bam\s+i\s+(depressed|bipolar|mentally\s+ill)\b",
        r"\b(antidepressants?|sertraline|fluoxetine|prozac|xanax|alprazolam|clonazepam|escitalopram"
        r"|medications?|dosage|prescri(be|ption))\b",
    ],
}
_COMPILED = {cat: [re.compile(p) for p in pats] for cat, pats in _PATTERNS.items()}
_PRIORITY = ["self_harm", "immediate_danger", "abuse", "severe_distress", "medical_request"]


@dataclass(frozen=True)
class SafetyResult:
    level: str                  # "high", "elevated", "boundary" or "none"
    category: Optional[str]     # one of the keys above, or None

    @property
    def is_high_risk(self) -> bool:
        return self.level == "high"

    @property
    def needs_special_handling(self) -> bool:
        return self.level != "none"


def _normalise(text: str) -> str:
    text = (text or "").lower().replace("\u2019", "'").replace("`", "'")
    return re.sub(r"\s+", " ", text).strip()


def assess_message(text: str) -> SafetyResult:
    clean = _normalise(text)
    for category in _PRIORITY:
        if any(p.search(clean) for p in _COMPILED[category]):
            level = ("high" if category in CATEGORIES_HIGH
                     else "elevated" if category == "severe_distress" else "boundary")
            return SafetyResult(level, category)
    return SafetyResult("none", None)


# ---- Support resources (editable JSON, no code change needed) -----------------
def load_resources(path=None) -> dict:
    """Load resources; on any problem return an empty list rather than crash."""
    try:
        with open(path or RESOURCES_PATH, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data.get("resources"), list):
            raise ValueError
        return data
    except (OSError, ValueError):
        return {"region": "", "resources": []}


def is_verified(resource: dict) -> bool:
    return (resource.get("verification_status") == "verified"
            and bool(resource.get("source_url")) and bool(resource.get("verified_on")))


def format_resources(resources: list) -> str:
    lines = []
    for r in resources:
        if not r.get("contact"):
            continue
        tag = "" if is_verified(r) else " (not yet verified, please confirm before relying on it)"
        lines.append(f"- **{r['name']}**: {r['contact']}{tag}")
    return "\n".join(lines) if lines else (
        "- No verified support numbers are configured in this installation. "
        "Please contact your local emergency services or a trusted person.")


_DISCLOSURE = ("_I am an automated program. Nobody is monitoring this chat and I have not contacted "
               "anyone. I can also miss signs of a crisis, so please reach out to people directly._")

_HIGH = {
    "self_harm": ("I'm really sorry you're going through something this painful. I'm glad you said it out loud. "
                  "Your safety matters most right now.\n\n"
                  "If you might act on these thoughts or are in immediate danger, please contact your local "
                  "emergency services now, or go to the nearest hospital. If you can, tell a trusted person "
                  "(a friend, family member, hostel warden or teacher) and ask them to stay with you."),
    "immediate_danger": ("That sounds frightening, and I'm sorry. If you are in immediate danger, please contact "
                         "your local emergency services right now and try to move to a safer place near other "
                         "people if you can. If you can, reach out to someone you trust who can be with you."),
    "abuse": ("I'm so sorry this has happened or is happening. It is not your fault, and you deserve to be safe. "
              "If you are in danger right now, please contact your local emergency services. When you feel "
              "ready, a trusted adult, a campus counsellor or a helpline can support you with next steps."),
}


def build_response(result: SafetyResult, resources: list = None) -> str:
    """Fixed, compassionate text for flagged messages. Needs no internet or AI model."""
    resources = load_resources()["resources"] if resources is None else resources
    block = "**Support you can contact:**\n" + format_resources(resources)
    if result.level == "high":
        return f"{_HIGH[result.category]}\n\n{block}\n\n{_DISCLOSURE}"
    if result.level == "elevated":
        return ("It sounds like things feel very heavy right now, and I'm sorry. You don't have to carry this alone. "
                "Talking with someone you trust or a qualified counsellor can really help, especially if this "
                "feeling is lasting or getting in the way of daily life.\n\n"
                f"{block}\n\n{_DISCLOSURE}")
    if result.level == "boundary":
        return ("I can't diagnose conditions or advise on medicines or treatment, and I'm not a substitute for "
                "a doctor or licensed mental health professional. A qualified professional can look at your "
                "whole situation and answer this safely. I'm happy to talk about stress, routines or "
                "coping strategies in general terms if that would help.")
    return ""
