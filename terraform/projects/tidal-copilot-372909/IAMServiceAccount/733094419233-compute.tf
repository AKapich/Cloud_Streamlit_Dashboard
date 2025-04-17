resource "google_service_account" "733094419233_compute" {
  account_id   = "733094419233-compute"
  display_name = "Default compute service account"
  project      = "tidal-copilot-372909"
}
# terraform import google_service_account.733094419233_compute projects/tidal-copilot-372909/serviceAccounts/733094419233-compute@tidal-copilot-372909.iam.gserviceaccount.com
