# Public staging review

Prepared 2026-10-30. Unpublished code-and-documentation staging copy; no data execution, repository creation, commit, push, HUMAL submission or publication performed.

## Scope and adaptation

Includes the existing R pipeline, all 17 current non-backup Python analysis/preparation scripts, Dash application and both coordinate-entry HTML source tools. No raw logs, museum spreadsheets, maps, coordinate lists, session records, Parquet, generated route exports, private HUMAL/RO-Crate metadata, Publisher state, credentials, backups or existing Git history were copied. The map-clicker README was rewritten as WORKFLOW.md instructions; its original private working-directory instructions were not copied.

Python project-relative data roots now resolve through workflow_config.py to a required external workspace. Private identifier examples were replaced with explicitly synthetic labels; historical dated/context workbook names became generic interface filenames. Inventory sheet is configurable (Python default devices; actual authorised sheet must be supplied explicitly). Private map dimensions were removed from the dashboard fallback and legacy clicker; the latter requires width/height URL parameters. All 549 original Python print calls and their argument evaluation were removed, including individual-record previews, identifiers and exception printing. Browser clicker console diagnostics were removed. Computation and restricted diagnostic file generation remain; there is no verbose-record switch. The Python configuration rejects source overlap, repository markers and symlinked top-level data directories. R configuration additionally rejects repository markers to guard against accidentally using the original project as an output workspace.

requirements.txt retains the private source's declared dependency versions and adds matplotlib, used by the coordinate diagnostic. It is not a lockfile and no runtime/package compatibility is claimed. Both ignore files were reviewed: Git uses an exact source-file allowlist; HUMAL exclusions cover data, generated outputs, maps, metadata, credentials, backups and environments while permitting the reviewed map-processing source files. Neither ignore file enforces access control or prevents manual publication.

## Software licensing

The included original source code is licensed under the [MIT License](LICENSE). Copyright (c) 2026 Kata Maria Metsar. The author has confirmed authority to release this original source code under MIT.

The MIT License does **not** cover ERM visitor logs, museum datasets, maps, device inventories, or other third-party materials. No rights to those materials are granted by this release; they require separate permission or applicable licences. Third-party software dependencies retain their own licences.

Licensing was finalized on 2026-10-30 with the author's explicit authorization. This does not authorize repository creation, commit, push, HUMAL submission or publication.

## Complete staged inventory

Exactly 36 regular files, listed below. No symlinks or .git directory. Only reviewed code and documentation are present.

- `.gitignore` — exact public file allowlist
- `.humalignore` — private/generated file exclusions
- `R/00_pipeline.R` — R pipeline entry point
- `R/01_parse_logs.R` — earlier log parser
- `R/02_join_devices.R` — inventory join
- `R/03_make_paths.R` — inferred transitions with one-hour threshold
- `R/04_usage_summary.R` — interaction and distinct-card summaries
- `R/05_plot_daily_usage.R` — coverage-aware plotting and summary
- `R/config.R` — external R workspace and inventory-sheet configuration
- `LICENSE` — standard MIT License, copyright 2026 Kata Maria Metsar
- `README.md` — purpose, setup, restrictions, software licensing, R workflow and Python overview
- `RELEASE_REVIEW.md` — this inventory, changes, validation and residual risks
- `WORKFLOW.md` — complete Python execution graph, schemas, outputs, map tools and method differences
- `app.py` — Dash analysis application; requires separately supplied authorised inputs
- `requirements.txt` — declared Python dependencies, not validated lockfile
- `scripts/01_import_logs.py` — reviewed and adapted Python stage; prerequisites and outputs documented in WORKFLOW.md
- `scripts/02_understand_log_fields.py` — reviewed and adapted Python stage; prerequisites and outputs documented in WORKFLOW.md
- `scripts/03_map_exhibits.py` — reviewed and adapted Python stage; prerequisites and outputs documented in WORKFLOW.md
- `scripts/04_make_daily_sessions.py` — reviewed and adapted Python stage; prerequisites and outputs documented in WORKFLOW.md
- `scripts/05_check_language_link.py` — reviewed and adapted Python stage; prerequisites and outputs documented in WORKFLOW.md
- `scripts/06_make_final_sessions.py` — reviewed and adapted Python stage; prerequisites and outputs documented in WORKFLOW.md
- `scripts/07_plot_visitor_path.py` — reviewed and adapted Python stage; prerequisites and outputs documented in WORKFLOW.md
- `scripts/07a_check_coordinates.py` — reviewed and adapted Python stage; prerequisites and outputs documented in WORKFLOW.md
- `scripts/07b_debug_route.py` — reviewed and adapted Python stage; prerequisites and outputs documented in WORKFLOW.md
- `scripts/07c_fix_coordinates.py` — reviewed and adapted Python stage; prerequisites and outputs documented in WORKFLOW.md
- `scripts/08_add_language_and_context.py` — reviewed and adapted Python stage; prerequisites and outputs documented in WORKFLOW.md
- `scripts/09_prepare_dashboard_data.py` — reviewed and adapted Python stage; prerequisites and outputs documented in WORKFLOW.md
- `scripts/10_prepare_context_data.py` — reviewed and adapted Python stage; prerequisites and outputs documented in WORKFLOW.md
- `scripts/11_prepare_ticket_sales.py` — reviewed and adapted Python stage; prerequisites and outputs documented in WORKFLOW.md
- `scripts/12_prepare_school_holidays.py` — reviewed and adapted Python stage; prerequisites and outputs documented in WORKFLOW.md
- `scripts/13_prepare_action_data.py` — reviewed and adapted Python stage; prerequisites and outputs documented in WORKFLOW.md
- `scripts/14_prepare_data_coverage.py` — reviewed and adapted Python stage; prerequisites and outputs documented in WORKFLOW.md
- `scripts/_public_config.py` — direct-script import helper
- `visitor_map_clicker_v2/map_clicker.html` — legacy Leaflet coordinate-entry source, no map or codes
- `visitor_map_clicker_v2/map_clicker_v3.html` — natural-image-pixel coordinate-entry source, no map or codes
- `workflow_config.py` — external Python workspace and inventory-sheet configuration

