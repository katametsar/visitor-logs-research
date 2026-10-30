# Code stays separate from restricted inputs and generated outputs.
code_root <- normalizePath(getwd(), mustWork = TRUE)
data_root <- Sys.getenv("VISITOR_LOGS_WORKSPACE", unset = "")
if (!nzchar(data_root)) {
  stop("Set VISITOR_LOGS_WORKSPACE to an existing restricted workspace outside this release.")
}
data_root <- normalizePath(path.expand(data_root), mustWork = TRUE)
if (data_root == code_root || startsWith(data_root, paste0(code_root, "/"))) {
  stop("The restricted workspace must be outside the public release directory.")
}
if (file.exists(file.path(data_root, ".git")) ||
    file.exists(file.path(data_root, "app.py")) ||
    file.exists(file.path(data_root, "R", "00_pipeline.R"))) {
  stop("Use a separate data workspace, never the original research repository.")
}
project_path <- function(relative) file.path(data_root, relative)
device_sheet <- Sys.getenv("VISITOR_LOGS_DEVICE_SHEET", unset = "devices")
