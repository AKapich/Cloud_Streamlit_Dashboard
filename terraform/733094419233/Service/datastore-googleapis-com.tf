resource "google_project_service" "datastore_googleapis_com" {
  project = "733094419233"
  service = "datastore.googleapis.com"
}
# terraform import google_project_service.datastore_googleapis_com 733094419233/datastore.googleapis.com
