from _public_config import workspace_root, device_sheet
from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# KAUSTAD
# ============================================================

BASE_DIR = workspace_root()

DATA_CLEAN = BASE_DIR / "data_clean"
DATA_RAW = BASE_DIR / "data_raw"
DASH_DATA = BASE_DIR / "dashboard_data"

DASH_DATA.mkdir(exist_ok=True)


# ============================================================
# ABIFUNKTSIOONID
# ============================================================

def heading(text):
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.


def find_first_existing(candidates):
    for path in candidates:
        if path.exists():
            return path
    return None


def normalise_date(series):
    """
    Teeb kuupäevaveerust timezone-vaba datetime'i,
    mille kellaaeg on 00:00:00.
    """
    return pd.to_datetime(
        series,
        errors="coerce",
        utc=True
    ).dt.tz_convert("Europe/Tallinn").dt.tz_localize(None).dt.normalize()


def safe_median(series):
    s = pd.to_numeric(series, errors="coerce")
    if s.notna().any():
        return s.median()
    return np.nan


def first_existing_column(df, candidates):
    """
    Tagastab esimese olemasoleva veeru nime.
    """
    lower_lookup = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for candidate in candidates:
        if candidate in df.columns:
            return candidate

        key = candidate.strip().lower()
        if key in lower_lookup:
            return lower_lookup[key]

    return None


# ============================================================
# 1. SESSIOONID
# ============================================================

heading("1. LOEN SESSIOONID")

sessions_path = DATA_CLEAN / "sessions_final.csv"

if not sessions_path.exists():
    raise FileNotFoundError(
        f"Puudub fail: {sessions_path}"
    )

sessions = pd.read_csv(
    sessions_path,
    low_memory=False
)

None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.


# ------------------------------------------------------------
# Kuupäev
# ------------------------------------------------------------

if "date" in sessions.columns:
    sessions["date"] = pd.to_datetime(
        sessions["date"],
        errors="coerce"
    ).dt.normalize()

elif "start_time" in sessions.columns:
    sessions["date"] = normalise_date(
        sessions["start_time"]
    )

else:
    raise ValueError(
        "sessions_final.csv-st ei leidnud veergu 'date' ega 'start_time'."
    )


sessions = sessions.loc[
    sessions["date"].notna()
].copy()

sessions["year"] = sessions["date"].dt.year
sessions["month"] = sessions["date"].dt.month
sessions["month_label"] = sessions["date"].dt.strftime("%Y-%m")

sessions["weekday_num"] = sessions["date"].dt.weekday

weekday_names = {
    0: "Esmaspäev",
    1: "Teisipäev",
    2: "Kolmapäev",
    3: "Neljapäev",
    4: "Reede",
    5: "Laupäev",
    6: "Pühapäev",
}

sessions["weekday"] = sessions["weekday_num"].map(
    weekday_names
)

sessions["week_start"] = (
    sessions["date"]
    - pd.to_timedelta(
        sessions["weekday_num"],
        unit="D"
    )
)


# ------------------------------------------------------------
# Algusaeg / kellaaeg
# ------------------------------------------------------------

start_col = first_existing_column(
    sessions,
    [
        "start_time",
        "session_start",
        "first_timestamp",
        "start_timestamp",
    ]
)

if start_col is not None:
    start_dt = pd.to_datetime(
        sessions[start_col],
        errors="coerce",
        utc=True
    ).dt.tz_convert("Europe/Tallinn")

    sessions["start_hour"] = start_dt.dt.hour
else:
    sessions["start_hour"] = np.nan
    None  # Console output removed for public staging.


# ------------------------------------------------------------
# Kestus
# ------------------------------------------------------------

duration_col = first_existing_column(
    sessions,
    [
        "duration_min",
        "duration_minutes",
        "session_duration_min",
        "duration",
    ]
)

if duration_col is None:
    raise ValueError(
        "Ei leidnud sessions_final.csv-st sessiooni kestuse veergu."
    )

sessions["duration_min_dashboard"] = pd.to_numeric(
    sessions[duration_col],
    errors="coerce"
)


# ------------------------------------------------------------
# Külastatud kohtade arv
# ------------------------------------------------------------

places_col = first_existing_column(
    sessions,
    [
        "unique_t_codes",
        "n_t_codes",
        "t_code_count",
        "unique_places",
        "places_count",
    ]
)

if places_col is not None:
    sessions["places_count_dashboard"] = pd.to_numeric(
        sessions[places_col],
        errors="coerce"
    )
else:
    sessions["places_count_dashboard"] = np.nan
    None  # Console output removed for public staging.


# ------------------------------------------------------------
# Sündmuste arv
# ------------------------------------------------------------

