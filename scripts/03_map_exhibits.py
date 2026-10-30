from _public_config import workspace_root, device_sheet
from pathlib import Path

import pandas as pd


# ============================================================
# KAUSTAD JA FAILID
# ============================================================

PROJECT_DIR = workspace_root()

EVENTS_FILE = PROJECT_DIR / "data_clean" / "events_raw.csv"

DEVICE_FILE = (
    PROJECT_DIR
    / "data_raw"
    / "Device_id.xlsx"
)

COORDINATES_FILE = (
    PROJECT_DIR
    / "data_raw"
    / "coordinates.csv"
)

LANGUAGE_FILE = (
    PROJECT_DIR
    / "data_raw"
    / "Cards - languages.csv"
)

OUTPUT_DIR = (
    PROJECT_DIR
    / "data_clean"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "events_mapped.csv"
)

LOOKUP_FILE = (
    OUTPUT_DIR
    / "exhibit_lookup.csv"
)

UNMATCHED_FILE = (
    OUTPUT_DIR
    / "unmatched_readers.csv"
)

DUPLICATES_FILE = (
    OUTPUT_DIR
    / "removed_duplicate_events.csv"
)


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
    # 1. LOGID
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    events = pd.read_csv(
        EVENTS_FILE,
        low_memory=False,
        dtype={
            "reader": "string",
            "card_id": "string",
            "device_id": "string",
            "source_file": "string",
        },
    )

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 2. READER LAHTI
    # --------------------------------------------------------

    events["reader_mac"] = (
        events["reader"]
        .str.extract(
            r"^(.+)/([01])$",
            expand=True,
        )[0]
        .str.lower()
        .str.strip()
    )

    events["action_code"] = (
        events["reader"]
        .str.extract(
            r"/([01])$",
            expand=False,
        )
    )

    events["action_type"] = (
        events["action_code"]
        .map(
            {
                "0": "language_change",
                "1": "take_museum_with_you",
            }
        )
        .fillna("unknown")
    )

    events["card_id"] = clean_text(
        events["card_id"]
    )

    events["device_id"] = clean_text(
        events["device_id"]
    )

    # --------------------------------------------------------
    # 3. KEELED
    # --------------------------------------------------------

    None  # Console output removed for public staging.

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
        clean_text(
            languages["Description"]
        )
    )

    language_lookup = dict(
        zip(
            languages["language_code"],
            languages["language"],
        )
    )

    events["language"] = (
        events["card_id"]
        .map(language_lookup)
    )

    # --------------------------------------------------------
    # 4. DUPLIKAADID
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    duplicate_columns = [
        "timestamp",
        "reader",
        "card_id",
        "device_id",
    ]

    duplicate_mask = (
        events
        .duplicated(
            subset=duplicate_columns,
            keep="first",
        )
    )

    duplicates = (
        events[
            duplicate_mask
        ]
        .copy()
    )

    None  # Console output removed for public staging.

    if len(duplicates) > 0:

        duplicates.to_csv(
            DUPLICATES_FILE,
            index=False,
            encoding="utf-8",
        )

    events = (
        events[
            ~duplicate_mask
        ]
        .copy()
        .reset_index(drop=True)
    )

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 5. DEVICE_ID.XLSX
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    devices = pd.read_excel(
        DEVICE_FILE,
        sheet_name=device_sheet(),
    )

    devices = devices.rename(
        columns={
            "Name": "device_name",
            "Supported device": "supported_device",
            "Sequence": "sequence",
            "Device": "reader_mac",
            'Regrouping of "names", vol 1': "group_name_1",
            'Regrouping of "names", vol 2': "group_name_2",
            "Topic": "topic",

            # Neid EI kasuta enam lõpliku
            # asukoha määramiseks.
            "Coordinate x": "device_x_old",
            "Coordinate y": "device_y_old",
        }
    )

    for column in [
        "device_name",
        "supported_device",
        "sequence",
        "reader_mac",
        "group_name_1",
        "group_name_2",
        "topic",
    ]:

        if column in devices.columns:

            devices[column] = (
                clean_text(
                    devices[column]
                )
            )

    devices["reader_mac"] = (
        devices["reader_mac"]
        .str.lower()
        .str.strip()
    )

    # --------------------------------------------------------
    # 6. T-KOOD
    # --------------------------------------------------------

    # Näiteks:
    #
    # SYNTHETIC_POINT_A-E1
    # ->
    # SYNTHETIC_POINT_A

    devices["t_code"] = (
        devices["device_name"]
        .str.extract(
            r"(T\d+(?:\.\d+)+)",
            expand=False,
        )
    )

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 7. CLICKERI KOORDINAADID
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    coordinates = pd.read_csv(
        COORDINATES_FILE,
        dtype={
            "code": "string",
        },
    )

    coordinates["code"] = (
        coordinates["code"]
        .str.strip()
    )

    coordinates["x"] = pd.to_numeric(
        coordinates["x"],
        errors="coerce",
    )

    coordinates["y"] = pd.to_numeric(
        coordinates["y"],
        errors="coerce",
    )

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    # Kontrollime duplikaate
    duplicate_codes = (
        coordinates["code"]
        .value_counts()
    )

    duplicate_codes = (
        duplicate_codes[
            duplicate_codes > 1
        ]
    )

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 8. KOORDINAADID T-KOODILE
    # --------------------------------------------------------

    coordinates = (
        coordinates
        .drop_duplicates(
            subset=["code"],
            keep="first",
        )
        .rename(
            columns={
                "code": "t_code"
            }
        )
    )

    # Väga oluline:
    #
    # x ja y tulevad nüüd AINULT coordinates.csv-st.

    devices = devices.merge(
        coordinates[
            [
                "t_code",
                "x",
                "y",
            ]
        ],
        on="t_code",
        how="left",
        validate="many_to_one",
    )

    # --------------------------------------------------------
    # 9. KONTROLL
    # --------------------------------------------------------

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    missing_codes = (
        devices.loc[
            devices["x"].isna()
            |
            devices["y"].isna(),
            [
                "device_name",
                "t_code",
                "reader_mac",
                "topic",
            ]
        ]
        .drop_duplicates()
    )

    if len(missing_codes) > 0:

        None  # Console output removed for public staging.

        None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 10. KOOND-EKSPONAAT
    # --------------------------------------------------------

    devices["exhibit_group"] = (
        devices["group_name_2"]
        .fillna(
            devices["group_name_1"]
        )
        .fillna(
            devices["device_name"]
        )
    )

    # --------------------------------------------------------
    # 11. READER LOOKUP
    # --------------------------------------------------------

    lookup_columns = [
        "reader_mac",
        "device_name",
        "t_code",
        "exhibit_group",
        "group_name_1",
        "group_name_2",
        "topic",
        "supported_device",
        "sequence",
        "x",
        "y",
    ]

    lookup = (
        devices[
            lookup_columns
        ]
        .dropna(
            subset=["reader_mac"]
        )
        .drop_duplicates(
            subset=["reader_mac"],
            keep="first",
        )
        .copy()
    )

    lookup.to_csv(
        LOOKUP_FILE,
        index=False,
        encoding="utf-8",
    )

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 12. LOGIDE ÜHENDAMINE
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    mapped = events.merge(
        lookup,
        on="reader_mac",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    matched = (
        mapped["_merge"] == "both"
    )

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 13. KOORDINAATIDE KAETUS
    # --------------------------------------------------------

    has_coordinates = (
        mapped["x"].notna()
        &
        mapped["y"].notna()
    )

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 14. SIDUMATA READERID
    # --------------------------------------------------------

    unmatched = (
        mapped[
            ~matched
        ]
        .groupby(
            "reader_mac",
            dropna=False,
        )
        .size()
        .reset_index(
            name="event_count"
        )
        .sort_values(
            "event_count",
            ascending=False,
        )
    )

    unmatched.to_csv(
        UNMATCHED_FILE,
        index=False,
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # 15. SALVESTAMINE
    # --------------------------------------------------------

    mapped = mapped.drop(
        columns="_merge"
    )

    None  # Console output removed for public staging.

    mapped.to_csv(
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