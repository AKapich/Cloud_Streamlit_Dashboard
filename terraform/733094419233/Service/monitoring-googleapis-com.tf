resource "google_project_service" "monitoring_googleapis_com" {
  project = "733094419233"
  service = "monitoring.googleapis.com"
}
# terraform import google_project_service.monitoring_googleapis_com 733094419233/monitoring.googleapis.com
