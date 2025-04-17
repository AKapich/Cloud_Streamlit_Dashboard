# scraper

resource "google_cloud_run_v2_job" "scrape_football_data" {
  client       = "cloud-console"
  launch_stage = "GA"
  location     = var.region
  name         = "scrape-football-data"
  project      = var.project_id

  template {
    task_count = 1

    template {
      containers {
        image = "gcr.io/tidal-copilot-372909/test_run_job@sha256:323cad260acde7d8062bbf9d1427d91f3983eddc44aa3f354422c39782848f7e"
        name  = "test-cloud-run-1"

        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
      }

      execution_environment = "EXECUTION_ENVIRONMENT_GEN2"
      max_retries           = 3
      service_account       = "733094419233-compute@developer.gserviceaccount.com"
      timeout               = "600s"
    }
  }
}
# terraform import google_cloud_run_v2_job.scrape_football_data projects/tidal-copilot-372909/locations/europe-central2/jobs/scrape-football-data

resource "google_cloud_scheduler_job" "scrape_football_data" {
  name        = "scrape-football-data-scheduler-trigger"
  region      = var.region
  schedule    = "0 9 * * 1"
  time_zone   = "Etc/UTC"
  attempt_deadline = "180s"

  retry_config {
    max_backoff_duration = "3600s"
    max_doublings        = 5
    max_retry_duration   = "0s"
    min_backoff_duration = "5s"
  }

  http_target {
    uri         = "https://europe-central2-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/tidal-copilot-372909/jobs/scrape-football-data:run"
    http_method = "POST"

    headers = {
      "User-Agent" = "Google-Cloud-Scheduler"
    }

    oauth_token {
      service_account_email = "scheduler-cloud-run-client@tidal-copilot-372909.iam.gserviceaccount.com"
      scope                 = "https://www.googleapis.com/auth/cloud-platform"
    }
  }
}
# terraform import google_cloud_scheduler_job.scrape_football_data projects/tidal-copilot-372909/locations/europe-central2/jobs/scrape-football-data-scheduler-trigger

resource "google_service_account" "scheduler_cloud_run_client" {
  account_id   = "scheduler-cloud-run-client"
  display_name = "scheduler-cloud-run-client"
  project      = var.project_id
}
# terraform import google_service_account.scheduler_cloud_run_client projects/tidal-copilot-372909/serviceAccounts/scheduler-cloud-run-client@tidal-copilot-372909.iam.gserviceaccount.com

resource "google_project_iam_member" "scheduler_cloud_run_jobs_executor" {
  project = var.project_id
  role    = "roles/run.jobsExecutor"
  member  = "serviceAccount:scheduler-cloud-run-client@tidal-copilot-372909.iam.gserviceaccount.com"
}

# streamlit app

resource "google_cloud_run_v2_service" "streamlit" {
  client         = "gcloud"
  client_version = "518.0.0"
  ingress        = "INGRESS_TRAFFIC_ALL"
  launch_stage   = "GA"
  location       = var.region
  name           = "streamlit"
  project        = var.project_id

  template {
    containers {
      image = "gcr.io/tidal-copilot-372909/streamlit"

      ports {
        container_port = 8501
        name           = "http1"
      }

      resources {
        cpu_idle = true

        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }

        startup_cpu_boost = true
      }

      startup_probe {
        failure_threshold     = 1
        initial_delay_seconds = 0
        period_seconds        = 240

        tcp_socket {
          port = 8501
        }

        timeout_seconds = 240
      }

      volume_mounts {
        mount_path = "/cloudsql"
        name       = "cloudsql"
      }
    }

    max_instance_request_concurrency = 80

    scaling {
      max_instance_count = 100
    }

    service_account = "733094419233-compute@developer.gserviceaccount.com"
    timeout         = "300s"

    volumes {
      cloud_sql_instance {
        instances = ["tidal-copilot-372909:europe-central2:football-db"]
      }

      name = "cloudsql"
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}
# terraform import google_cloud_run_v2_service.streamlit projects/tidal-copilot-372909/locations/europe-central2/services/streamlit


# database

resource "google_sql_database_instance" "football_db" {
  database_version    = "POSTGRES_16"
  instance_type       = "CLOUD_SQL_INSTANCE"
  maintenance_version = "POSTGRES_16_8.R20250302.00_04"
  name                = "football-db"
  project             = var.project_id
  region              = var.region

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
      query_string_length = 256
    }

    ip_configuration {
      # block removed not to push secret info to github

      ipv4_enabled = true
    }

    location_preference {
      zone = "europe-central2-c"
    }

    maintenance_window {
      day          = 1
      hour         = 3
      update_track = "canary"
    }

    pricing_plan = "PER_USE"
    tier         = "db-g1-small"
  }
}
# terraform import google_sql_database_instance.football_db projects/tidal-copilot-372909/instances/football-db