events_col = first_existing_column(
    sessions,
    [
        "event_count",
        "events",
        "n_events",
        "events_count",
    ]
)

if events_col is not None:
    sessions["event_count_dashboard"] = pd.to_numeric(
        sessions[events_col],
        errors="coerce"
    )
else:
    sessions["event_count_dashboard"] = np.nan


# ------------------------------------------------------------
# Keel
# ------------------------------------------------------------

language_col = first_existing_column(
    sessions,
    [
        "ticket_language",
        "language",
    ]
)

if language_col is None:
    raise ValueError(
        "sessions_final.csv-st puudub ticket_language."
    )

sessions["ticket_language_dashboard"] = (
    sessions[language_col]
    .fillna("UNKNOWN")
    .astype(str)
    .str.strip()
)


# ============================================================
# 2. SESSIOONIDE KERGE PARQUET
# ============================================================

heading("2. TEEN KERGE SESSIOONITABELI")

session_columns = [
    "session_id",
    "visitor_id",
    "date",
    "week_start",
    "year",
    "month",
    "month_label",
    "weekday_num",
    "weekday",
    "start_hour",
    "duration_min_dashboard",
    "places_count_dashboard",
    "event_count_dashboard",
    "ticket_language_dashboard",
]

session_columns = [
    col for col in session_columns
    if col in sessions.columns
]

sessions_dashboard = sessions[
    session_columns
].copy()

sessions_dashboard.to_parquet(
    DASH_DATA / "sessions_dashboard.parquet",
    index=False
)

None  # Console output removed for public staging.


# ============================================================
# 3. PÄEVANE KOKKUVÕTE
# ============================================================

heading("3. PÄEVANE KOKKUVÕTE")

daily = (
    sessions
    .groupby("date", as_index=False)
    .agg(
        sessions=("date", "size"),
        median_duration_min=(
            "duration_min_dashboard",
            "median"
        ),
        mean_duration_min=(
            "duration_min_dashboard",
            "mean"
        ),
        median_places=(
            "places_count_dashboard",
            "median"
        ),
        mean_places=(
            "places_count_dashboard",
            "mean"
        ),
        median_events=(
            "event_count_dashboard",
            "median"
        ),
    )
)

daily["year"] = daily["date"].dt.year
daily["month"] = daily["date"].dt.month
daily["month_label"] = daily["date"].dt.strftime(
    "%Y-%m"
)
daily["weekday_num"] = daily["date"].dt.weekday
daily["weekday"] = daily["weekday_num"].map(
    weekday_names
)

daily["week_start"] = (
    daily["date"]
    - pd.to_timedelta(
        daily["weekday_num"],
        unit="D"
    )
)


# ============================================================
# 4. KEELED PÄEVADE KAUPA
# ============================================================

heading("4. KEELED PÄEVADE KAUPA")

daily_language_long = (
    sessions
    .groupby(
        [
            "date",
            "ticket_language_dashboard"
        ],
        as_index=False
    )
    .size()
    .rename(
        columns={
            "size": "sessions",
            "ticket_language_dashboard": "language",
        }
    )
)

daily_language_wide = (
    daily_language_long
    .pivot(
        index="date",
        columns="language",
        values="sessions"
    )
    .fillna(0)
    .reset_index()
)

daily_language_wide.columns.name = None

daily = daily.merge(
    daily_language_wide,
    on="date",
    how="left"
)

daily_language_long.to_parquet(
    DASH_DATA / "daily_language.parquet",
    index=False
)

None  # Console output removed for public staging.


# ============================================================
# 5. NÄDALANE KOKKUVÕTE
# ============================================================

heading("5. NÄDALANE KOKKUVÕTE")

weekly = (
    sessions
    .groupby("week_start", as_index=False)
    .agg(
        sessions=("date", "size"),
        median_duration_min=(
            "duration_min_dashboard",
            "median"
        ),
        mean_duration_min=(
            "duration_min_dashboard",
            "mean"
        ),
        median_places=(
            "places_count_dashboard",
            "median"
        ),
        mean_places=(
            "places_count_dashboard",
            "mean"
        ),
    )
)

weekly["year"] = weekly["week_start"].dt.year
weekly["week"] = (
    weekly["week_start"]
    .dt.isocalendar()
    .week
    .astype(int)
)


weekly_language = (
    sessions
    .groupby(
        [
            "week_start",
            "ticket_language_dashboard"
        ],
        as_index=False
    )
    .size()
    .rename(
        columns={
            "size": "sessions",
            "ticket_language_dashboard": "language",
        }
    )
)

weekly_language.to_parquet(
    DASH_DATA / "weekly_language.parquet",
    index=False
)


