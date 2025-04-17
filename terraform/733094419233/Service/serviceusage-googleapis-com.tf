resource "google_project_service" "serviceusage_googleapis_com" {
  project = "733094419233"
  service = "serviceusage.googleapis.com"
}
# terraform import google_project_service.serviceusage_googleapis_com 733094419233/serviceusage.googleapis.com