resource "google_sql_user" "postgres_user" {
  name     = "postgres"
  instance = "football-db"
}

# load balancer

resource "google_compute_region_backend_service" "streamlit" {
  connection_draining_timeout_sec = 0
  load_balancing_scheme           = "EXTERNAL_MANAGED"
  name                            = "streamlit"
  port_name                       = "http"
  project                         = var.project_id
  protocol                        = "HTTPS"
  region                          = var.region
  session_affinity                = "NONE"
  timeout_sec                     = 30
  backend {
    balancing_mode                  = "UTILIZATION"
    capacity_scaler                 = 1
    failover                        = false
    group                           = "https://www.googleapis.com/compute/v1/projects/tidal-copilot-372909/regions/europe-central2/networkEndpointGroups/streamlit"
    max_connections                 = 0
    max_connections_per_endpoint    = 0
    max_connections_per_instance    = 0
    max_rate                        = 0
    max_rate_per_endpoint           = 0
    max_rate_per_instance           = 0
    max_utilization                 = 0
  }
  
}
# terraform import google_compute_region_backend_service.streamlit projects/tidal-copilot-372909/regions/europe-central2/backendServices/streamlit

resource "google_compute_forwarding_rule" "load_balancer1_forwarding_rule" {
  ip_address            = "34.0.245.131"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  name                  = "load-balancer1-forwarding-rule"
  network               = "https://www.googleapis.com/compute/v1/projects/tidal-copilot-372909/global/networks/default"
  network_tier          = "STANDARD"
  port_range            = "80-80"
  project               = var.project_id
  region                = var.region
  target                = "https://www.googleapis.com/compute/beta/projects/tidal-copilot-372909/regions/europe-central2/targetHttpProxies/load-balancer1-target-proxy"
}
# terraform import google_compute_forwarding_rule.load_balancer1_forwarding_rule projects/tidal-copilot-372909/regions/europe-central2/forwardingRules/load-balancer1-forwarding-rule

resource "google_compute_subnetwork" "proxy_subnet1" {
  ip_cidr_range              = "10.0.0.0/24"
  name                       = "proxy-subnet1"
  network                    = "https://www.googleapis.com/compute/v1/projects/tidal-copilot-372909/global/networks/default"
  private_ipv6_google_access = "DISABLE_GOOGLE_ACCESS"
  project                    = var.project_id
  purpose                    = "REGIONAL_MANAGED_PROXY"
  region                     = var.region
  role                       = "ACTIVE"
}
# terraform import google_compute_subnetwork.proxy_subnet1 projects/tidal-copilot-372909/regions/europe-central2/subnetworks/proxy-subnet1

resource "google_compute_region_url_map" "load_balancer1" {
  default_service = "https://www.googleapis.com/compute/v1/projects/tidal-copilot-372909/regions/europe-central2/backendServices/streamlit"
  name            = "load-balancer1"
  project         = var.project_id
  region          = var.region
}
# terraform import google_compute_region_url_map.load_balancer1 projects/tidal-copilot-372909/regions/europe-central2/urlMaps/load-balancer1

resource "google_compute_region_target_http_proxy" "load_balancer1_target_proxy" {
  name    = "load-balancer1-target-proxy"
  project = var.project_id
  region  = var.region
  url_map = "https://www.googleapis.com/compute/v1/projects/tidal-copilot-372909/regions/europe-central2/urlMaps/load-balancer1"
}
# terraform import google_compute_region_target_http_proxy.load_balancer1_target_proxy projects/tidal-copilot-372909/regions/europe-central2/targetHttpProxies/load-balancer1-target-proxy