# ============================================================
# 6. KELLAAJAD
# ============================================================

heading("6. KÜLASTUSTE ALGUSAJAD")

hourly = (
    sessions.loc[
        sessions["start_hour"].notna()
    ]
    .groupby(
        [
            "start_hour",
            "weekday_num",
            "weekday"
        ],
        as_index=False
    )
    .size()
    .rename(
        columns={"size": "sessions"}
    )
)

hourly["start_hour"] = hourly[
    "start_hour"
].astype(int)

hourly.to_parquet(
    DASH_DATA / "hourly_visits.parquet",
    index=False
)

None  # Console output removed for public staging.


# ============================================================
# 7. KESTUSE JAOTUS
# ============================================================

heading("7. KÜLASTUSE KESTUSE JAOTUS")

duration_bins = [
    0,
    15,
    30,
    45,
    60,
    90,
    120,
    180,
    np.inf,
]

duration_labels = [
    "0–15 min",
    "15–30 min",
    "30–45 min",
    "45–60 min",
    "60–90 min",
    "90–120 min",
    "2–3 h",
    "3+ h",
]

sessions["duration_group"] = pd.cut(
    sessions["duration_min_dashboard"],
    bins=duration_bins,
    labels=duration_labels,
    right=False
)

duration_distribution = (
    sessions
    .groupby(
        "duration_group",
        observed=False
    )
    .size()
    .reset_index(name="sessions")
)

duration_distribution[
    "duration_group"
] = duration_distribution[
    "duration_group"
].astype(str)

duration_distribution.to_parquet(
    DASH_DATA / "duration_distribution.parquet",
    index=False
)


# ============================================================
# 8. KÜLASTATUD EKSPONAADID / HEATMAP
# ============================================================

heading("8. EKSPONAATIDE PÄEVANE KASUTUS")

events_path = DATA_CLEAN / "visitor_events.csv"

if not events_path.exists():
    raise FileNotFoundError(
        f"Puudub fail: {events_path}"
    )

None  # Console output removed for public staging.

wanted_columns = [
    "timestamp",
    "session_id",
    "visitor_id",
    "t_code",
    "topic",
    "x",
    "y",
    "ticket_language",
]

header = pd.read_csv(
    events_path,
    nrows=0
)

available_columns = [
    col for col in wanted_columns
    if col in header.columns
]

events = pd.read_csv(
    events_path,
    usecols=available_columns,
    low_memory=False
)

None  # Console output removed for public staging.

events["timestamp"] = pd.to_datetime(
    events["timestamp"],
    errors="coerce",
    utc=True
)

events["date"] = (
    events["timestamp"]
    .dt.tz_convert("Europe/Tallinn")
    .dt.tz_localize(None)
    .dt.normalize()
)

events = events.loc[
    events["date"].notna()
].copy()

events["x"] = pd.to_numeric(
    events.get("x"),
    errors="coerce"
)

events["y"] = pd.to_numeric(
    events.get("y"),
    errors="coerce"
)


# ------------------------------------------------------------
# Sessiooni ID olemasolu
# ------------------------------------------------------------

if "session_id" not in events.columns:
    None  # Console output removed for public staging.

    events["session_id"] = (
        events["visitor_id"].astype(str)
        + "_"
        + events["date"].dt.strftime("%Y-%m-%d")
    )


# ------------------------------------------------------------
# Päev × T-kood
# ------------------------------------------------------------

map_events = events.loc[
    events["t_code"].notna()
    & events["x"].notna()
    & events["y"].notna()
].copy()

exhibit_daily = (
    map_events
    .groupby(
        [
            "date",
            "t_code",
            "x",
            "y"
        ],
        as_index=False
    )
    .agg(
        unique_sessions=(
            "session_id",
            "nunique"
        ),
        event_count=(
            "session_id",
            "size"
        ),
    )
)

if "topic" in map_events.columns:
    topic_lookup = (
        map_events.loc[
            map_events["topic"].notna(),
            ["t_code", "topic"]
        ]
        .drop_duplicates("t_code")
    )

    exhibit_daily = exhibit_daily.merge(
        topic_lookup,
        on="t_code",
        how="left"
    )

exhibit_daily.to_parquet(
    DASH_DATA / "exhibit_daily.parquet",
    index=False
)

None  # Console output removed for public staging.


# ------------------------------------------------------------
# Päev × T-kood × keel
# ------------------------------------------------------------

