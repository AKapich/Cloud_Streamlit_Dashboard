resource "google_project_service" "logging_googleapis_com" {
  project = "733094419233"
  service = "logging.googleapis.com"
}
# terraform import google_project_service.logging_googleapis_com 733094419233/logging.googleapis.com
