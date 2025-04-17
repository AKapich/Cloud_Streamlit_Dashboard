resource "google_cloud_run_v2_job" "scrape_football_data" {
  client       = "cloud-console"
  launch_stage = "GA"
  location     = "europe-central2"
  name         = "scrape-football-data"
  project      = "tidal-copilot-372909"

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
