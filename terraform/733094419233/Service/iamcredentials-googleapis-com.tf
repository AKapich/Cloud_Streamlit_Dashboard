resource "google_project_service" "iamcredentials_googleapis_com" {
  project = "733094419233"
  service = "iamcredentials.googleapis.com"
}
# terraform import google_project_service.iamcredentials_googleapis_com 733094419233/iamcredentials.googleapis.com
