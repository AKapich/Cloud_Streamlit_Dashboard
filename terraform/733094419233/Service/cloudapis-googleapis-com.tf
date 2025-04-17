resource "google_project_service" "cloudapis_googleapis_com" {
  project = "733094419233"
  service = "cloudapis.googleapis.com"
}
# terraform import google_project_service.cloudapis_googleapis_com 733094419233/cloudapis.googleapis.com
