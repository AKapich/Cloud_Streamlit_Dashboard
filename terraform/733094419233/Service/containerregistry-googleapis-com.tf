resource "google_project_service" "containerregistry_googleapis_com" {
  project = "733094419233"
  service = "containerregistry.googleapis.com"
}
# terraform import google_project_service.containerregistry_googleapis_com 733094419233/containerregistry.googleapis.com
