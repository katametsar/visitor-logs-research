from _public_config import workspace_root, device_sheet
from pathlib import Path

import pandas as pd


PROJECT_DIR = workspace_root()

EVENTS_FILE = PROJECT_DIR / "data_clean" / "visitor_events.csv"
SESSIONS_FILE = PROJECT_DIR / "data_clean" / "sessions_final.csv"
COORDINATES_FILE = PROJECT_DIR / "data_raw" / "coordinates.csv"

OUTPUT_FILE = PROJECT_DIR / "outputs" / "route_debug.csv"


def main():

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 1. VALIME SAMA NÄIDISSESSIOONI
    # --------------------------------------------------------

    sessions = pd.read_csv(
        SESSIONS_FILE,
        dtype={
            "session_id": "string",
            "visitor_id": "string",
        },
    )

    candidates = sessions[
        (sessions["year"] == 2026)
        &
        (sessions["unique_t_codes"] >= 20)
        &
        (sessions["coordinate_pct"] >= 80)
        &
        (sessions["duration_minutes"] >= 30)
        &
        (sessions["duration_minutes"] <= 180)
    ].copy()

    candidates["distance_from_median"] = (
        candidates["duration_minutes"]
        -
        candidates["duration_minutes"].median()
    ).abs()

    selected = (
        candidates
        .sort_values("distance_from_median")
        .iloc[0]
    )

    session_id = selected["session_id"]

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 2. LOEME SELLE SESSIOONI
    # --------------------------------------------------------

    parts = []

    for chunk in pd.read_csv(
        EVENTS_FILE,
        chunksize=200_000,
        low_memory=False,
        dtype={
            "session_id": "string",
            "reader": "string",
            "reader_mac": "string",
            "device_name": "string",
            "t_code": "string",
            "exhibit_group": "string",
            "group_name_1": "string",
            "group_name_2": "string",
            "topic": "string",
        },
    ):

        found = chunk[
            chunk["session_id"] == session_id
        ]

        if len(found):
            parts.append(found)

    path = pd.concat(
        parts,
        ignore_index=True,
    )

    path["timestamp"] = pd.to_datetime(
        path["timestamp"],
        errors="coerce",
    )

    path["x"] = pd.to_numeric(
        path["x"],
        errors="coerce",
    )

    path["y"] = pd.to_numeric(
        path["y"],
        errors="coerce",
    )

    path = (
        path
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    # ainult koordinaatidega
    path = path[
        path["x"].notna()
        &
        path["y"].notna()
    ].copy()

    # --------------------------------------------------------
    # 3. JÄRJESTIKUSED SAMAD PUNKTID KOONDAME
    # --------------------------------------------------------

    path["location_key"] = (
        path["x"].astype(str)
        +
        "_"
        +
        path["y"].astype(str)
    )

    path["previous_location_key"] = (
        path["location_key"].shift(1)
    )

    route = path[
        path["location_key"]
        !=
        path["previous_location_key"]
    ].copy()

    route = route.reset_index(drop=True)

    route["path_step"] = (
        route.index + 1
    )

    # --------------------------------------------------------
    # 4. CLICKERI KOORDINAADID ERALDI JUURDE
    # --------------------------------------------------------

    coords = pd.read_csv(
        COORDINATES_FILE,
        dtype={"code": "string"},
    )

    coords["code"] = (
        coords["code"]
        .str.strip()
    )

    coords = coords.rename(
        columns={
            "x": "clicker_x",
            "y": "clicker_y",
        }
    )

    route = route.merge(
        coords,
        left_on="t_code",
        right_on="code",
        how="left",
    )

    # --------------------------------------------------------
    # 5. KONTROLLTABEL
    # --------------------------------------------------------

    columns = [
        "path_step",
        "timestamp",
        "reader",
        "reader_mac",
        "device_name",
        "group_name_1",
        "group_name_2",
        "exhibit_group",
        "t_code",
        "topic",
        "x",
        "y",
        "clicker_x",
        "clicker_y",
    ]

    existing_columns = [
        c for c in columns
        if c in route.columns
    ]

    result = route[
        existing_columns
    ].copy()

    result.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    None  # Console output removed for public staging.


if __name__ == "__main__":
    main()