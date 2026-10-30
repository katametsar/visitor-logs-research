from _public_config import workspace_root, device_sheet
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image


PROJECT_DIR = workspace_root()

DEVICE_FILE = PROJECT_DIR / "data_raw" / "Device_id.xlsx"
MAP_FILE = PROJECT_DIR / "data_raw" / "museum_map.png"

OUTPUT_FILE = PROJECT_DIR / "outputs" / "coordinate_check.png"


None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.


# ------------------------------------------------------------
# 1. KAART
# ------------------------------------------------------------

img = Image.open(MAP_FILE)

width, height = img.size

None  # Console output removed for public staging.
None  # Console output removed for public staging.


# ------------------------------------------------------------
# 2. DEVICE TABEL
# ------------------------------------------------------------

df = pd.read_excel(
    DEVICE_FILE,
    sheet_name=device_sheet()
)

df["Coordinate x"] = pd.to_numeric(
    df["Coordinate x"],
    errors="coerce"
)

df["Coordinate y"] = pd.to_numeric(
    df["Coordinate y"],
    errors="coerce"
)

points = df[
    df["Coordinate x"].notna()
    &
    df["Coordinate y"].notna()
].copy()


None  # Console output removed for public staging.

None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.

None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.


# ------------------------------------------------------------
# 3. VALIME MÕNED KONTROLLPUNKTID
# ------------------------------------------------------------

# Võtame eri kohtadest rea punkte,
# et oleks näha kogu koordinaadisüsteemi käitumine.

sample = (
    points
    .drop_duplicates(
        subset=["Coordinate x", "Coordinate y"]
    )
    .iloc[::20]
    .copy()
)

None  # Console output removed for public staging.
None  # Console output removed for public staging.


# ------------------------------------------------------------
# 4. JOONISTAME ALGSED X/Y KOORDINAADID
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(20, 11)
)

ax.imshow(
    img,
    origin="upper"
)

ax.scatter(
    sample["Coordinate x"],
    sample["Coordinate y"],
    s=60
)


# ------------------------------------------------------------
# 5. LISAME T-KOODID
# ------------------------------------------------------------

for _, row in sample.iterrows():

    ax.annotate(
        str(row["Name"]),
        (
            row["Coordinate x"],
            row["Coordinate y"]
        ),
        fontsize=7,
        xytext=(4, 4),
        textcoords="offset points"
    )


# ------------------------------------------------------------
# 6. TELJED JÄTAME PRAEGU NÄHTAVAKS
# ------------------------------------------------------------

ax.set_xlim(
    0,
    width
)

ax.set_ylim(
    height,
    0
)

ax.set_title(
    "Device_id.xlsx ALGSED koordinaadid museum_map.png peal"
)

ax.set_xlabel("X")
ax.set_ylabel("Y")


# ------------------------------------------------------------
# 7. SALVESTAME
# ------------------------------------------------------------

plt.tight_layout()

plt.savefig(
    OUTPUT_FILE,
    dpi=150
)

plt.close()


None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.
None  # Console output removed for public staging.

None  # Console output removed for public staging.
None  # Console output removed for public staging.