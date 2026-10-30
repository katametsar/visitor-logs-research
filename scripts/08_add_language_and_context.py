from _public_config import workspace_root, device_sheet
from pathlib import Path

import pandas as pd


# ============================================================
# KAUSTAD JA FAILID
# ============================================================

PROJECT_DIR = workspace_root()

VISITOR_EVENTS_FILE = (
    PROJECT_DIR
    / "data_clean"
    / "visitor_events.csv"
)

SESSIONS_FILE = (
    PROJECT_DIR
    / "data_clean"
    / "sessions_final.csv"
)

LANGUAGE_FILE = (
    PROJECT_DIR
    / "data_raw"
    / "Cards - languages.csv"
)

CONTEXT_FILE = (
    PROJECT_DIR
    / "data_raw"
    / "museum_calendar.csv"
)


# ============================================================
# ABIFUNKTSIOON
# ============================================================

def build_language_lookup():

    languages = pd.read_csv(
        LANGUAGE_FILE,
        dtype={
            "ID": "string",
            "Description": "string",
        },
    )

    languages["language_code"] = (
        languages["ID"]
        .astype("string")
        .str.strip()
        .str.zfill(2)
    )

    languages["language"] = (
        languages["Description"]
        .astype("string")
        .str.strip()
    )

    return dict(
        zip(
            languages["language_code"],
            languages["language"],
        )
    )


# ============================================================
# PÕHIPROGRAMM
# ============================================================

def main():

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    language_lookup = build_language_lookup()

    None  # Console output removed for public staging.

    for code, language in language_lookup.items():
        None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 1. VISITOR_EVENTS
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    events = pd.read_csv(
        VISITOR_EVENTS_FILE,
        low_memory=False,
        dtype={
            "visitor_id": "string",
            "card_id": "string",
            "session_id": "string",
        },
    )

    events["ticket_language_code"] = (
        events["visitor_id"]
        .str[:2]
    )

    events["ticket_language"] = (
        events["ticket_language_code"]
        .map(language_lookup)
    )

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    events.to_csv(
        VISITOR_EVENTS_FILE,
        index=False,
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # 2. SESSIONS
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    sessions = pd.read_csv(
        SESSIONS_FILE,
        low_memory=False,
        dtype={
            "visitor_id": "string",
            "session_id": "string",
        },
    )

    sessions["ticket_language_code"] = (
        sessions["visitor_id"]
        .str[:2]
    )

    sessions["ticket_language"] = (
        sessions["ticket_language_code"]
        .map(language_lookup)
    )

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    sessions.to_csv(
        SESSIONS_FILE,
        index=False,
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # 3. KONTEKSTIFAIL
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    if CONTEXT_FILE.exists():

        None  # Console output removed for public staging.

    else:

        context = pd.DataFrame(
            [
                {
                    "start_date": "",
                    "end_date": "",
                    "event_type": "",
                    "event_name": "",
                    "description": "",
                }
            ]
        )

        context.to_csv(
            CONTEXT_FILE,
            index=False,
            encoding="utf-8",
        )

        None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 4. LÕPP
    # --------------------------------------------------------

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.


if __name__ == "__main__":
    main()