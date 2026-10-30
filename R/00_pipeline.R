# Run from the public release root: Rscript R/00_pipeline.R
source("R/config.R")
source(file.path(code_root, "R/01_parse_logs.R"))
source(file.path(code_root, "R/02_join_devices.R"))
source(file.path(code_root, "R/03_make_paths.R"))
source(file.path(code_root, "R/04_usage_summary.R"))
source(file.path(code_root, "R/05_plot_daily_usage.R"))
message("Processing complete. Outputs remain restricted.")
