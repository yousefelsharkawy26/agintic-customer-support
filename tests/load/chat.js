import { check, sleep } from 'k6';
import http from 'k6/http';

const BASE = 'http://localhost:8080';
const TOKEN = __ENV.AUTH_TOKEN || '';

export const options = {
  stages: [
    { duration: '10s', target: 5 },
    { duration: '20s', target: 20 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000', 'p(99)<5000'],
    http_req_failed: ['rate<0.05'],
  },
};

export default function () {
  const payload = JSON.stringify({
    message: 'Load test message ' + __VU + '_' + __ITER,
  });
  const res = http.post(`${BASE}/api/v1/chat`, payload, {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${TOKEN}`,
    },
  });
  check(res, {
    'chat status 200': (r) => r.status === 200,
  });
  sleep(1);
}
