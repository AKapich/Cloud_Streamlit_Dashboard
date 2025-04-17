resource "google_sql_database_instance" "football_db" {
  database_version    = "POSTGRES_16"
  instance_type       = "CLOUD_SQL_INSTANCE"
  maintenance_version = "POSTGRES_16_8.R20250302.00_04"
  name                = "football-db"
  project             = "tidal-copilot-372909"
  region              = "europe-central2"

  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"

    backup_configuration {
      backup_retention_settings {
        retained_backups = 7
        retention_unit   = "COUNT"
      }

      enabled                        = true
      location                       = "eu"
      start_time                     = "00:00"
      transaction_log_retention_days = 7
    }

    connector_enforcement       = "NOT_REQUIRED"
    deletion_protection_enabled = true
    disk_autoresize             = true
    disk_autoresize_limit       = 0
    disk_size                   = 10
    disk_type                   = "PD_SSD"
    edition                     = "ENTERPRISE"

    insights_config {
      query_string_length = 0
    }

    ip_configuration {
      authorized_networks {
        name  = "aleks"
        value = "83.5.242.158/32"
      }

      authorized_networks {
        name  = "alicja"
        value = "84.40.220.36/32"
      }

      authorized_networks {
        name  = "mati"
        value = "194.29.137.21/32"
      }

      authorized_networks {
        name  = "streamlit app"
        value = "216.239.0.0/16"
      }

      ipv4_enabled = true
    }

    location_preference {
      zone = "europe-central2-c"
    }

    maintenance_window {
      update_track = "canary"
    }

    pricing_plan = "PER_USE"
    tier         = "db-g1-small"
  }
}
# terraform import google_sql_database_instance.football_db projects/tidal-copilot-372909/instances/football-db
