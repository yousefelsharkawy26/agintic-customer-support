import { check } from 'k6';
import http from 'k6/http';

export const options = {
  vus: 10,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<200', 'p(99)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const res = http.get('http://localhost:8080/health');
  check(res, {
    'health status 200': (r) => r.status === 200,
    'body has status ok': (r) => r.json('status') === 'ok',
  });
}
