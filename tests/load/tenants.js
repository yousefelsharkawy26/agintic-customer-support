import { check, sleep } from 'k6';
import http from 'k6/http';

const BASE = 'http://localhost:8080';
const TOKEN = __ENV.AUTH_TOKEN || '';

export const options = {
  vus: 5,
  duration: '20s',
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.02'],
  },
};

export default function () {
  const res = http.get(`${BASE}/api/v1/tenants/t1/config`, {
    headers: { Authorization: `Bearer ${TOKEN}` },
  });
  check(res, {
    'tenant config status 200': (r) => r.status === 200,
  });
  sleep(0.5);
}
