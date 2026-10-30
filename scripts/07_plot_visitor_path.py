from _public_config import workspace_root, device_sheet
from pathlib import Path
import base64

import pandas as pd
import plotly.graph_objects as go
from PIL import Image


# ============================================================
# KAUSTAD JA FAILID
# ============================================================

PROJECT_DIR = workspace_root()

EVENTS_FILE = PROJECT_DIR / "data_clean" / "visitor_events.csv"
SESSIONS_FILE = PROJECT_DIR / "data_clean" / "sessions_final.csv"
MAP_FILE = PROJECT_DIR / "data_raw" / "museum_map.png"

OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_FILE = OUTPUT_DIR / "visitor_path_example.html"


# ============================================================
# ABIFUNKTSIOON
# ============================================================

def image_to_data_uri(path: Path) -> str:
    suffix = path.suffix.lower().replace(".", "")

    if suffix == "jpg":
        suffix = "jpeg"

    with path.open("rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")

    return f"data:image/{suffix};base64,{encoded}"


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
    # 1. SESSIOONID
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    sessions = pd.read_csv(
        SESSIONS_FILE,
        dtype={
            "session_id": "string",
            "visitor_id": "string",
        },
    )

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 2. VALIME NÄIDISSESSIOONI
    # --------------------------------------------------------

    candidates = sessions[
        (sessions["year"] == 2026)
        &
        (sessions["unique_t_codes"] >= 20)
        &
        (sessions["coordinate_pct"] >= 80)
        &
        (sessions["duration_minutes"] >= 30)
        &
        (sessions["duration_minutes"] <= 180)
    ].copy()

    if len(candidates) == 0:

        candidates = sessions[
            (sessions["unique_t_codes"] >= 10)
            &
            (sessions["coordinate_pct"] >= 70)
        ].copy()

    if len(candidates) == 0:
        raise ValueError(
            "Ei leidnud sobivat koordinaatidega sessiooni."
        )

    candidates["distance_from_median"] = (
        candidates["duration_minutes"]
        -
        candidates["duration_minutes"].median()
    ).abs()

    selected = (
        candidates
        .sort_values("distance_from_median")
        .iloc[0]
    )

    session_id = selected["session_id"]

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 3. LOEME SELLE SESSIOONI SÜNDMUSED
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    chunks = []

    for chunk in pd.read_csv(
        EVENTS_FILE,
        chunksize=200_000,
        low_memory=False,
        dtype={
            "session_id": "string",
            "visitor_id": "string",
            "t_code": "string",
            "topic": "string",
            "action_code": "string",
            "action_type": "string",
        },
    ):

        found = chunk[
            chunk["session_id"] == session_id
        ]

        if len(found) > 0:
            chunks.append(found)

    if not chunks:
        raise ValueError(
            f"Sessiooni {session_id} sündmusi ei leitud."
        )

    path = pd.concat(
        chunks,
        ignore_index=True,
    )

    path["timestamp"] = pd.to_datetime(
        path["timestamp"],
        errors="coerce",
    )

    path = (
        path
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 4. KOORDINAADID
    # --------------------------------------------------------

    path["x"] = pd.to_numeric(
        path["x"],
        errors="coerce",
    )

    path["y"] = pd.to_numeric(
        path["y"],
        errors="coerce",
    )

    mapped = path[
        path["x"].notna()
        &
        path["y"].notna()
    ].copy()

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 5. KAARDIPILT
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    image = Image.open(
        MAP_FILE
    )

    image_width, image_height = image.size

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 6. KOORDINAADID JÄÄVAD MUUTMATA
    # --------------------------------------------------------

    # Kontrollpilt näitas, et Device_id.xlsx x/y väärtused
    # vastavad juba museum_map.png pikslikoordinaatidele:
    #
    # (0,0) = üleval vasakul
    # x kasvab paremale
    # y kasvab allapoole

    mapped["x_plot"] = mapped["x"]
    mapped["y_plot"] = mapped["y"]

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    # --------------------------------------------------------
    # 7. JÄRJESTIKUSTE SAMA ASUKOHA SÜNDMUSTE KOONDAMINE
    # --------------------------------------------------------

    # Kui külastaja teeb samas punktis järjest mitu tegevust,
    # jätame trajektoorile ühe punkti.
    #
    # Algandmetes jäävad kõik sündmused alles.

    mapped["location_key"] = (
        mapped["x_plot"].round(2).astype(str)
        +
        "_"
        +
        mapped["y_plot"].round(2).astype(str)
    )

    mapped["previous_location_key"] = (
        mapped["location_key"]
        .shift(1)
    )

    route = mapped[
        mapped["location_key"]
        !=
        mapped["previous_location_key"]
    ].copy()

    route = (
        route
        .reset_index(drop=True)
    )

    route["path_step"] = (
        route.index + 1
    )

    None  # Console output removed for public staging.

    if len(route) < 2:
        raise ValueError(
            "Sessioonis pole piisavalt eri asukohti."
        )

    # --------------------------------------------------------
    # 8. HOVER-INFO
    # --------------------------------------------------------

    route["time_label"] = (
        route["timestamp"]
        .dt.strftime("%H:%M:%S")
    )

    route["topic_display"] = (
        route["topic"]
        .fillna("Teema puudub")
    )

    route["t_code_display"] = (
        route["t_code"]
        .fillna("T-kood puudub")
    )

    route["action_display"] = (
        route["action_code"]
        .map(
            {
                "0": "0 – tekstikasti tegevus",
                "1": '1 – "Võta muuseum kaasa"',
            }
        )
        .fillna("Tegevus teadmata")
    )

    hover_text = []

    for _, row in route.iterrows():

        hover_text.append(
            f"<b>{row['path_step']}. "
            f"{row['t_code_display']}</b>"
            f"<br>{row['topic_display']}"
            f"<br>Kell: {row['time_label']}"
            f"<br>{row['action_display']}"
        )

    # --------------------------------------------------------
    # 9. TAUSTAPILT
    # --------------------------------------------------------

    image_uri = image_to_data_uri(
        MAP_FILE
    )

    # --------------------------------------------------------
    # 10. JOONIS
    # --------------------------------------------------------

    None  # Console output removed for public staging.

    fig = go.Figure()

    # --------------------------------------------------------
    # JÄRJESTUST NÄITAV JOON
    # --------------------------------------------------------

    fig.add_trace(
        go.Scatter(
            x=route["x_plot"],
            y=route["y_plot"],
            mode="lines",
            name="Külastusjärjestus",
            hoverinfo="skip",
            line=dict(
                width=3,
            ),
        )
    )

    # --------------------------------------------------------
    # KÜLASTATUD PUNKTID
    # --------------------------------------------------------

    fig.add_trace(
        go.Scatter(
            x=route["x_plot"],
            y=route["y_plot"],
            mode="markers+text",
            name="Külastatud eksponaadid",
            text=route["path_step"],
            textposition="top center",
            hovertext=hover_text,
            hoverinfo="text",
            marker=dict(
                size=10,
                line=dict(
                    width=1,
                ),
            ),
        )
    )

    # --------------------------------------------------------
    # ALGUS
    # --------------------------------------------------------

    first = route.iloc[0]

    fig.add_trace(
        go.Scatter(
            x=[first["x_plot"]],
            y=[first["y_plot"]],
            mode="markers",
            name="Algus",
            marker=dict(
                size=19,
                symbol="circle-open",
                line=dict(
                    width=4,
                ),
            ),
            hovertext=[
                "ALGUS"
                f"<br>{first['t_code_display']}"
                f"<br>{first['time_label']}"
            ],
            hoverinfo="text",
        )
    )

    # --------------------------------------------------------
    # LÕPP
    # --------------------------------------------------------

    last = route.iloc[-1]

    fig.add_trace(
        go.Scatter(
            x=[last["x_plot"]],
            y=[last["y_plot"]],
            mode="markers",
            name="Lõpp",
            marker=dict(
                size=19,
                symbol="x",
                line=dict(
                    width=4,
                ),
            ),
            hovertext=[
                "LÕPP"
                f"<br>{last['t_code_display']}"
                f"<br>{last['time_label']}"
            ],
            hoverinfo="text",
        )
    )

    # --------------------------------------------------------
    # 11. TAUSTAKAART
    # --------------------------------------------------------

    # PNG koordinaadisüsteem:
    #
    # 0,0 üleval vasakul.
    #
    # Pildi ülemine vasak nurk ankurdame y=0 juurde
    # ning y-telje pöörame allpool ümber.

    fig.add_layout_image(
        dict(
            source=image_uri,

            xref="x",
            yref="y",

            x=0,
            y=0,

            xanchor="left",
            yanchor="top",

            sizex=image_width,
            sizey=image_height,

            sizing="stretch",

            opacity=1,

            layer="below",
        )
    )

    # --------------------------------------------------------
    # 12. TELJED
    # --------------------------------------------------------

    fig.update_xaxes(
        range=[
            0,
            image_width,
        ],
        visible=False,
        fixedrange=False,
    )

    # PNG Y kasvab allapoole.
    #
    # Plotlys teeme seetõttu pööratud y-telje:
    #
    # 0 on üleval
    # image_height on all.

    fig.update_yaxes(
        range=[
            image_height,
            0,
        ],
        visible=False,
        scaleanchor="x",
        scaleratio=1,
        fixedrange=False,
    )

    # --------------------------------------------------------
    # 13. KUJUNDUS
    # --------------------------------------------------------

    fig.update_layout(
        title=(
            "Külastaja eksponaatide külastusjärjestus – "
            + str(selected["visit_date"])
            + "<br>"
            + "<sup>"
            + str(int(selected["event_count"]))
            + " sündmust, "
            + str(int(selected["unique_t_codes"]))
            + " T-koodi, "
            + f"{selected['duration_minutes']:.0f} min"
            + "</sup>"
        ),

        width=1500,
        height=900,

        margin=dict(
            l=0,
            r=0,
            t=75,
            b=0,
        ),

        hovermode="closest",

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1,
        ),

        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    # --------------------------------------------------------
    # 14. SALVESTAMINE
    # --------------------------------------------------------

    fig.write_html(
        OUTPUT_FILE,
        include_plotlyjs=True,
        full_html=True,
    )

    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.
    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.

    None  # Console output removed for public staging.


if __name__ == "__main__":
    main()