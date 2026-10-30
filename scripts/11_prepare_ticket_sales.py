from _public_config import workspace_root, device_sheet
from pathlib import Path
import pandas as pd


BASE_DIR = workspace_root()

DATA_RAW = BASE_DIR / "data_raw"
DASH_DATA = BASE_DIR / "dashboard_data"

TICKET_FILE = (
    DATA_RAW
    / "ticket_sales.xlsx"
)

DAILY_CONTEXT_FILE = (
    DASH_DATA
    / "daily_context.parquet"
)

OUTPUT_TICKETS = (
    DASH_DATA
    / "ticket_sales_daily.parquet"
)

OUTPUT_CONTEXT = (
    DASH_DATA
    / "daily_context_with_tickets.parquet"
)


None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.


# ============================================================
# 1. LOEN PILETIMÜÜGI
# ============================================================

None  # Console output removed for public staging.

tickets = pd.read_excel(
    TICKET_FILE,
    sheet_name="Page 1"
)

None  # Console output removed for public staging.

None  # Console output removed for public staging.


# ============================================================
# 2. KUUPÄEVAD JA ARVUD
# ============================================================

tickets["date"] = pd.to_datetime(
    tickets["Day"],
    errors="coerce"
).dt.normalize()

tickets["ticket_count"] = pd.to_numeric(
    tickets["Amount of tickets"],
    errors="coerce"
)

tickets["paid_sum"] = pd.to_numeric(
    tickets["Paid sum"],
    errors="coerce"
)

tickets = tickets[
    tickets["date"].notna()
    &
    tickets["ticket_count"].notna()
].copy()


# ============================================================
# 3. PÄEVANE KOOND
# ============================================================

None  # Console output removed for public staging.

daily_tickets = (
    tickets
    .groupby(
        "date",
        as_index=False
    )
    .agg(
        tickets_sold=(
            "ticket_count",
            "sum"
        ),
        ticket_transactions=(
            "ticket_count",
            "size"
        ),
        paid_sum=(
            "paid_sum",
            "sum"
        ),
    )
)

daily_tickets["tickets_sold"] = (
    daily_tickets["tickets_sold"]
    .round()
    .astype(int)
)

daily_tickets["year"] = (
    daily_tickets["date"]
    .dt.year
)

daily_tickets["month"] = (
    daily_tickets["date"]
    .dt.month
)

daily_tickets["weekday_num"] = (
    daily_tickets["date"]
    .dt.dayofweek
)

None  # Console output removed for public staging.

None  # Console output removed for public staging.

None  # Console output removed for public staging.

None  # Console output removed for public staging.

None  # Console output removed for public staging.

None  # Console output removed for public staging.


# ============================================================
# 4. SALVESTAN PILETIMÜÜGI
# ============================================================

daily_tickets.to_parquet(
    OUTPUT_TICKETS,
    index=False
)

None  # Console output removed for public staging.


# ============================================================
# 5. ÜHENDAN KÜLASTUSLOGIDEGA
# ============================================================

None  # Console output removed for public staging.

daily = pd.read_parquet(
    DAILY_CONTEXT_FILE
)

daily["date"] = pd.to_datetime(
    daily["date"]
).dt.normalize()

combined = daily.merge(
    daily_tickets[
        [
            "date",
            "tickets_sold",
            "ticket_transactions",
            "paid_sum",
        ]
    ],
    on="date",
    how="left"
)


# ============================================================
# 6. DIGITAALSE KASUTUSE OSAKAAL
# ============================================================

# daily_summary tabeli "sessions" tähendab siin
# digitaalse süsteemi päevaseid kasutussessioone.

combined["digital_sessions"] = (
    pd.to_numeric(
        combined["sessions"],
        errors="coerce"
    )
)

combined["ticket_usage_rate_pct"] = (
    combined["digital_sessions"]
    /
    combined["tickets_sold"]
    *
    100
)

# Kui piletimüügi andmeid pole või piletite arv = 0,
# jätame osakaalu tühjaks.

combined.loc[
    combined["tickets_sold"].isna()
    |
    (combined["tickets_sold"] <= 0),
    "ticket_usage_rate_pct"
] = pd.NA


# ============================================================
# 7. KONTROLL
# ============================================================

None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.

over_100 = combined[
    combined["ticket_usage_rate_pct"] > 100
]

None  # Console output removed for public staging.

if len(over_100):

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.


# ============================================================
# 8. SALVESTAN ÜHENDTABELI
# ============================================================

combined.to_parquet(
    OUTPUT_CONTEXT,
    index=False
)

None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.

None  # Console output removed for public staging.

None  # Console output removed for public staging.