from _public_config import workspace_root, device_sheet
from pathlib import Path
import pandas as pd


# ============================================================
# ASUKOHAD
# ============================================================

BASE_DIR = workspace_root()

DATA_RAW = BASE_DIR / "data_raw"
DASH_DATA = BASE_DIR / "dashboard_data"

HOLIDAY_FILE = (
    DATA_RAW
    / "school_holidays.xlsx"
)

CONTEXT_FILE = (
    DASH_DATA
    / "daily_context_with_tickets.parquet"
)

OUTPUT_HOLIDAYS = (
    DASH_DATA
    / "school_holidays_daily.parquet"
)

OUTPUT_CONTEXT = (
    DASH_DATA
    / "daily_context_final.parquet"
)


None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.


# ============================================================
# 1. LOEN KOOLIVAHEAJAD
# ============================================================

None  # Console output removed for public staging.

holidays = pd.read_excel(
    HOLIDAY_FILE,
    sheet_name="Leht1"
)

None  # Console output removed for public staging.
None  # Console output removed for public staging.


# ============================================================
# 2. PUHASTAN
# ============================================================

holidays["Country"] = (
    holidays["Country"]
    .astype(str)
    .str.strip()
)

holidays["Date start"] = pd.to_datetime(
    holidays["Date start"],
    errors="coerce"
).dt.normalize()

holidays["Date end"] = pd.to_datetime(
    holidays["Date end"],
    errors="coerce"
).dt.normalize()

holidays = holidays[
    holidays["Date start"].notna()
    &
    holidays["Date end"].notna()
].copy()

None  # Console output removed for public staging.
None  # Console output removed for public staging.

None  # Console output removed for public staging.


# ============================================================
# 3. TEEN ÜHE REA IGA VAHEAJAPÄEVA KOHTA
# ============================================================

None  # Console output removed for public staging.

daily_rows = []

for _, row in holidays.iterrows():

    country = row["Country"]
    start = row["Date start"]
    end = row["Date end"]

    dates = pd.date_range(
        start=start,
        end=end,
        freq="D"
    )

    for date in dates:
        daily_rows.append(
            {
                "date": date.normalize(),
                "country": country,
            }
        )


holiday_days_long = pd.DataFrame(
    daily_rows
)

# Kui mõni päev esineb mingil põhjusel
# sama riigi tabelis mitu korda, eemaldame duplikaadi.

holiday_days_long = (
    holiday_days_long
    .drop_duplicates(
        subset=[
            "date",
            "country",
        ]
    )
)


# ============================================================
# 4. TEEN RIIGID ERALDI VEERGUDEKS
# ============================================================

holiday_days = (
    holiday_days_long
    .assign(value=True)
    .pivot_table(
        index="date",
        columns="country",
        values="value",
        aggfunc="max",
        fill_value=False
    )
    .reset_index()
)

holiday_days.columns.name = None


# ============================================================
# 5. STANDARDISEERIN VEERUNIMED
# ============================================================

country_mapping = {
    "Estonia": "school_holiday_estonia",
    "Latvia": "school_holiday_latvia",
    "Finland": "school_holiday_finland",
}

holiday_days = holiday_days.rename(
    columns=country_mapping
)

expected_columns = [
    "school_holiday_estonia",
    "school_holiday_latvia",
    "school_holiday_finland",
]

# Kui mõni riik on failis teise nimega või puudub,
# ei lase me skriptil katki minna.

for col in expected_columns:
    if col not in holiday_days.columns:
        holiday_days[col] = False


for col in expected_columns:
    holiday_days[col] = (
        holiday_days[col]
        .fillna(False)
        .astype(bool)
    )


# ============================================================
# 6. LISAN KOONDTUNNUSED
# ============================================================

holiday_days["school_holiday_any"] = (
    holiday_days[
        expected_columns
    ]
    .any(axis=1)
)

holiday_days["school_holiday_countries"] = (
    holiday_days[
        expected_columns
    ]
    .apply(
        lambda row: ", ".join(
            [
                country
                for country, col
                in [
                    (
                        "Estonia",
                        "school_holiday_estonia"
                    ),
                    (
                        "Latvia",
                        "school_holiday_latvia"
                    ),
                    (
                        "Finland",
                        "school_holiday_finland"
                    ),
                ]
                if bool(row[col])
            ]
        ),
        axis=1
    )
)


# ============================================================
# 7. SALVESTAN KOOLIVAHEAEGADE TABELI
# ============================================================

holiday_days = (
    holiday_days
    .sort_values("date")
    .reset_index(drop=True)
)

holiday_days.to_parquet(
    OUTPUT_HOLIDAYS,
    index=False
)

None  # Console output removed for public staging.

None  # Console output removed for public staging.

for col in expected_columns:
    None  # Console output removed for public staging.


# ============================================================
# 8. LOEN SENISE PÄEVAKONTEKSTI
# ============================================================

None  # Console output removed for public staging.

context = pd.read_parquet(
    CONTEXT_FILE
)

context["date"] = pd.to_datetime(
    context["date"],
    errors="coerce"
).dt.normalize()

None  # Console output removed for public staging.


# ============================================================
# 9. ÜHENDAN KOOLIVAHEAJAD
# ============================================================

context = context.merge(
    holiday_days[
        [
            "date",
            "school_holiday_estonia",
            "school_holiday_latvia",
            "school_holiday_finland",
            "school_holiday_any",
            "school_holiday_countries",
        ]
    ],
    on="date",
    how="left"
)


# Päev, mida holiday_days tabelis ei olnud,
# tähendab: selles kolmes riigis polnud vaheaega.

for col in [
    "school_holiday_estonia",
    "school_holiday_latvia",
    "school_holiday_finland",
    "school_holiday_any",
]:
    context[col] = (
        context[col]
        .fillna(False)
        .astype(bool)
    )

context["school_holiday_countries"] = (
    context["school_holiday_countries"]
    .fillna("")
)


# ============================================================
# 10. KONTROLL
# ============================================================

None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.

None  # Console output removed for public staging.

for col in expected_columns:
    None  # Console output removed for public staging.


None  # Console output removed for public staging.

sample = context.loc[
    context["school_holiday_any"],
    [
        "date",
        "school_holiday_estonia",
        "school_holiday_latvia",
        "school_holiday_finland",
        "school_holiday_countries",
    ]
].head(30)

None  # Console output removed for public staging.


# ============================================================
# 11. SALVESTAN LÕPLIKU PÄEVAKONTEKSTI
# ============================================================

context = (
    context
    .sort_values("date")
    .reset_index(drop=True)
)

context.to_parquet(
    OUTPUT_CONTEXT,
    index=False
)


None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.

None  # Console output removed for public staging.

None  # Console output removed for public staging.