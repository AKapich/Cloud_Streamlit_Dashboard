resource "google_project_service" "storage_googleapis_com" {
  project = "733094419233"
  service = "storage.googleapis.com"
}
# terraform import google_project_service.storage_googleapis_com 733094419233/storage.googleapis.com
