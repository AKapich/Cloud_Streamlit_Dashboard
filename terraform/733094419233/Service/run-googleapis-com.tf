resource "google_project_service" "run_googleapis_com" {
  project = "733094419233"
  service = "run.googleapis.com"
}
# terraform import google_project_service.run_googleapis_com 733094419233/run.googleapis.com
