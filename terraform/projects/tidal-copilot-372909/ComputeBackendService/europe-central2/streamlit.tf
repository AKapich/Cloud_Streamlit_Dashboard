resource "google_compute_region_backend_service" "streamlit" {
  connection_draining_timeout_sec = 0
  load_balancing_scheme           = "EXTERNAL_MANAGED"
  name                            = "streamlit"
  port_name                       = "http"
  project                         = "tidal-copilot-372909"
  protocol                        = "HTTPS"
  region                          = "europe-central2"
  security_policy                 = "https://www.googleapis.com/compute/beta/projects/tidal-copilot-372909/regions/europe-central2/securityPolicies/default-security-policy-for-backend-service-streamlit"
  session_affinity                = "NONE"
  timeout_sec                     = 30
}
# terraform import google_compute_region_backend_service.streamlit projects/tidal-copilot-372909/regions/europe-central2/backendServices/streamlit
