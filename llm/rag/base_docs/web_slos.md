# Example Web SLOs

**Service**: web-frontend
**Objective**: Maintain low latency and high availability

## SLOs
- 99.9% of requests should respond within 300ms
- Availability should be above 99.95%

## SLIs
- latency_p95
- http_5xx_error_rate

## Notes
- Review latency spikes from Black Friday traffic (2023)
- Similar services: mobile-api, dashboard-web
