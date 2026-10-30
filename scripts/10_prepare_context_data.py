from _public_config import workspace_root, device_sheet
from pathlib import Path
import pandas as pd


BASE_DIR = workspace_root()

DATA_RAW = BASE_DIR / "data_raw"
DASH_DATA = BASE_DIR / "dashboard_data"


# ============================================================
# 1. MUUSEUMI KALENDER
# ============================================================

None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.

calendar_path = DATA_RAW / "museum_calendar.csv"

calendar = pd.read_csv(
    calendar_path,
    low_memory=False
)

calendar["start_date"] = pd.to_datetime(
    calendar["start_date"],
    errors="coerce"
)

calendar["end_date"] = pd.to_datetime(
    calendar["end_date"],
    errors="coerce"
)

# Kui end_date puudub, võtame sama päeva
calendar["end_date"] = (
    calendar["end_date"]
    .fillna(calendar["start_date"])
)

calendar = calendar[
    calendar["start_date"].notna()
].copy()

daily_rows = []

for _, row in calendar.iterrows():

    dates = pd.date_range(
        row["start_date"],
        row["end_date"],
        freq="D"
    )

    for date in dates:

        daily_rows.append(
            {
                "date": date.normalize(),
                "event_type": row.get(
                    "event_type",
                    None
                ),
                "event_name": row.get(
                    "event_name",
                    None
                ),
                "description": row.get(
                    "description",
                    None
                ),
            }
        )

calendar_daily = pd.DataFrame(
    daily_rows
)

calendar_daily.to_parquet(
    DASH_DATA / "museum_calendar_daily.parquet",
    index=False
)

None  # Console output removed for public staging.

if len(calendar_daily):

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.


# ============================================================
# 2. ILM
# ============================================================

None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.

weather_path = (
    DATA_RAW
    / "weather.xlsx"
)

weather = pd.read_excel(
    weather_path
)

None  # Console output removed for public staging.

weather["date"] = pd.to_datetime(
    dict(
        year=weather["Year"],
        month=weather["Month"],
        day=weather["Day"],
    ),
    errors="coerce"
)

weather["temp_c"] = pd.to_numeric(
    weather["Temp °C"],
    errors="coerce"
)

weather["rain_mm"] = pd.to_numeric(
    weather["AVG rain mm"],
    errors="coerce"
)

weather["humidity_pct"] = pd.to_numeric(
    weather["Humidity %"],
    errors="coerce"
)

weather = weather[
    weather["date"].notna()
].copy()

# Fail paistab sisaldavat ka kellaaegu.
# Dashboardi jaoks teeme päevase kokkuvõtte.

weather_daily = (
    weather
    .groupby(
        "date",
        as_index=False
    )
    .agg(
        temp_mean_c=(
            "temp_c",
            "mean"
        ),
        temp_min_c=(
            "temp_c",
            "min"
        ),
        temp_max_c=(
            "temp_c",
            "max"
        ),
        rain_mean_mm=(
            "rain_mm",
            "mean"
        ),
        rain_max_mm=(
            "rain_mm",
            "max"
        ),
        humidity_mean_pct=(
            "humidity_pct",
            "mean"
        ),
    )
)

weather_daily.to_parquet(
    DASH_DATA / "weather_daily.parquet",
    index=False
)

None  # Console output removed for public staging.

None  # Console output removed for public staging.
None  # Console output removed for public staging.


# ============================================================
# 3. ERMi SÜNDMUSED
# ============================================================

None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.

events_path = (
    DATA_RAW
    / "museum_events.xlsx"
)

museum_events = pd.read_excel(
    events_path
)

museum_events["date"] = pd.to_datetime(
    museum_events["Date"],
    errors="coerce"
)

museum_events = museum_events[
    museum_events["date"].notna()
].copy()

museum_events = museum_events.rename(
    columns={
        "Type": "event_type",
        "Time": "event_time",
    }
)

museum_events[
    [
        "date",
        "event_type",
        "event_time",
    ]
].to_parquet(
    DASH_DATA
    / "museum_events_daily.parquet",
    index=False
)

None  # Console output removed for public staging.

None  # Console output removed for public staging.

None  # Console output removed for public staging.


# ============================================================
# 4. KÕIK PÄEVAKONTEKSTID ÜHTE TABELISSE
# ============================================================

None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.

daily_path = (
    DASH_DATA
    / "daily_summary.parquet"
)

daily = pd.read_parquet(
    daily_path
)

daily["date"] = pd.to_datetime(
    daily["date"]
)

# ------------------------------------------------------------
# ilm
# ------------------------------------------------------------

daily = daily.merge(
    weather_daily,
    on="date",
    how="left"
)

# ------------------------------------------------------------
# ERMi sündmuste arv päevas
# ------------------------------------------------------------

event_counts = (
    museum_events
    .groupby(
        "date",
        as_index=False
    )
    .size()
    .rename(
        columns={
            "size":
                "museum_event_count"
        }
    )
)

daily = daily.merge(
    event_counts,
    on="date",
    how="left"
)

daily[
    "museum_event_count"
] = (
    daily[
        "museum_event_count"
    ]
    .fillna(0)
    .astype(int)
)

# ------------------------------------------------------------
# kalendrisündmused
# ------------------------------------------------------------

if len(calendar_daily):

    calendar_flags = (
        calendar_daily
        .groupby("date")
        .agg(
            calendar_event_count=(
                "event_type",
                "size"
            ),
            calendar_event_types=(
                "event_type",
                lambda x:
                    ", ".join(
                        sorted(
                            set(
                                x.dropna()
                                .astype(str)
                            )
                        )
                    )
            ),
            calendar_event_names=(
                "event_name",
                lambda x:
                    " | ".join(
                        sorted(
                            set(
                                x.dropna()
                                .astype(str)
                            )
                        )
                    )
            ),
        )
        .reset_index()
    )

    daily = daily.merge(
        calendar_flags,
        on="date",
        how="left"
    )

else:

    daily[
        "calendar_event_count"
    ] = 0

    daily[
        "calendar_event_types"
    ] = ""

    daily[
        "calendar_event_names"
    ] = ""


daily[
    "calendar_event_count"
] = (
    daily[
        "calendar_event_count"
    ]
    .fillna(0)
    .astype(int)
)

daily[
    "calendar_event_types"
] = (
    daily[
        "calendar_event_types"
    ]
    .fillna("")
)

daily[
    "calendar_event_names"
] = (
    daily[
        "calendar_event_names"
    ]
    .fillna("")
)


# ============================================================
# 5. SALVESTAMINE
# ============================================================

output_path = (
    DASH_DATA
    / "daily_context.parquet"
)

daily.to_parquet(
    output_path,
    index=False
)

None  # Console output removed for public staging.

None  # Console output removed for public staging.

None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.

for filename in [
    "museum_calendar_daily.parquet",
    "weather_daily.parquet",
    "museum_events_daily.parquet",
    "daily_context.parquet",
]:

    path = DASH_DATA / filename

    if path.exists():

        None  # Console output removed for public staging.