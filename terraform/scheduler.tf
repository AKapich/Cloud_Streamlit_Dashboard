resource "google_cloud_scheduler_job" "scrape_football_data" {
  name        = "scrape-football-data-scheduler-trigger"
  region      = "europe-central2"
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
