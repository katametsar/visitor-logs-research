if (!exists("project_path", mode = "function")) source("R/config.R")
library(tidyverse)

log_files <- list.files(
  project_path("data_raw/Logide_failid"),
  pattern = "\\.log$",
  full.names = TRUE
)

all_logs <- map_dfr(log_files, function(f) {
  lines <- readLines(f)

  tibble(
    source_file = basename(f),
    raw = lines
  )
})

print(paste("Leitud logifaile:", length(log_files)))
print(paste("Kokku logiridu:", nrow(all_logs)))


parsed_logs <- all_logs %>%
  extract(
    raw,
    into = c("time_raw", "device_id", "channel", "card_hex", "object_hex"),
    regex = "\\[(.*?)\\] ([^/]+)/([^:]+): ([0-9A-Fa-f]+) ([0-9A-Fa-f]+)",
    remove = FALSE
  )


print("Mitu rida jäi parsida:")
print(sum(is.na(parsed_logs$time_raw)))

dir.create(project_path("data_clean"), recursive = TRUE, showWarnings = FALSE)

write_csv(
  parsed_logs,
  project_path("data_clean/parsed_logs.csv")
)

message("Output written to the configured restricted workspace.")
