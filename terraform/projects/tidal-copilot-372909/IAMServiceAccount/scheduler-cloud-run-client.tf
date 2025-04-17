resource "google_service_account" "scheduler_cloud_run_client" {
  account_id   = "scheduler-cloud-run-client"
  display_name = "scheduler-cloud-run-client"
  project      = "tidal-copilot-372909"
}
# terraform import google_service_account.scheduler_cloud_run_client projects/tidal-copilot-372909/serviceAccounts/scheduler-cloud-run-client@tidal-copilot-372909.iam.gserviceaccount.com