if "ticket_language" in map_events.columns:

    map_events["ticket_language"] = (
        map_events["ticket_language"]
        .fillna("UNKNOWN")
        .astype(str)
    )

    exhibit_language_daily = (
        map_events
        .groupby(
            [
                "date",
                "t_code",
                "x",
                "y",
                "ticket_language"
            ],
            as_index=False
        )
        .agg(
            unique_sessions=(
                "session_id",
                "nunique"
            ),
            event_count=(
                "session_id",
                "size"
            ),
        )
        .rename(
            columns={
                "ticket_language": "language"
            }
        )
    )

    exhibit_language_daily.to_parquet(
        DASH_DATA
        / "exhibit_language_daily.parquet",
        index=False
    )

    None  # Console output removed for public staging.


# ============================================================
# 9. KONTEKST: MUUSEUMI KALENDER
# ============================================================

heading("9. MUUSEUMI KALENDER")

calendar_path = DATA_RAW / "museum_calendar.csv"

if calendar_path.exists():

    calendar = pd.read_csv(
        calendar_path,
        low_memory=False
    )

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    date_col = first_existing_column(
        calendar,
        [
            "date",
            "Date",
            "kuupaev",
            "kuupäev",
        ]
    )

    if date_col is not None:
        calendar["date"] = pd.to_datetime(
            calendar[date_col],
            errors="coerce"
        ).dt.normalize()

        calendar = calendar.loc[
            calendar["date"].notna()
        ].copy()

        calendar.to_parquet(
            DASH_DATA / "museum_calendar.parquet",
            index=False
        )

        None  # Console output removed for public staging.

        # Kui kalender on juba päevatasemel,
        # proovime selle daily tabeliga ühendada.
        calendar_one_day = (
            calendar
            .sort_values("date")
            .drop_duplicates("date")
        )

        extra_cols = [
            c for c in calendar_one_day.columns
            if c != date_col
            and c != "date"
            and c not in daily.columns
        ]

        daily = daily.merge(
            calendar_one_day[
                ["date"] + extra_cols
            ],
            on="date",
            how="left"
        )

    else:
        None  # Console output removed for public staging.

else:
    None  # Console output removed for public staging.


# ============================================================
# 10. ILMAFAIL
# ============================================================

heading("10. ILMAANDMED")

weather_path = find_first_existing(
    [
        DATA_RAW / "weather.xlsx",
        DATA_RAW / "weather.xlsx",
        DATA_RAW / "weather.xlsx",
    ]
)

if weather_path is not None:

    None  # Console output removed for public staging.

    try:
        weather = pd.read_excel(
            weather_path
        )

        None  # Console output removed for public staging.
        None  # Console output removed for public staging.

        weather_date_col = first_existing_column(
            weather,
            [
                "date",
                "Date",
                "Kuupäev",
                "kuupäev",
                "kuupaev",
            ]
        )

        if weather_date_col is not None:

            weather["date"] = pd.to_datetime(
                weather[weather_date_col],
                errors="coerce"
            ).dt.normalize()

            weather = weather.loc[
                weather["date"].notna()
            ].copy()

            weather.to_parquet(
                DASH_DATA / "weather_daily.parquet",
                index=False
            )

            None  # Console output removed for public staging.

        else:
            None  # Console output removed for public staging.

    except Exception as exc:
        None  # Console output removed for public staging.
        None  # Console output removed for public staging.

else:
    None  # Console output removed for public staging.


# ============================================================
# 11. ERMi SÜNDMUSED
# ============================================================

heading("11. ERMi SÜNDMUSED")

events_context_path = find_first_existing(
    [
        DATA_RAW / "museum_events.xlsx",
        DATA_RAW / "museum_events.xlsx",
        DATA_RAW / "events.xlsx",
    ]
)

if events_context_path is not None:

    None  # Console output removed for public staging.

    try:
        museum_events = pd.read_excel(
            events_context_path
        )

        None  # Console output removed for public staging.
        None  # Console output removed for public staging.

        museum_events.to_parquet(
            DASH_DATA / "museum_events.parquet",
            index=False
        )

        None  # Console output removed for public staging.

    except Exception as exc:
        None  # Console output removed for public staging.
        None  # Console output removed for public staging.

else:
    None  # Console output removed for public staging.


# ============================================================
# 12. SALVESTAN PÕHITABELID
# ============================================================

heading("12. SALVESTAN DASHBOARDI PÕHITABELID")

daily.to_parquet(
    DASH_DATA / "daily_summary.parquet",
    index=False
)

weekly.to_parquet(
    DASH_DATA / "weekly_summary.parquet",
    index=False
)


# ============================================================
# 13. FAILIDE SUURUSED
# ============================================================

heading("13. VALMIS")

None  # Console output removed for public staging.

for path in sorted(
    DASH_DATA.glob("*.parquet")
):
    size_mb = path.stat().st_size / 1024 / 1024

    None  # Console output removed for public staging.

None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.

None  # Console output removed for public staging.