from _public_config import workspace_root, device_sheet
from pathlib import Path
import pandas as pd

BASE_DIR = workspace_root()
DATA_CLEAN = BASE_DIR / "data_clean"
DATA_DIR = BASE_DIR / "dashboard_data"
DATA_DIR.mkdir(exist_ok=True)

EVENTS_FILE = DATA_CLEAN / "visitor_events.csv"
OUTPUT_FILE = DATA_DIR / "exhibit_action_daily.parquet"

None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.

header = pd.read_csv(EVENTS_FILE, nrows=0)
wanted = [
    "timestamp", "session_id", "visitor_id", "t_code", "topic",
    "x", "y", "ticket_language", "action_code", "action_type"
]
usecols = [c for c in wanted if c in header.columns]

events = pd.read_csv(EVENTS_FILE, usecols=usecols, low_memory=False)
None  # Console output removed for public staging.

if "action_code" not in events.columns:
    raise ValueError("visitor_events.csv-s puudub action_code. Käivita enne 06_make_final_sessions.py.")

events["timestamp"] = pd.to_datetime(events["timestamp"], errors="coerce", utc=True)
events["date"] = (
    events["timestamp"]
    .dt.tz_convert("Europe/Tallinn")
    .dt.tz_localize(None)
    .dt.normalize()
)

events["action_code"] = events["action_code"].astype("string").str.strip()
events = events[events["action_code"].isin(["0", "1"])].copy()

events["x"] = pd.to_numeric(events.get("x"), errors="coerce")
events["y"] = pd.to_numeric(events.get("y"), errors="coerce")
events = events[
    events["date"].notna()
    & events["t_code"].notna()
    & events["x"].notna()
    & events["y"].notna()
].copy()

if "session_id" not in events.columns:
    events["session_id"] = (
        events["visitor_id"].astype(str)
        + "_"
        + events["date"].dt.strftime("%Y-%m-%d")
    )

if "ticket_language" not in events.columns:
    events["ticket_language"] = "UNKNOWN"
else:
    events["ticket_language"] = events["ticket_language"].fillna("UNKNOWN").astype(str)

# User-defined meaning in this project.
action_labels = {
    "0": "Keele muutmine",
    "1": "Teksti salvestamine",
}
events["action_label"] = events["action_code"].map(action_labels)

agg = (
    events
    .groupby(
        ["date", "t_code", "x", "y", "ticket_language", "action_code", "action_label"],
        as_index=False,
        dropna=False,
    )
    .agg(
        unique_sessions=("session_id", "nunique"),
        event_count=("session_id", "size"),
    )
)

if "topic" in events.columns:
    topic_lookup = (
        events.loc[events["topic"].notna(), ["t_code", "topic"]]
        .drop_duplicates("t_code")
    )
    agg = agg.merge(topic_lookup, on="t_code", how="left")

agg.to_parquet(OUTPUT_FILE, index=False)

None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.
