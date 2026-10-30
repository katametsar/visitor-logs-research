from _public_config import workspace_root, device_sheet
from pathlib import Path

import pandas as pd


# ============================================================
# KAUSTAD JA FAILID
# ============================================================

PROJECT_DIR = workspace_root()

INPUT_FILE = PROJECT_DIR / "data_clean" / "events_mapped.csv"

OUTPUT_DIR = PROJECT_DIR / "data_clean"

VISITOR_EVENTS_FILE = OUTPUT_DIR / "visitor_events.csv"
SESSIONS_FILE = OUTPUT_DIR / "sessions_final.csv"
LANGUAGE_EVENTS_FILE = OUTPUT_DIR / "language_events.csv"
REPEATED_TICKETS_FILE = OUTPUT_DIR / "repeated_ticket_ids.csv"


# ============================================================
# ABIFUNKTSIOON
# ============================================================

def clean_text(series):
    result = (
        series
        .astype("string")
        .str.strip()
    )

    return result.replace(
        {
            "": pd.NA,
            "<NA>": pd.NA,
            "nan": pd.NA,
            "None": pd.NA,
        }
    )


# ============================================================
# PÕHIPROGRAMM
# ============================================================

def main():

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # 1. LOEME SÜNDMUSED
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    events = pd.read_csv(
        INPUT_FILE,
        low_memory=False,
        dtype={
            "card_id": "string",
            "device_id": "string",
            "reader": "string",
            "reader_mac": "string",
            "action_code": "string",
            "action_type": "string",
            "language": "string",
            "t_code": "string",
            "device_name": "string",
            "exhibit_group": "string",
            "topic": "string",
        },
    )

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 2. AJATEMPEL
    # --------------------------------------------------------

    events["timestamp"] = pd.to_datetime(
        events["timestamp"],
        utc=True,
        errors="coerce",
    )

    events = events[
        events["timestamp"].notna()
    ].copy()

    events["timestamp"] = (
        events["timestamp"]
        .dt.tz_convert("Europe/Tallinn")
    )

    events["visit_date"] = (
        events["timestamp"]
        .dt.strftime("%Y-%m-%d")
    )

    events["year"] = (
        events["timestamp"]
        .dt.year
    )

    events["month"] = (
        events["timestamp"]
        .dt.month
    )

    events["hour"] = (
        events["timestamp"]
        .dt.hour
    )

    # --------------------------------------------------------
    # 3. CARD_ID PUHASTAMINE
    # --------------------------------------------------------

    events["card_id"] = clean_text(
        events["card_id"]
    )

    events["card_id_length"] = (
        events["card_id"]
        .str.len()
    )

    # --------------------------------------------------------
    # 4. KEELESÜNDMUSED
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    language_events = events[
        events["language"].notna()
    ].copy()

    language_events = (
        language_events
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    language_events.to_csv(
        LANGUAGE_EVENTS_FILE,
        index=False,
        encoding="utf-8",
    )

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 5. PÄRIS PILETISÜNDMUSED
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    visitor_events = events[
        events["card_id_length"] == 18
    ].copy()

    visitor_events["visitor_id"] = (
        visitor_events["card_id"]
    )

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 6. SESSION_ID
    # --------------------------------------------------------

    # Üks pilet + üks päev = üks sessioon.

    visitor_events["session_id"] = (
        visitor_events["visitor_id"]
        +
        "_"
        +
        visitor_events["visit_date"]
    )

    visitor_events = (
        visitor_events
        .sort_values(
            [
                "session_id",
                "timestamp",
            ]
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # 7. JÄRJEKORD SESSIOONIS
    # --------------------------------------------------------

    visitor_events["event_number"] = (
        visitor_events
        .groupby("session_id")
        .cumcount()
        + 1
    )

    # --------------------------------------------------------
    # 8. EELMINE SÜNDMUS
    # --------------------------------------------------------

    visitor_events["previous_timestamp"] = (
        visitor_events
        .groupby("session_id")["timestamp"]
        .shift(1)
    )

    visitor_events["gap_minutes"] = (
        (
            visitor_events["timestamp"]
            -
            visitor_events["previous_timestamp"]
        )
        .dt.total_seconds()
        / 60
    )

    visitor_events["previous_t_code"] = (
        visitor_events
        .groupby("session_id")["t_code"]
        .shift(1)
    )

    visitor_events["previous_x"] = (
        visitor_events
        .groupby("session_id")["x"]
        .shift(1)
    )

    visitor_events["previous_y"] = (
        visitor_events
        .groupby("session_id")["y"]
        .shift(1)
    )

    # --------------------------------------------------------
    # 9. ASUKOHA MUUTUS
    # --------------------------------------------------------

    visitor_events["location_changed"] = (
        visitor_events["t_code"].notna()
        &
        visitor_events["previous_t_code"].notna()
        &
        (
            visitor_events["t_code"]
            !=
            visitor_events["previous_t_code"]
        )
    )

    # --------------------------------------------------------
    # 10. KOORDINAATIDE OLEMASOLU
    # --------------------------------------------------------

    visitor_events["has_coordinates"] = (
        visitor_events["x"].notna()
        &
        visitor_events["y"].notna()
    )

    # --------------------------------------------------------
    # 11. SESSIOONIDE KOONDTABEL
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    sessions = (
        visitor_events
        .groupby(
            "session_id",
            as_index=False,
        )
        .agg(
            visitor_id=(
                "visitor_id",
                "first",
            ),
            visit_date=(
                "visit_date",
                "first",
            ),
            year=(
                "year",
                "first",
            ),
            start_time=(
                "timestamp",
                "min",
            ),
            end_time=(
                "timestamp",
                "max",
            ),
            event_count=(
                "timestamp",
                "size",
            ),
            unique_readers=(
                "reader_mac",
                "nunique",
            ),
            unique_t_codes=(
                "t_code",
                "nunique",
            ),
            unique_topics=(
                "topic",
                "nunique",
            ),
            location_changes=(
                "location_changed",
                "sum",
            ),
            coordinate_events=(
                "has_coordinates",
                "sum",
            ),
        )
    )

    # --------------------------------------------------------
    # 12. KESTUS
    # --------------------------------------------------------

    sessions["duration_minutes"] = (
        (
            sessions["end_time"]
            -
            sessions["start_time"]
        )
        .dt.total_seconds()
        / 60
    )

    sessions["coordinate_pct"] = (
        sessions["coordinate_events"]
        /
        sessions["event_count"]
        *
        100
    )

    # --------------------------------------------------------
    # 13. TEGEVUSTE ARV
    # --------------------------------------------------------

    action_counts = (
        visitor_events
        .pivot_table(
            index="session_id",
            columns="action_code",
            values="timestamp",
            aggfunc="count",
            fill_value=0,
        )
        .reset_index()
    )

    action_counts.columns = [
        str(col)
        for col in action_counts.columns
    ]

    if "0" in action_counts.columns:
        action_counts = action_counts.rename(
            columns={
                "0": "action_0_events"
            }
        )
    else:
        action_counts["action_0_events"] = 0

    if "1" in action_counts.columns:
        action_counts = action_counts.rename(
            columns={
                "1": "action_1_events"
            }
        )
    else:
        action_counts["action_1_events"] = 0

    action_counts = action_counts[
        [
            "session_id",
            "action_0_events",
            "action_1_events",
        ]
    ]

    sessions = sessions.merge(
        action_counts,
        on="session_id",
        how="left",
    )

    # --------------------------------------------------------
    # 14. ESIMENE JA VIIMANE T-KOOD
    # --------------------------------------------------------

    t_events = visitor_events[
        visitor_events["t_code"].notna()
    ].copy()

    first_t = (
        t_events
        .groupby("session_id")
        .first()
        .reset_index()
        [
            [
                "session_id",
                "t_code",
                "topic",
            ]
        ]
        .rename(
            columns={
                "t_code": "first_t_code",
                "topic": "first_topic",
            }
        )
    )

    last_t = (
        t_events
        .groupby("session_id")
        .last()
        .reset_index()
        [
            [
                "session_id",
                "t_code",
                "topic",
            ]
        ]
        .rename(
            columns={
                "t_code": "last_t_code",
                "topic": "last_topic",
            }
        )
    )

    sessions = sessions.merge(
        first_t,
        on="session_id",
        how="left",
    )

    sessions = sessions.merge(
        last_t,
        on="session_id",
        how="left",
    )

    # --------------------------------------------------------
    # 15. MITMEL PÄEVAL KORDUVAD PILETID
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    ticket_days = (
        visitor_events
        .groupby("visitor_id")
        .agg(
            number_of_days=(
                "visit_date",
                "nunique",
            ),
            first_date=(
                "visit_date",
                "min",
            ),
            last_date=(
                "visit_date",
                "max",
            ),
            total_events=(
                "timestamp",
                "size",
            ),
        )
        .reset_index()
    )

    repeated_tickets = (
        ticket_days[
            ticket_days["number_of_days"] > 1
        ]
        .sort_values(
            [
                "number_of_days",
                "total_events",
            ],
            ascending=[
                False,
                False,
            ],
        )
        .copy()
    )

    repeated_tickets.to_csv(
        REPEATED_TICKETS_FILE,
        index=False,
        encoding="utf-8",
    )

    None  # Console output removed for public staging.

    if len(repeated_tickets) > 0:

        None  # Console output removed for public staging.

        None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 16. KOKKUVÕTE
    # --------------------------------------------------------

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 17. AASTATE KAUPA
    # --------------------------------------------------------

    yearly = (
        sessions
        .groupby("year")
        .agg(
            sessions=(
                "session_id",
                "nunique",
            ),
            tickets=(
                "visitor_id",
                "nunique",
            ),
            median_duration=(
                "duration_minutes",
                "median",
            ),
            median_events=(
                "event_count",
                "median",
            ),
            median_t_codes=(
                "unique_t_codes",
                "median",
            ),
        )
    )

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 18. SALVESTAMINE
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    visitor_events.to_csv(
        VISITOR_EVENTS_FILE,
        index=False,
        encoding="utf-8",
    )

    sessions.to_csv(
        SESSIONS_FILE,
        index=False,
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # 19. LÕPP
    # --------------------------------------------------------

    None  # Console output removed for public staging.
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