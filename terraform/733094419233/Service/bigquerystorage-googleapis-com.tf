resource "google_project_service" "bigquerystorage_googleapis_com" {
  project = "733094419233"
  service = "bigquerystorage.googleapis.com"
}
# terraform import google_project_service.bigquerystorage_googleapis_com 733094419233/bigquerystorage.googleapis.com
