resource "google_project_service" "storage_api_googleapis_com" {
  project = "733094419233"
  service = "storage-api.googleapis.com"
}
# terraform import google_project_service.storage_api_googleapis_com 733094419233/storage-api.googleapis.com
