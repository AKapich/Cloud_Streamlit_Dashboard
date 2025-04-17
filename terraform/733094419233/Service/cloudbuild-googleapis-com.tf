resource "google_project_service" "cloudbuild_googleapis_com" {
  project = "733094419233"
  service = "cloudbuild.googleapis.com"
}
# terraform import google_project_service.cloudbuild_googleapis_com 733094419233/cloudbuild.googleapis.com
