from _public_config import workspace_root, device_sheet
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = workspace_root()
DATA_DIR = BASE_DIR / "dashboard_data"

SESSIONS_FILE = DATA_DIR / "sessions_dashboard.parquet"
TICKETS_FILE = DATA_DIR / "ticket_sales_daily.parquet"
WEATHER_FILE = DATA_DIR / "weather_daily.parquet"
EVENTS_FILE = DATA_DIR / "museum_events_daily.parquet"
HOLIDAYS_FILE = DATA_DIR / "school_holidays_daily.parquet"

OUTPUT_FILE = DATA_DIR / "data_coverage_daily.parquet"
MONTHLY_OUTPUT_FILE = DATA_DIR / "data_coverage_monthly.parquet"


# ============================================================
# ABIFUNKTSIOONID
# ============================================================

def get_date_column(df):
    """Leia tabelist kuupäevaveerg."""
    for col in ["date", "visit_date", "Day", "Date"]:
        if col in df.columns:
            return col
    return None


def dates_present(path):
    """Tagasta kuupäevad, mille kohta tabelis on vähemalt üks kirje."""
    if not path.exists():
        return pd.DatetimeIndex([])

    df = pd.read_parquet(path)
    date_col = get_date_column(df)

    if date_col is None:
        None  # Console output removed for public staging.
        return pd.DatetimeIndex([])

    dates = (
        pd.to_datetime(df[date_col], errors="coerce")
        .dropna()
        .dt.normalize()
    )

    return pd.DatetimeIndex(dates.unique())


None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.


# ============================================================
# 1. ANDMEALLIKATE KUUPÄEVAD
# ============================================================

None  # Console output removed for public staging.

sessions = pd.read_parquet(SESSIONS_FILE)

session_date_col = get_date_column(sessions)

if session_date_col is None:
    raise ValueError(
        "sessions_dashboard.parquet failist ei leidnud kuupäevaveergu."
    )

sessions[session_date_col] = (
    pd.to_datetime(
        sessions[session_date_col],
        errors="coerce"
    )
    .dt.normalize()
)

log_dates = pd.DatetimeIndex(
    sessions[session_date_col]
    .dropna()
    .unique()
)

ticket_dates = dates_present(TICKETS_FILE)
weather_dates = dates_present(WEATHER_FILE)
event_dates = dates_present(EVENTS_FILE)


# ============================================================
# 2. TÄIELIK KALENDER
# ============================================================

all_known_dates = []

for dates in [
    log_dates,
    ticket_dates,
    weather_dates,
    event_dates
]:
    if len(dates):
        all_known_dates.extend(dates.tolist())

if not all_known_dates:
    raise ValueError(
        "Ühestki andmeallikast ei leitud kuupäevi."
    )

start_date = pd.Timestamp(min(all_known_dates)).normalize()
end_date = pd.Timestamp(max(all_known_dates)).normalize()

calendar = pd.DataFrame({
    "date": pd.date_range(
        start_date,
        end_date,
        freq="D"
    )
})

calendar["year"] = calendar["date"].dt.year
calendar["month"] = calendar["date"].dt.month
calendar["day"] = calendar["date"].dt.day
calendar["weekday_num"] = calendar["date"].dt.weekday

weekday_names = {
    0: "Esmaspäev",
    1: "Teisipäev",
    2: "Kolmapäev",
    3: "Neljapäev",
    4: "Reede",
    5: "Laupäev",
    6: "Pühapäev",
}

calendar["weekday"] = (
    calendar["weekday_num"]
    .map(weekday_names)
)


# ============================================================
# 3. MUUSEUMI TEADAOLEV AVATUS
# ============================================================

None  # Console output removed for public staging.

# Oluline:
# see väli kirjeldab muuseumi tavakülastajale teadaolevat avatust.
#
# See EI ütle midagi selle kohta, kas digisüsteemis võis
# samal päeval tegevust olla.
#
# Praegu teame kindlalt:
# - esmaspäeviti on muuseum tavakülastajale suletud
# - 1. jaanuaril on muuseum suletud
#
# Teiste riigipühade kohta me oletusi ei tee.

calendar["known_closed"] = False
calendar["closure_reason"] = pd.NA

monday_mask = calendar["weekday_num"] == 0

calendar.loc[
    monday_mask,
    "known_closed"
] = True

calendar.loc[
    monday_mask,
    "closure_reason"
] = "Esmaspäev"


january_first_mask = (
    (calendar["month"] == 1)
    & (calendar["day"] == 1)
)

calendar.loc[
    january_first_mask,
    "known_closed"
] = True

calendar.loc[
    january_first_mask,
    "closure_reason"
] = "1. jaanuar"


