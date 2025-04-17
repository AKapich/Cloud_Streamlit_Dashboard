resource "google_storage_bucket" "tidal_copilot_372909_cloudbuild" {
  force_destroy            = false
  location                 = "US"
  name                     = "tidal-copilot-372909_cloudbuild"
  project                  = "tidal-copilot-372909"
  public_access_prevention = "inherited"
  storage_class            = "STANDARD"
}
# terraform import google_storage_bucket.tidal_copilot_372909_cloudbuild tidal-copilot-372909_cloudbuild
