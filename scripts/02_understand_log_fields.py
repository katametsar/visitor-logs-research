from _public_config import workspace_root, device_sheet
from pathlib import Path

import pandas as pd


# ============================================================
# KAUSTAD
# ============================================================

PROJECT_DIR = workspace_root()

EVENTS_FILE = PROJECT_DIR / "data_clean" / "events_raw.csv"
LANGUAGE_FILE = PROJECT_DIR / "data_raw" / "Cards - languages.csv"

OUTPUT_DIR = PROJECT_DIR / "data_clean"

OUTPUT_SUMMARY = OUTPUT_DIR / "log_action_summary.csv"
OUTPUT_SAMPLE = OUTPUT_DIR / "log_action_samples.csv"


# ============================================================
# PÕHIPROGRAMM
# ============================================================

def main():

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

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
        },
    )

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 2. READER LAHTI
    # --------------------------------------------------------

    # Näide:
    #
    # SYNTHETIC_READER_A/0
    #
    # reader_mac     = SYNTHETIC_READER_A
    # reader_channel = 0

    events["reader_mac"] = (
        events["reader"]
        .str.extract(
            r"^(.+)/[01]$",
            expand=False,
        )
    )

    events["reader_channel"] = (
        events["reader"]
        .str.extract(
            r"/([01])$",
            expand=False,
        )
    )

    # --------------------------------------------------------
    # 3. TEGEVUSE TÜÜP
    # --------------------------------------------------------

    events["action_type"] = events["reader_channel"].map(
        {
            "0": "language_change",
            "1": "take_museum_with_you",
        }
    )

    # Kui kunagi leidub midagi peale 0 või 1,
    # jääb see praegu unknown.
    events["action_type"] = (
        events["action_type"]
        .fillna("unknown")
    )

    # --------------------------------------------------------
    # 4. CARD_ID PUHASTAMINE
    # --------------------------------------------------------

    events["card_id_clean"] = (
        events["card_id"]
        .astype("string")
        .str.strip()
    )

    # Vaatame pikkust.
    events["card_id_length"] = (
        events["card_id_clean"]
        .str.len()
    )

    # --------------------------------------------------------
    # 5. KEELED
    # --------------------------------------------------------

    languages = pd.read_csv(
        LANGUAGE_FILE,
        dtype={
            "ID": "string",
            "Description": "string",
        },
    )

    languages["language_id"] = (
        languages["ID"]
        .astype("string")
        .str.strip()
        .str.zfill(2)
    )

    languages["language"] = (
        languages["Description"]
        .astype("string")
        .str.strip()
    )

    language_lookup = dict(
        zip(
            languages["language_id"],
            languages["language"],
        )
    )

    # Näiteks:
    # 03 -> ENG
    #
    # Ainult siis, kui card_id on üks teadaolevatest
    # keelekoodidest.

    events["language"] = (
        events["card_id_clean"]
        .map(language_lookup)
    )

    # --------------------------------------------------------
    # 6. KAS CARD_ID NÄEB VÄLJA NAGU KEELEKOOD?
    # --------------------------------------------------------

    events["is_language_code"] = (
        events["language"]
        .notna()
    )

    # --------------------------------------------------------
    # 7. ÜLDSTATISTIKA
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

    # --------------------------------------------------------
    # 8. /0 JA /1 ERALDI
    # --------------------------------------------------------

    for channel in ["0", "1"]:

        subset = events[
            events["reader_channel"] == channel
        ]

        None  # Console output removed for public staging.
        None  # Console output removed for public staging.

        if channel == "0":
            None  # Console output removed for public staging.
        else:
            None  # Console output removed for public staging.

        None  # Console output removed for public staging.

        None  # Console output removed for public staging.

        None  # Console output removed for public staging.

        None  # Console output removed for public staging.

        None  # Console output removed for public staging.

        None  # Console output removed for public staging.

        if len(subset) > 0:

            pct = (
                subset["is_language_code"]
                .mean()
                * 100
            )

            None  # Console output removed for public staging.

        None  # Console output removed for public staging.

        None  # Console output removed for public staging.

        None  # Console output removed for public staging.

        None  # Console output removed for public staging.

        None  # Console output removed for public staging.

        None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 9. KEELEVAHETUSTE TABEL
    # --------------------------------------------------------

    language_events = events[
        events["reader_channel"] == "0"
    ]

    language_counts = (
        language_events
        .groupby(
            [
                "language",
                "card_id_clean",
            ],
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

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 10. CROSS-TABEL
    # --------------------------------------------------------

    cross = pd.crosstab(
        events["reader_channel"],
        events["is_language_code"],
        margins=True,
    )

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 11. NÄIDISREAD
    # --------------------------------------------------------

    sample_columns = [
        "timestamp",
        "reader",
        "reader_mac",
        "reader_channel",
        "action_type",
        "card_id_clean",
        "language",
        "device_id",
    ]

    samples = []

    for action in [
        "language_change",
        "take_museum_with_you",
    ]:

        subset = events[
            events["action_type"] == action
        ]

        if len(subset) > 0:

            samples.append(
                subset[
                    sample_columns
                ].head(100)
            )

    if samples:

        sample_df = pd.concat(
            samples,
            ignore_index=True,
        )

        sample_df.to_csv(
            OUTPUT_SAMPLE,
            index=False,
            encoding="utf-8",
        )

    # --------------------------------------------------------
    # 12. KOKKUVÕTTE CSV
    # --------------------------------------------------------

    summary = (
        events
        .groupby(
            [
                "reader_channel",
                "action_type",
                "card_id_length",
                "is_language_code",
            ],
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

    summary.to_csv(
        OUTPUT_SUMMARY,
        index=False,
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # 13. LÕPP
    # --------------------------------------------------------

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.


if __name__ == "__main__":
    main()