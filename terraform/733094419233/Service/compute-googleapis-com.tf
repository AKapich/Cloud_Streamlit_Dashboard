resource "google_project_service" "compute_googleapis_com" {
  project = "733094419233"
  service = "compute.googleapis.com"
}
# terraform import google_project_service.compute_googleapis_com 733094419233/compute.googleapis.com
