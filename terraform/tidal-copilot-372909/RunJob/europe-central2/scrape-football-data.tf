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
        image = "gcr.io/tidal-copilot-372909/test_cloud_run@sha256:bbb92d49de99467b1146e96103cd0739d839c2c89056635315fa4026bc112e82"
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
