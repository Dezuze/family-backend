const base = process.env.API_BASE || 'http://localhost:8000';
const email = process.env.SIM_EMAIL || 'test@example.com';
const password = process.env.SIM_PASS || 'hunter2';
const csrfPresent = process.env.SIM_CSRF === 'true';
const csrftoken = csrfPresent ? 'dummy-csrf-token' : null;

const csrfFetch = {
  url: `${base}/api/csrf/`,
  options: { method: 'GET', credentials: 'include' },
};

const loginHeaders = { 'Content-Type': 'application/json' };
if (csrftoken) loginHeaders['X-CSRFToken'] = csrftoken;

const loginFetch = {
  url: `${base}/api/auth/login/`,
  options: {
    method: 'POST',
    headers: loginHeaders,
    credentials: 'include',
    body: JSON.stringify({ identifier: email, password }),
  },
};

console.log('\n--- Simulated fetch sequence ---\n');
console.log('1) CSRF initialization request:');
console.log(JSON.stringify(csrfFetch, null, 2));
console.log('\n2) Login request:');
console.log(JSON.stringify(loginFetch, null, 2));

console.log('\n--- Equivalent fetch calls ---\n');
console.log(`fetch('${csrfFetch.url}', ${JSON.stringify(csrfFetch.options, null, 2)});`);
console.log('\n');
console.log(`fetch('${loginFetch.url}', ${JSON.stringify(loginFetch.options, null, 2)});`);

console.log('\n(You can toggle CSRF presence by setting SIM_CSRF=true when running the script)\n');