from _public_config import workspace_root, device_sheet
from pathlib import Path

import pandas as pd


# ============================================================
# KAUSTAD JA FAILID
# ============================================================

PROJECT_DIR = workspace_root()

INPUT_FILE = PROJECT_DIR / "data_clean" / "events_mapped.csv"

OUTPUT_DIR = PROJECT_DIR / "data_clean"

EVENTS_OUTPUT = OUTPUT_DIR / "events_sessions.csv"
SESSIONS_OUTPUT = OUTPUT_DIR / "sessions.csv"
REPEATED_DEVICES_OUTPUT = OUTPUT_DIR / "repeated_device_ids.csv"


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
            "visitor_token": "string",
            "device_id": "string",
            "card_id": "string",
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

    None  # Console output removed for public staging.

    events["timestamp"] = pd.to_datetime(
        events["timestamp"],
        utc=True,
        errors="coerce",
    )

    bad_timestamps = events["timestamp"].isna().sum()

    None  # Console output removed for public staging.

    events = events[
        events["timestamp"].notna()
    ].copy()

    # Muudame UTC-st Eesti ajaks.
    events["timestamp"] = (
        events["timestamp"]
        .dt.tz_convert("Europe/Tallinn")
    )

    # --------------------------------------------------------
    # 3. VISITOR_ID
    # --------------------------------------------------------

    # Kasutame külastaja tehnilise tunnusena device_id-d.
    events["visitor_id"] = events["device_id"]

    missing_visitors = (
        events["visitor_id"]
        .isna()
        .sum()
    )

    None  # Console output removed for public staging.

    # Sessiooni ei saa ilma visitor_id-ta usaldusväärselt teha.
    events = events[
        events["visitor_id"].notna()
    ].copy()

    # --------------------------------------------------------
    # 4. KÜLASTUSKUUPÄEV
    # --------------------------------------------------------

    events["visit_date"] = (
        events["timestamp"]
        .dt.strftime("%Y-%m-%d")
    )

    # --------------------------------------------------------
    # 5. SESSION_ID
    # --------------------------------------------------------

    # Üks device_id + üks kalendripäev = üks sessioon.
    #
    # Näiteks:
    #
    # SYNTHETIC_IDENTIFIER_A_2026-01-02

    events["session_id"] = (
        events["visitor_id"]
        .astype(str)
        +
        "_"
        +
        events["visit_date"]
    )

    # --------------------------------------------------------
    # 6. SORTEERIME
    # --------------------------------------------------------

    events = (
        events
        .sort_values(
            [
                "session_id",
                "timestamp",
            ]
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # 7. SÜNDMUSE JÄRJEKORD SESSIOONIS
    # --------------------------------------------------------

    events["event_number"] = (
        events
        .groupby("session_id")
        .cumcount()
        + 1
    )

    # --------------------------------------------------------
    # 8. EELMINE SÜNDMUS
    # --------------------------------------------------------

    events["previous_timestamp"] = (
        events
        .groupby("session_id")["timestamp"]
        .shift(1)
    )

    events["gap_minutes"] = (
        (
            events["timestamp"]
            -
            events["previous_timestamp"]
        )
        .dt.total_seconds()
        / 60
    )

    # --------------------------------------------------------
    # 9. EELMINE ASUKOHT
    # --------------------------------------------------------

    events["previous_t_code"] = (
        events
        .groupby("session_id")["t_code"]
        .shift(1)
    )

    events["previous_x"] = (
        events
        .groupby("session_id")["x"]
        .shift(1)
    )

    events["previous_y"] = (
        events
        .groupby("session_id")["y"]
        .shift(1)
    )

    # --------------------------------------------------------
    # 10. KAS ASUKOHT MUUTUS?
    # --------------------------------------------------------

    events["location_changed"] = (
        events["t_code"].notna()
        &
        events["previous_t_code"].notna()
        &
        (
            events["t_code"]
            !=
            events["previous_t_code"]
        )
    )

    # --------------------------------------------------------
    # 11. SESSIOONIDE ARV
    # --------------------------------------------------------

    session_count = (
        events["session_id"]
        .nunique()
    )

    visitor_count = (
        events["visitor_id"]
        .nunique()
    )

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 12. SESSIOONIDE KOONDTABEL
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    # Põhiandmed
    sessions = (
        events
        .groupby(
            "session_id",
            as_index=False,
        )
        .agg(
            visitor_id=(
                "visitor_id",
                "first",
            ),
            card_id=(
                "card_id",
                "first",
            ),
            visit_date=(
                "visit_date",
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
        )
    )

    # --------------------------------------------------------
    # 13. KESTUS
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

    # --------------------------------------------------------
    # 14. /0 JA /1 TEGEVUSED
    # --------------------------------------------------------

    action_counts = (
        events
        .pivot_table(
            index="session_id",
            columns="action_code",
            values="timestamp",
            aggfunc="count",
            fill_value=0,
        )
        .reset_index()
    )

    # Pandas võib action_code veerud teha stringideks.
    action_counts.columns = [
        str(col)
        for col in action_counts.columns
    ]

    if "0" in action_counts.columns:
        action_counts = action_counts.rename(
            columns={
                "0": "language_change_events"
            }
        )
    else:
        action_counts["language_change_events"] = 0

    if "1" in action_counts.columns:
        action_counts = action_counts.rename(
            columns={
                "1": "take_museum_events"
            }
        )
    else:
        action_counts["take_museum_events"] = 0

    keep_action_columns = [
        "session_id",
        "language_change_events",
        "take_museum_events",
    ]

    action_counts = action_counts[
        keep_action_columns
    ]

    sessions = sessions.merge(
        action_counts,
        on="session_id",
        how="left",
    )

    # --------------------------------------------------------
    # 15. KOORDINAATIDEGA SÜNDMUSED
    # --------------------------------------------------------

    events["has_coordinates"] = (
        events["x"].notna()
        &
        events["y"].notna()
    )

    coordinate_summary = (
        events
        .groupby(
            "session_id",
            as_index=False,
        )
        .agg(
            coordinate_events=(
                "has_coordinates",
                "sum",
            )
        )
    )

    sessions = sessions.merge(
        coordinate_summary,
        on="session_id",
        how="left",
    )

    sessions["coordinate_pct"] = (
        sessions["coordinate_events"]
        /
        sessions["event_count"]
        *
        100
    )

    # --------------------------------------------------------
    # 16. KEELED
    # --------------------------------------------------------

    # Milliseid keelekoode selle sessiooni jooksul logiti?

    session_languages = (
        events[
            events["language"].notna()
        ]
        .groupby("session_id")["language"]
        .agg(
            lambda x: ",".join(
                sorted(
                    set(x.astype(str))
                )
            )
        )
        .reset_index(
            name="languages"
        )
    )

    sessions = sessions.merge(
        session_languages,
        on="session_id",
        how="left",
    )

    # --------------------------------------------------------
    # 17. ESIMENE JA VIIMANE T-KOOD
    # --------------------------------------------------------

    t_events = events[
        events["t_code"].notna()
    ].copy()

    if len(t_events) > 0:

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
    # 18. MITMEL PÄEVAL KASUTATUD DEVICE_ID-D
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    visitor_days = (
        events
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
            card_id=(
                "card_id",
                "first",
            ),
        )
        .reset_index()
    )

    repeated = (
        visitor_days[
            visitor_days["number_of_days"] > 1
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

    repeated.to_csv(
        REPEATED_DEVICES_OUTPUT,
        index=False,
        encoding="utf-8",
    )

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 19. SESSIOONIDE KESTUSE KONTROLL
    # --------------------------------------------------------

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    duration = sessions[
        "duration_minutes"
    ]

    quantiles = [
        0.25,
        0.50,
        0.75,
        0.90,
        0.95,
        0.99,
    ]

    for q, value in (
        duration
        .quantile(quantiles)
        .items()
    ):

        None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 20. SÜNDMUSTE ARV SESSIOONIS
    # --------------------------------------------------------

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    event_quantiles = (
        sessions["event_count"]
        .quantile(
            [
                0.25,
                0.50,
                0.75,
                0.90,
                0.95,
                0.99,
            ]
        )
    )

    for q, value in event_quantiles.items():

        None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 21. T-KOODIDE ARV SESSIOONIS
    # --------------------------------------------------------

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    t_quantiles = (
        sessions["unique_t_codes"]
        .quantile(
            [
                0.25,
                0.50,
                0.75,
                0.90,
                0.95,
                0.99,
            ]
        )
    )

    for q, value in t_quantiles.items():

        None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 22. AASTATE KAUPA
    # --------------------------------------------------------

    sessions["year"] = (
        pd.to_datetime(
            sessions["visit_date"]
        )
        .dt.year
    )

    sessions_per_year = (
        sessions
        .groupby("year")
        .agg(
            sessions=(
                "session_id",
                "nunique",
            ),
            visitors=(
                "visitor_id",
                "nunique",
            ),
            events=(
                "event_count",
                "sum",
            ),
            median_duration_min=(
                "duration_minutes",
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
    # 23. SALVESTAMINE
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    events.to_csv(
        EVENTS_OUTPUT,
        index=False,
        encoding="utf-8",
    )

    sessions.to_csv(
        SESSIONS_OUTPUT,
        index=False,
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # 24. LÕPP
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