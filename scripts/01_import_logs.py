from __future__ import annotations

from _public_config import workspace_root, device_sheet

import re
from pathlib import Path

import pandas as pd


# ============================================================
# KAUSTAD JA FAILID
# ============================================================

PROJECT_DIR = workspace_root()

LOG_DIR = PROJECT_DIR / "data_raw" / "Logide_failid"
OUTPUT_DIR = PROJECT_DIR / "data_clean"

OUTPUT_FILE = OUTPUT_DIR / "events_raw.csv"
FAILED_OUTPUT_FILE = OUTPUT_DIR / "unparsed_log_rows.csv"


# ============================================================
# LOGIREA MUSTER
# ============================================================

# Näide:
#
# [02/Jan/2026:11:06:48 +0200]
# SYNTHETIC_READER_A/0:
# SYNTHETIC_IDENTIFIER_A
# SYNTHETIC_IDENTIFIER_A
#
# Väljad:
# timestamp
# reader
# card_id
# device_id

LOG_PATTERN = re.compile(
    r"""
    ^\[
        (?P<timestamp>[^\]]+)
    \]
    \s+
    (?P<reader>[0-9a-fA-F:]+/\d+)
    :
    \s+
    (?P<card_id>\S+)
    \s+
    (?P<device_id>\S+)
    \s*$
    """,
    re.VERBOSE,
)


# ============================================================
# ÜHE REA PARSIMINE
# ============================================================

def parse_log_line(
    line: str,
    source_file: str,
    line_number: int,
) -> dict | None:

    line = line.strip()

    if not line:
        return None

    match = LOG_PATTERN.match(line)

    if not match:
        return None

    row = match.groupdict()

    row["source_file"] = source_file
    row["line_number"] = line_number
    row["raw_line"] = line

    return row


# ============================================================
# ÜHE LOGIFAILI LUGEMINE
# ============================================================

def read_log_file(path: Path) -> tuple[list[dict], list[dict]]:

    encodings = [
        "utf-8",
        "latin-1",
    ]

    last_error = None

    for encoding in encodings:

        parsed_rows = []
        failed_rows = []

        try:

            with path.open(
                "r",
                encoding=encoding,
                errors="strict",
            ) as file:

                for line_number, line in enumerate(
                    file,
                    start=1,
                ):

                    if not line.strip():
                        continue

                    parsed = parse_log_line(
                        line=line,
                        source_file=path.name,
                        line_number=line_number,
                    )

                    if parsed is None:

                        failed_rows.append(
                            {
                                "source_file": path.name,
                                "line_number": line_number,
                                "raw_line": line.strip(),
                            }
                        )

                    else:

                        parsed_rows.append(parsed)

            return parsed_rows, failed_rows

        except UnicodeDecodeError as error:

            last_error = error
            continue

    raise UnicodeError(
        f"Faili ei õnnestunud lugeda: {path}\n"
        f"Viimane viga: {last_error}"
    )


# ============================================================
# AJATEMPLITE PARSIMINE
# ============================================================

def parse_timestamps(events: pd.DataFrame) -> pd.DataFrame:

    events = events.copy()

    # Säilitame originaalväärtuse.
    events["timestamp_raw"] = events["timestamp"]

    # Logides esineb nii +0200 kui +0300.
    #
    # Seetõttu:
    # 1. parsime kõik esmalt UTC-sse
    # 2. teisendame Eesti kohalikku aega
    #
    # Nii töötab korrektselt ka suve-/talveaja vahetus.

    events["timestamp"] = pd.to_datetime(
        events["timestamp"],
        format="%d/%b/%Y:%H:%M:%S %z",
        errors="coerce",
        utc=True,
    )

    events["timestamp"] = (
        events["timestamp"]
        .dt.tz_convert("Europe/Tallinn")
    )

    return events


# ============================================================
# PÕHIPROGRAMM
# ============================================================

