from __future__ import annotations

PERSONA_PROFILES: dict[str, dict[str, str]] = {
    "first_time_user": {
        "label": "First-Time User",
        "behavior": (
            "You are unfamiliar with the product, read labels carefully, and get confused by unclear UI."
        ),
    },
    "power_user": {
        "label": "Power User",
        "behavior": (
            "You optimize for speed, expect efficient flows, and flag unnecessary friction."
        ),
    },
    "elderly_user": {
        "label": "Elderly / Low Vision User",
        "behavior": (
            "You need large text, strong contrast, and large touch targets; flag accessibility blockers."
        ),
    },
    "adversarial_user": {
        "label": "Adversarial Tester",
        "behavior": (
            "You try edge cases and malformed input to expose security and validation weaknesses."
        ),
    },
}