## Validation

The licensing-only review checked the standard MIT text and copyright, matching scope exclusions in README.md and this review, the 36-file inventory and LICENSE inclusion in the Git allowlist. A recursive text check found no outdated pending-licence statements. Only LICENSE, README.md, RELEASE_REVIEW.md and .gitignore changed; workflow sources and dependencies were unchanged. No data or workflow execution was needed for this review.

All 20 Python files passed AST parsing and in-memory compilation without imports or bytecode generation; the 18 adapted original sources contain zero print calls. Both HTML tools' inline JavaScript passed node --check without browser execution. All seven R sources passed syntax parsing without evaluation. Review covered file roots, input/output calls, imports, identifier examples, record previews, session construction, context joins and map entry code. Recursive text scans found no private home-directory paths, email addresses, long hexadecimal identifiers (16+ characters, including before underscores), MAC addresses or obvious credential assignments. The two Leaflet CDN URLs are expected public dependency references, not private endpoints. Scan results reduce risk but cannot prove absence of sensitive information.

No visitor records, workbook contents, maps, generated data or private metadata were opened for this extension. No workflow script, dashboard or browser tool was executed. No packages were installed. Dependency resolution, runtime compatibility, actual input schemas, numerical results, performance, UI/callback behavior and end-to-end execution remain unverified. The earlier staging review recorded package availability and configuration checks for the R-only release; those are not claims of validation of this extension.

Before and after source-code/dependency/coordinate-tool and private Git-file hashes, plus private git status, were compared. The original research sources and private repository remained unchanged. Existing staged R analysis sources were retained; only R/config.R gained an additional workspace guard.

## Remaining risks and author decisions

- Generated event/session CSVs, repeated-ID tables, failed raw lines, sample exports and route HTML remain row-level restricted data. Route HTML embeds an authorised map. Session dashboard Parquet retains session identifiers. Aggregation does not make other outputs automatically publishable; review small groups and linking risks.
- Console prints were removed, but library warnings, raised exceptions, server logs and browser UI can reveal input values, paths or sensitive detail. Keep execution, logs, browser storage and downloads within the authorised environment. Nested symlinks and external-workspace selection are not fully sandboxed.
- Several preparation stages run on import and overwrite outputs. Stage 08 rewrites two CSVs and may create a calendar template; 07c writes corrected coordinates under data_raw. Never point either workflow at the original private repository. Use a separate controlled data workspace and retention policy.
- The earlier device-per-day Python method, final ticket-per-day method and R card-transition method have materially different identities, timestamp contracts and session/transition rules. The 18-character ticket filter, language-prefix inference, closure assumptions and coordinate correction require validation. Coordinate provenance and the coordinates.csv versus coordinates_fixed.csv split are explicitly documented.
- No authentication or reviewed deployment is supplied. Dashboard startup requires nonempty compatible session data and corrected coordinates; optional-file handling does not guarantee every empty-data callback works. No public demo or numerical reproduction is claimed.
- Legacy clicker loads third-party Leaflet from a CDN and retains coordinates in localStorage. Both tools assume trusted simple input codes and are not hardened for arbitrary CSV/UI content. Manual map rights, coordinate checks and controlled-browser cleanup remain necessary.
- Future HUMAL metadata must describe an MIT-licensed code-and-methodology release, with separately restricted inputs and an unverified dashboard, not a public dataset or a runnable demo. Third-party material rights remain separate from the software licence.

Re-review the complete inventory after any change. Repository creation, commit, push, HUMAL submission and publication remain separate, unauthorised steps.