calendar["museum_status"] = np.where(
    calendar["known_closed"],
    "Teadaolevalt suletud",
    "Avatud või teadmata"
)


# ============================================================
# 4. ANDMEALLIKATE KATVUS
# ============================================================

None  # Console output removed for public staging.

calendar["log_data_available"] = (
    calendar["date"].isin(log_dates)
)

calendar["ticket_data_available"] = (
    calendar["date"].isin(ticket_dates)
)

calendar["weather_data_available"] = (
    calendar["date"].isin(weather_dates)
)

calendar["museum_event_data_available"] = (
    calendar["date"].isin(event_dates)
)


# ============================================================
# 5. DIGISESSIOONIDE PÄEVANE MAHT
# ============================================================

daily_logs = (
    sessions
    .dropna(subset=[session_date_col])
    .groupby(
        session_date_col,
        observed=True
    )
    .size()
    .reset_index(name="digital_sessions")
    .rename(
        columns={session_date_col: "date"}
    )
)

calendar = calendar.merge(
    daily_logs,
    on="date",
    how="left"
)

# Äärmiselt oluline:
#
# kui logiandmeid selle kuupäeva kohta pole,
# EI tähenda see null sessiooni.
#
# Seetõttu jääb väärtuseks NaN.

calendar.loc[
    ~calendar["log_data_available"],
    "digital_sessions"
] = np.nan


# ============================================================
# 6. DIGITEGEVUS TEADAOLEVALT SULETUD PÄEVADEL
# ============================================================

# See EI tähenda automaatselt külastajaid.
#
# Võimalikud põhjused:
# - töötajate testimine
# - ekskursioon
# - eriüritus
# - hooldus
# - muu sisemine kasutus
#
# Me ei klassifitseeri neid praegu automaatselt.

calendar["digital_activity_on_closed_day"] = (
    calendar["known_closed"]
    & calendar["log_data_available"]
    & (calendar["digital_sessions"] > 0)
)


# ============================================================
# 7. PILETIMÜÜK
# ============================================================

if TICKETS_FILE.exists():

    tickets = pd.read_parquet(TICKETS_FILE)

    ticket_date_col = get_date_column(tickets)

    if ticket_date_col:

        tickets[ticket_date_col] = (
            pd.to_datetime(
                tickets[ticket_date_col],
                errors="coerce"
            )
            .dt.normalize()
        )

        keep = [ticket_date_col]

        for col in [
            "tickets_sold",
            "ticket_transactions",
            "paid_sum"
        ]:
            if col in tickets.columns:
                keep.append(col)

        ticket_small = tickets[keep].copy()

        if ticket_date_col != "date":
            ticket_small = ticket_small.rename(
                columns={ticket_date_col: "date"}
            )

        calendar = calendar.merge(
            ticket_small,
            on="date",
            how="left"
        )


# ============================================================
# 8. KOOLIVAHEAJAD
# ============================================================

if HOLIDAYS_FILE.exists():

    holidays = pd.read_parquet(HOLIDAYS_FILE)

    holiday_date_col = get_date_column(
        holidays
    )

    if holiday_date_col:

        holidays[holiday_date_col] = (
            pd.to_datetime(
                holidays[holiday_date_col],
                errors="coerce"
            )
            .dt.normalize()
        )

        keep = [holiday_date_col] + [
            c
            for c in holidays.columns
            if c.startswith("school_holiday_")
        ]

        holiday_small = (
            holidays[keep]
            .copy()
        )

        if holiday_date_col != "date":
            holiday_small = (
                holiday_small.rename(
                    columns={
                        holiday_date_col: "date"
                    }
                )
            )

        calendar = calendar.merge(
            holiday_small,
            on="date",
            how="left"
        )

        bool_cols = [
            c
            for c in calendar.columns
            if c in [
                "school_holiday_estonia",
                "school_holiday_latvia",
                "school_holiday_finland",
            ]
        ]

        for col in bool_cols:
            calendar[col] = (
                calendar[col]
                .astype("boolean")
                .fillna(False)
                .astype(bool)
            )


# ============================================================
# 9. ANDMEKATVUSE STAATUS
# ============================================================

# See kirjeldab ainult DIGILOGI olemasolu.
# Muuseumi avatus on sellest täiesti eraldi tunnus.

calendar["digital_data_status"] = np.where(
    calendar["log_data_available"],
    "Logiandmed olemas",
    "Logiandmed puuduvad"
)


# ============================================================
# 10. NÄDAL
# ============================================================

# Nädal algab esmaspäeval.
# Kasutame nädala tähiseks selle esmaspäeva kuupäeva.

calendar["week_start"] = (
    calendar["date"]
    - pd.to_timedelta(
        calendar["weekday_num"],
        unit="D"
    )
)

calendar["week_end"] = (
    calendar["week_start"]
    + pd.Timedelta(days=6)
)


