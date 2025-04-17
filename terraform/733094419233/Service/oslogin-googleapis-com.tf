resource "google_project_service" "oslogin_googleapis_com" {
  project = "733094419233"
  service = "oslogin.googleapis.com"
}
# terraform import google_project_service.oslogin_googleapis_com 733094419233/oslogin.googleapis.com
