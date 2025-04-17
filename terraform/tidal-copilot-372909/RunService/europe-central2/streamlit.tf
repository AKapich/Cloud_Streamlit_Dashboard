resource "google_cloud_run_v2_service" "streamlit" {
  client         = "gcloud"
  client_version = "518.0.0"
  ingress        = "INGRESS_TRAFFIC_ALL"
  launch_stage   = "GA"
  location       = "europe-central2"
  name           = "streamlit"
  project        = "tidal-copilot-372909"

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
