from _public_config import workspace_root, device_sheet
from pathlib import Path

import pandas as pd
from PIL import Image


# ============================================================
# KAUSTAD JA FAILID
# ============================================================

PROJECT_DIR = workspace_root()

OLD_COORDS_FILE = (
    PROJECT_DIR
    / "data_raw"
    / "coordinates.csv"
)

NEW_COORDS_FILE = (
    PROJECT_DIR
    / "visitor_map_clicker_v2"
    / "coordinates_v2.csv"
)

MAP_FILE = (
    PROJECT_DIR
    / "data_raw"
    / "museum_map.png"
)

OUTPUT_FILE = (
    PROJECT_DIR
    / "data_raw"
    / "coordinates_fixed.csv"
)

CHECK_FILE = (
    PROJECT_DIR
    / "outputs"
    / "coordinates_fixed_check.csv"
)


# ============================================================
# PÕHIPROGRAMM
# ============================================================

def main():

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 1. KAARDI MÕÕT
    # --------------------------------------------------------

    image = Image.open(MAP_FILE)

    image_width, image_height = image.size

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 2. VANA COORDINATES.CSV
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    old = pd.read_csv(
        OLD_COORDS_FILE,
        dtype={
            "code": "string",
        },
    )

    old["code"] = (
        old["code"]
        .str.strip()
    )

    old["x_old"] = pd.to_numeric(
        old["x"],
        errors="coerce",
    )

    old["y_old"] = pd.to_numeric(
        old["y"],
        errors="coerce",
    )

    old = old[
        [
            "code",
            "x_old",
            "y_old",
        ]
    ].copy()

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 3. UUS CLICKERI FAIL
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    new = pd.read_csv(
        NEW_COORDS_FILE,
        dtype={
            "code": "string",
        },
    )

    new["code"] = (
        new["code"]
        .str.strip()
    )

    new["x_new"] = pd.to_numeric(
        new["x"],
        errors="coerce",
    )

    new["y_new"] = pd.to_numeric(
        new["y"],
        errors="coerce",
    )

    new = new[
        [
            "code",
            "x_new",
            "y_new",
        ]
    ].copy()

    manually_checked = (
        new["x_new"].notna()
        &
        new["y_new"].notna()
    )

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 4. ÜHENDAME
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    combined = old.merge(
        new,
        on="code",
        how="outer",
        validate="one_to_one",
    )

    # --------------------------------------------------------
    # 5. AUTOMAATNE PARANDUS
    # --------------------------------------------------------

    # Vana clicker kasutas Y-telge vastupidises suunas.
    #
    # Vana:
    # y suureneb ülespoole
    #
    # PNG:
    # y suureneb allapoole
    #
    # Seega automaatne parandus:
    #
    # y_fixed = image_height - y_old

    combined["x_auto"] = (
        combined["x_old"]
    )

    combined["y_auto"] = (
        image_height
        -
        combined["y_old"]
    )

    # --------------------------------------------------------
    # 6. LÕPLIK X/Y
    # --------------------------------------------------------

    # Kui uus clickeriga kontrollitud punkt on olemas,
    # kasutame seda.
    #
    # Kui ei ole, kasutame automaatselt parandatud vana punkti.

    combined["x"] = (
        combined["x_new"]
        .fillna(
            combined["x_auto"]
        )
    )

    combined["y"] = (
        combined["y_new"]
        .fillna(
            combined["y_auto"]
        )
    )

    combined["coordinate_source"] = "auto_flipped_old"

    combined.loc[
        combined["x_new"].notna()
        &
        combined["y_new"].notna(),
        "coordinate_source"
    ] = "manual_v2"

    # --------------------------------------------------------
    # 7. KONTROLL: UUS VS AUTOMAATNE
    # --------------------------------------------------------

    checked = combined[
        combined["coordinate_source"]
        == "manual_v2"
    ].copy()

    checked["x_difference"] = (
        checked["x_new"]
        -
        checked["x_auto"]
    )

    checked["y_difference"] = (
        checked["y_new"]
        -
        checked["y_auto"]
    )

    checked["distance_difference"] = (
        (
            checked["x_difference"] ** 2
            +
            checked["y_difference"] ** 2
        )
        ** 0.5
    )

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 8. KVALITEEDIKONTROLL
    # --------------------------------------------------------

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    missing = (
        combined["x"].isna()
        |
        combined["y"].isna()
    )

    None  # Console output removed for public staging.

    # Kas punktid mahuvad pildi sisse?
    outside = (
        (combined["x"] < 0)
        |
        (combined["x"] > image_width)
        |
        (combined["y"] < 0)
        |
        (combined["y"] > image_height)
    )

    None  # Console output removed for public staging.

    if outside.any():

        None  # Console output removed for public staging.

        None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 9. SALVESTAME LÕPLIKU FAILI
    # --------------------------------------------------------

    final = combined[
        [
            "code",
            "x",
            "y",
        ]
    ].copy()

    final["x"] = (
        final["x"]
        .round()
        .astype("Int64")
    )

    final["y"] = (
        final["y"]
        .round()
        .astype("Int64")
    )

    final = (
        final
        .sort_values("code")
        .reset_index(drop=True)
    )

    final.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # 10. SALVESTAME KA KONTROLLFAILI
    # --------------------------------------------------------

    combined[
        [
            "code",
            "x_old",
            "y_old",
            "x_auto",
            "y_auto",
            "x_new",
            "y_new",
            "x",
            "y",
            "coordinate_source",
        ]
    ].to_csv(
        CHECK_FILE,
        index=False,
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # 11. LÕPP
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