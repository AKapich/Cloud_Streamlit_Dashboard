resource "google_project_service" "sqladmin_googleapis_com" {
  project = "733094419233"
  service = "sqladmin.googleapis.com"
}
# terraform import google_project_service.sqladmin_googleapis_com 733094419233/sqladmin.googleapis.com
