resource "google_project_service" "cloudscheduler_googleapis_com" {
  project = "733094419233"
  service = "cloudscheduler.googleapis.com"
}
# terraform import google_project_service.cloudscheduler_googleapis_com 733094419233/cloudscheduler.googleapis.com