# ============================================================
# 11. KUU
# ============================================================

calendar["month_date"] = (
    calendar["date"]
    .dt.to_period("M")
    .dt.to_timestamp()
)


# ============================================================
# 12. SALVESTA PÄEVATABEL
# ============================================================

calendar.to_parquet(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 13. KUUPÕHINE DIAGNOSTIKA
# ============================================================

None  # Console output removed for public staging.

monthly = (
    calendar
    .groupby(
        "month_date",
        observed=True
    )
    .agg(
        calendar_days=(
            "date",
            "size"
        ),
        known_closed_days=(
            "known_closed",
            "sum"
        ),
        log_days=(
            "log_data_available",
            "sum"
        ),
        ticket_days=(
            "ticket_data_available",
            "sum"
        ),
        weather_days=(
            "weather_data_available",
            "sum"
        ),
        museum_event_days=(
            "museum_event_data_available",
            "sum"
        ),
        digital_sessions=(
            "digital_sessions",
            lambda x: (
                x.sum(min_count=1)
            )
        ),
        digital_activity_closed_days=(
            "digital_activity_on_closed_day",
            "sum"
        ),
    )
    .reset_index()
)


# ============================================================
# 14. KATVUSE PROTSENDID
# ============================================================

# DIGILOGI katvus arvutatakse KÕIGI kalendripäevade suhtes.
#
# Me ei eemalda esmaspäevi, sest digisüsteem võib
# töötada ka ajal, mil muuseum on tavakülastajale suletud.

monthly["log_coverage_pct"] = (
    100
    * monthly["log_days"]
    / monthly["calendar_days"]
)


# Piletimüügi puhul on mõistlik vaadata teadaolevalt
# mitte-suletud päevi.
#
# NB! "Avatud või teadmata" ei tähenda, et oleme kõigi
# ajalooliste lahtiolekuaegade osas täiesti kindlad.

monthly["potential_visitor_days"] = (
    monthly["calendar_days"]
    - monthly["known_closed_days"]
)

monthly["ticket_coverage_pct"] = np.where(
    monthly["potential_visitor_days"] > 0,
    (
        100
        * monthly["ticket_days"]
        / monthly["potential_visitor_days"]
    ),
    np.nan
)

# Kaitse diagnostikas üle 100% väärtuse vastu.
# Piletimüüki võib olla ka päeval, mille oleme üldreegli järgi
# suletuks märkinud, seega jätame algse info alles,
# kuid eraldi piiratud protsendi võib dashboard hiljem kasutada.

monthly["ticket_coverage_pct_capped"] = (
    monthly["ticket_coverage_pct"]
    .clip(upper=100)
)


monthly.to_parquet(
    MONTHLY_OUTPUT_FILE,
    index=False
)


# ============================================================
# 15. TERMINALI KONTROLL
# ============================================================

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

None  # Console output removed for public staging.


# ============================================================
# 16. SULETUD PÄEVADE DIGITEGEVUSE NÄITED
# ============================================================

closed_activity = (
    calendar.loc[
        calendar[
            "digital_activity_on_closed_day"
        ],
        [
            "date",
            "weekday",
            "closure_reason",
            "digital_sessions",
            "tickets_sold",
        ]
        if "tickets_sold" in calendar.columns
        else [
            "date",
            "weekday",
            "closure_reason",
            "digital_sessions",
        ]
    ]
    .sort_values(
        "digital_sessions",
        ascending=False
    )
)

None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.

if len(closed_activity):

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

else:
    None  # Console output removed for public staging.


# ============================================================
# 17. DIGILOGIDE KATVUS KUUTI
# ============================================================

None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.

display = monthly.copy()

display["kuu"] = (
    display["month_date"]
    .dt.strftime("%Y-%m")
)

cols = [
    "kuu",
    "calendar_days",
    "log_days",
    "log_coverage_pct",
    "digital_sessions",
    "digital_activity_closed_days",
]

None  # Console output removed for public staging.


# ============================================================
# 18. KATVUSE KATEGOORIA
# ============================================================

monthly["log_coverage_level"] = pd.cut(
    monthly["log_coverage_pct"],
    bins=[
        -0.01,
        0,
        50,
        90,
        99.999,
        100.001,
    ],
    labels=[
        "Andmed puuduvad",
        "Väga osaline",
        "Osaline",
        "Peaaegu täielik",
        "Täielik",
    ]
)

# Uuesti salvestame, nüüd koos coverage level väljaga.
monthly.to_parquet(
    MONTHLY_OUTPUT_FILE,
    index=False
)


None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.

None  # Console output removed for public staging.
None  # Console output removed for public staging.

None  # Console output removed for public staging.
None  # Console output removed for public staging.