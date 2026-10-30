# Visitor interaction log research workflow

This code-only release describes an exploratory workflow for transforming exhibition interaction logs into usage summaries and approximate transitions between exhibition points. No visitor data, museum maps, device inventory, results, private metadata or Git history are included. Dash source is included; a runnable public demo is outside this release's scope.

## Included code and method

The six numbered scripts in `R/` are adapted from the project's earlier R analysis pipeline; `config.R` is new public-release configuration. Run the numbered stages through `00_pipeline.R`:

1. `01_parse_logs.R`: read log files and extract time, device, channel, card and object fields. Report counts and failed timestamp extractions without previewing records.
2. `02_join_devices.R`: left-join a separately supplied device inventory to assign exhibition points and topics; report join counts.
3. `03_make_paths.R`: parse day-month-year timestamps, order events by card identifier and time, remove consecutive repeated points, and retain transitions with a positive gap below 3,600 seconds.
4. `04_usage_summary.R`: count events by exhibition point, date, hour and weekday, and distinct card identifiers by date.
5. `05_plot_daily_usage.R`: complete the date calendar, preserve missing days as NA rather than zero, plot observed usage and discontinuous series, and calculate coverage.

## Restricted inputs and local use

This is source for methodological inspection, not a self-contained analysis or a validated reproduction. No data are downloaded or generated. Use only separately authorised inputs in an access-controlled workspace outside this public directory. Generated files, including parsed raw lines and card-linked paths, remain restricted. Never upload them with this release.

Requires R with `tidyverse`, `readxl` and `lubridate`. Dependency versions are not locked and full execution has not been validated on restricted inputs. From this release's root, set `VISITOR_LOGS_WORKSPACE` to the existing restricted workspace, then run `Rscript R/00_pipeline.R`. `VISITOR_LOGS_DEVICE_SHEET` selects the workbook sheet (default `devices`). Individual stages can also be run from the release root. The configuration fails when the workspace is unset or inside this release.

The external workspace must contain:

- `data_raw/Logide_failid/*.log`: line-oriented logs matching the regular expression in `01_parse_logs.R`. The parser expects a bracketed timestamp, `device/channel:`, then two hexadecimal fields. The R timestamp conversion expects day-month-year time values; other timestamp formats, timezone offsets and daylight-saving transitions require adaptation and validation.
- `data_raw/Device_id.xlsx`: a device inventory with columns `Name`, `Device`, `Topic`, `Regrouping of "names", vol 1` and `Regrouping of "names", vol 2`, on the configured sheet. Column names describe the input schema, not permission to share an inventory.

`data_clean/` and `outputs/` are created in that workspace. No example dataset is supplied. If discussing field values, use labels such as `SYNTHETIC_CARD_A`, `SYNTHETIC_DEVICE_A` and `SYNTHETIC_POINT_A`; these are explanatory labels, not parser-ready records.

## Interpretation and limitations

A card identifier is a pseudonymous system key, not proof of an individual person's identity. Reuse, sharing, missing events and maintenance activity can affect counts. Distinct cards are not validated visitor counts. Logs record interactions, not continuous movement, attention, learning, dwell time or the full visitor experience.

Transitions infer ordering between recorded points; they do not reconstruct physical routes. The one-hour threshold is a heuristic. This R workflow does not implement the private Python session logic or contextual joins. Device inventory uniqueness, timestamp parsing, unmatched rows and suitable session boundaries must be checked before drawing conclusions. Missing log days indicate missing observations, not a closed museum or zero activity. Coverage is calculated over the observed minimum-to-maximum date range, not an independently verified collection calendar. Small samples, empty inputs and malformed records require additional handling. Loess smoothing is exploratory.

## Access, rights and release status

Obtain the data controller's approval and appropriate agreements before processing restricted logs, device inventories or derived records. Limit access and retention; do not attempt identification or linkage for identification. Aggregate outputs can still reveal small groups and require disclosure review before sharing. Ignore files are guardrails, not anonymisation or access controls.

The included original source code is licensed under the [MIT License](LICENSE). Copyright (c) 2026 Kata Maria Metsar. The author has confirmed authority to release this original source code under MIT.

The MIT License does **not** cover ERM visitor logs, museum datasets, maps, device inventories, or other third-party materials. No rights to those materials are granted by this release; they require separate permission or applicable licences. Third-party software dependencies retain their own licences.

See `RELEASE_REVIEW.md` for the complete staged inventory, review findings and remaining decisions. No repository has been created and no commit, push, HUMAL submission or publication is authorised by this staging step.

## Extended Python and dashboard release

The public staging scope now also includes all 17 non-backup Python analysis/preparation scripts, the Dash source, shared public configuration, Python dependencies and both coordinate-entry HTML sources. No maps, coordinate lists, datasets, generated results, private metadata or Git history are included.

See [WORKFLOW.md](WORKFLOW.md) for the complete execution graph, stage outputs, input schemas, coordinate conventions and methodological differences. The Python final dashboard branch uses 18-character card identifiers grouped by local day; the older Python device-per-day branch and R card transitions represent different methods and should not be compared as identical visitor counts.

Use Python 3.10 or later (source syntax requirement). `requirements.txt` preserves the source project's stated Dash, Plotly, pandas and NumPy versions and unpinned dependencies, adding matplotlib for the coordinate diagnostic. These are declared dependencies, not a resolved or verified environment. Pillow handles maps, openpyxl spreadsheets, pyarrow Parquet, Plotly interactive figures and Dash the application; gunicorn is an inherited optional deployment dependency. No package installation or runtime compatibility validation was performed. R dependencies remain as described above.

In a separately managed Python environment, install with `python3 -m pip install -r requirements.txt`. Set `VISITOR_LOGS_WORKSPACE` to an existing, access-controlled data workspace **separate from both repositories**, then run the selected stages from this source directory. For example:

```sh
export VISITOR_LOGS_WORKSPACE=/absolute/path/to/authorised-workspace
export VISITOR_LOGS_PYTHON_DEVICE_SHEET=devices
python3 scripts/01_import_logs.py
```

Continue in the order documented in WORKFLOW.md. Supply authorised data independently; the release does not download any data. Python rejects an unset workspace, source-tree overlap, repository markers and symlinked top-level data directories. These checks are guardrails, not a filesystem sandbox: nested symlinks and manual copying still need access controls. Do not point configuration at the original private project. R and Python share directory conventions but write different products; use separate workspaces to avoid confusing their outputs.

Launch `python3 app.py` only after preparation. It binds to loopback on port 8050 with debug disabled. No dashboard data are bundled, so launching this copy without authorised inputs is expected to fail. Dash is not an access-control system; this release does not supply authentication or a reviewed deployment setup. The browser may receive sensitive data or maps through figures and interactions. Keep the application within the authorised environment.

All Python print calls were removed, including argument evaluation, to prevent record previews and identifiers reaching standard output through these calls. No verbose-record opt-in is provided. Diagnostic CSVs, route HTML, plots and session Parquets still contain restricted material. Library warnings, exceptions and server logging may expose values or paths; manage them as restricted logs. Several stages execute at import time; inspect source without importing it. Static validation does not establish numerical correctness, complete anonymity or suitability for publication.