def main() -> None:

    if not LOG_DIR.exists():

        raise FileNotFoundError(
            f"Logifailide kausta ei leitud:\n{LOG_DIR}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # LEIAME LOGIFAILID
    # --------------------------------------------------------

    log_files = sorted(
        path
        for path in LOG_DIR.iterdir()
        if path.is_file()
        and (
            ".log" in path.name.lower()
            or path.suffix.lower() == ".txt"
        )
    )

    if not log_files:

        raise FileNotFoundError(
            f"Kaustas ei leitud logifaile:\n{LOG_DIR}"
        )

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    all_rows = []
    all_failed_rows = []

    # --------------------------------------------------------
    # LOEME KÕIK FAILID
    # --------------------------------------------------------

    for path in log_files:

        parsed_rows, failed_rows = read_log_file(path)

        all_rows.extend(parsed_rows)
        all_failed_rows.extend(failed_rows)

        None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # KONTROLL
    # --------------------------------------------------------

    if not all_rows:

        raise ValueError(
            "Ühtegi logirida ei õnnestunud parsida."
        )

    # --------------------------------------------------------
    # DATAFRAME
    # --------------------------------------------------------

    events = pd.DataFrame(all_rows)

    # --------------------------------------------------------
    # AJATEMPLID
    # --------------------------------------------------------

    events = parse_timestamps(events)

    # --------------------------------------------------------
    # TEKSTIVEERUD
    # --------------------------------------------------------

    for column in [
        "reader",
        "card_id",
        "device_id",
        "source_file",
    ]:

        events[column] = (
            events[column]
            .astype("string")
            .str.strip()
        )

    # --------------------------------------------------------
    # AJAST TULETATUD VEERUD
    # --------------------------------------------------------

    events["date"] = (
        events["timestamp"]
        .dt.date
    )

    events["time"] = (
        events["timestamp"]
        .dt.strftime("%H:%M:%S")
    )

    events["hour"] = (
        events["timestamp"]
        .dt.hour
    )

    events["weekday"] = (
        events["timestamp"]
        .dt.day_name()
    )

    events["year"] = (
        events["timestamp"]
        .dt.year
    )

    events["month"] = (
        events["timestamp"]
        .dt.month
    )

    events["day"] = (
        events["timestamp"]
        .dt.day
    )

    # --------------------------------------------------------
    # READERI LAHTIVÕTMINE
    # --------------------------------------------------------

    # Näiteks:
    #
    # SYNTHETIC_READER_A/0
    #
    # ->
    #
    # reader_mac = SYNTHETIC_READER_A
    # reader_channel = 0

    events["reader_mac"] = (
        events["reader"]
        .str.replace(
            r"/\d+$",
            "",
            regex=True,
        )
    )

    events["reader_channel"] = (
        events["reader"]
        .str.extract(
            r"/(\d+)$"
        )[0]
        .astype("Int64")
    )

    # --------------------------------------------------------
    # SORTEERIMINE
    # --------------------------------------------------------

    events = (
        events
        .sort_values(
            [
                "timestamp",
                "source_file",
                "line_number",
            ],
            na_position="last",
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # DUPLIKAATIDE KONTROLL
    # --------------------------------------------------------

    duplicate_mask = events.duplicated(
        subset=[
            "timestamp",
            "reader",
            "card_id",
            "device_id",
        ],
        keep=False,
    )

    duplicate_count = duplicate_mask.sum()

    exact_duplicate_count = events.duplicated(
        subset=[
            "timestamp",
            "reader",
            "card_id",
            "device_id",
        ],
        keep="first",
    ).sum()

    # Praegu EI kustuta duplikaate.
    #
    # Kõigepealt uurime, miks need tekivad:
    # - sama sündmus mitmes failis?
    # - logifaili koopia?
    # - päris korduv interaktsioon?

    # --------------------------------------------------------
    # SALVESTAMINE
    # --------------------------------------------------------

    events.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )

    failed_df = pd.DataFrame(all_failed_rows)

    if len(failed_df) > 0:

        failed_df.to_csv(
            FAILED_OUTPUT_FILE,
            index=False,
            encoding="utf-8",
        )

    else:

        pd.DataFrame(
            columns=[
                "source_file",
                "line_number",
                "raw_line",
            ]
        ).to_csv(
            FAILED_OUTPUT_FILE,
            index=False,
            encoding="utf-8",
        )

    # --------------------------------------------------------
    # KOKKUVÕTE
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

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # AJAVAHEMIK
    # --------------------------------------------------------

    if events["timestamp"].notna().any():

        None  # Console output removed for public staging.

        None  # Console output removed for public staging.

        None  # Console output removed for public staging.

        None  # Console output removed for public staging.

    # --------------------------------------------------------
    # AASTAD
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    yearly = (
        events["year"]
        .value_counts()
        .sort_index()
    )

    for year, count in yearly.items():

        None  # Console output removed for public staging.

    # --------------------------------------------------------
    # VÄLJUNDID
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.


# ============================================================
# KÄIVITAMINE
# ============================================================

if __name__ == "__main__":
    main()