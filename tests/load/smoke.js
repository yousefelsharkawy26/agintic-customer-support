import { check, sleep, group } from 'k6';
import http from 'k6/http';

const BASE = 'http://localhost:8080';
const TOKEN = __ENV.AUTH_TOKEN || '';

export const options = {
  vus: 3,
  duration: '15s',
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  group('health', function () {
    const res = http.get(`${BASE}/health`);
    check(res, { 'health 200': (r) => r.status === 200 });
  });

  group('readiness', function () {
    const res = http.get(`${BASE}/ready`);
    check(res, { 'ready 200': (r) => r.status === 200 });
  });

  group('auth', function () {
    const res = http.get(`${BASE}/api/v1/webhooks/providers`, {
      headers: { Authorization: `Bearer ${TOKEN}` },
    });
    check(res, { 'auth 200': (r) => r.status === 200 });
  });

  group('404', function () {
    const res = http.get(`${BASE}/api/v1/webhooks/configs/nonexistent`, {
      headers: { Authorization: `Bearer ${TOKEN}` },
    });
    check(res, { 'not_found 404': (r) => r.status === 404 });
  });

  sleep(1);
}
