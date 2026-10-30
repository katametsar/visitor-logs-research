from _public_config import workspace_root, device_sheet
from pathlib import Path
import pandas as pd


PROJECT_DIR = workspace_root()
INPUT_FILE = PROJECT_DIR / "data_clean" / "events_mapped.csv"


def main():

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    df = pd.read_csv(
        INPUT_FILE,
        low_memory=False,
        dtype={
            "card_id": "string",
            "device_id": "string",
            "reader": "string",
            "reader_mac": "string",
        },
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        utc=True,
        errors="coerce",
    ).dt.tz_convert("Europe/Tallinn")

    df["card_id_clean"] = (
        df["card_id"]
        .astype("string")
        .str.strip()
    )

    df["card_length"] = (
        df["card_id_clean"]
        .str.len()
    )

    # Keelekoodid
    language_map = {
        "01": "EST",
        "02": "RUS",
        "03": "ENG",
        "04": "FIN",
        "05": "FRA",
        "06": "LAT",
        "07": "GER",
        "08": "UKR",
    }

    df["language_event"] = (
        df["card_id_clean"]
        .map(language_map)
    )

    # --------------------------------------------------------
    # 1. KAS SAMA DEVICE_ID NÄEB NII KEELEKOODI KUI PIKKA KAARTI?
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    device_stats = (
        df.groupby("device_id")
        .agg(
            has_language=(
                "language_event",
                lambda x: x.notna().any()
            ),
            has_long_card=(
                "card_length",
                lambda x: (x == 18).any()
            ),
            events=("timestamp", "size"),
        )
    )

    both = device_stats[
        device_stats["has_language"]
        &
        device_stats["has_long_card"]
    ]

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 2. NÄITED
    # --------------------------------------------------------

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    example_devices = (
        both
        .sort_values("events", ascending=False)
        .head(10)
        .index
    )

    for device in example_devices:

        None  # Console output removed for public staging.
        None  # Console output removed for public staging.
        None  # Console output removed for public staging.

        example = (
            df[df["device_id"] == device]
            .sort_values("timestamp")
            [
                [
                    "timestamp",
                    "reader",
                    "card_id_clean",
                    "language_event",
                    "t_code",
                    "topic",
                ]
            ]
            .head(40)
        )

        None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 3. KEELEKOODILE JÄRGNEV PIKK CARD_ID
    # --------------------------------------------------------

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    df = df.sort_values(
        ["device_id", "timestamp"]
    )

    df["next_card"] = (
        df.groupby("device_id")["card_id_clean"]
        .shift(-1)
    )

    df["next_card_length"] = (
        df["next_card"]
        .str.len()
    )

    df["next_timestamp"] = (
        df.groupby("device_id")["timestamp"]
        .shift(-1)
    )

    df["seconds_to_next"] = (
        (
            df["next_timestamp"]
            -
            df["timestamp"]
        )
        .dt.total_seconds()
    )

    language_rows = df[
        df["language_event"].notna()
    ].copy()

    None  # Console output removed for public staging.

    followed_by_long = language_rows[
        language_rows["next_card_length"] == 18
    ]

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.


if __name__ == "__main__":
    main()