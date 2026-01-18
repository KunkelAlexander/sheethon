/***************
 * CONFIG
 ***************/
const BASE_URL = "https://YOUR_NGROK_DOMAIN.ngrok-free.app"; // <-- change this
const USERNAME = "user"; // <-- must match server
const PASSWORD = "pass"; // <-- must match server

// How long we poll before giving up for THIS calculation call
const MAX_POLL_MS = 3500;
const POLL_INTERVAL_MS = 400;

// Cache how long (seconds) we remember a submitted job_id for given inputs
const CACHE_TTL_SECONDS = 3600;


/***************
 * PUBLIC SHEET FUNCTIONS
 ***************/
function PY_ADD(a, b) {
  return runRemoteOp_("ADD", a, b);
}

function PY_MULTIPLY(a, b) {
  return runRemoteOp_("MULTIPLY", a, b);
}


/***************
 * CORE LOGIC
 ***************/
function runRemoteOp_(op, a, b) {
  a = Number(a);
  b = Number(b);

  if (isNaN(a) || isNaN(b)) {
    return "ERROR: inputs must be numbers";
  }

  const cache = CacheService.getScriptCache();
  const cacheKey = makeCacheKey_(op, a, b);

  // 1) reuse existing job_id if we already submitted
  let jobId = cache.get(cacheKey);

  // 2) otherwise submit new job
  if (!jobId) {
    const submitResp = submitJob_(op, a, b);
    if (submitResp.error) return submitResp.error;

    jobId = submitResp.job_id;
    cache.put(cacheKey, jobId, CACHE_TTL_SECONDS);
  }

  // 3) poll result until ready (or timeout)
  const start = Date.now();
  while (Date.now() - start < MAX_POLL_MS) {
    const res = getResult_(jobId);
    if (res.error) return res.error;

    if (res.status === "done") {
      return res.result;
    }
    if (res.status === "error") {
      return "SERVER ERROR: " + res.result;
    }

    Utilities.sleep(POLL_INTERVAL_MS);
  }

  // Not ready yet
  return "PROCESSING";
}


/***************
 * HTTP CALLS
 ***************/
 function submitJob_(op, a, b) {
  try {
    const url = BASE_URL + "/submit";
    const payload = JSON.stringify({ op: op, a: a, b: b });

    const response = UrlFetchApp.fetch(url, {
      method: "post",
      contentType: "application/json",
      payload: payload,
      headers: {
        Authorization: basicAuthHeader_(USERNAME, PASSWORD),
        "ngrok-skip-browser-warning": "1",
      },
      muteHttpExceptions: true,
    });

    const code = response.getResponseCode();
    const body = response.getContentText();

    if (code !== 200) {
      return { error: `SUBMIT FAILED (${code}): ${body}` };
    }

    return JSON.parse(body);
  } catch (e) {
    return { error: "SUBMIT EXCEPTION: " + e };
  }
}

function getResult_(jobId) {
  try {
    const url = BASE_URL + "/result/" + encodeURIComponent(jobId);

    const response = UrlFetchApp.fetch(url, {
      method: "get",
      headers: {
        Authorization: basicAuthHeader_(USERNAME, PASSWORD),
        "ngrok-skip-browser-warning": "1",
      },
      muteHttpExceptions: true,
    });

    const code = response.getResponseCode();
    const body = response.getContentText();

    if (code !== 200) {
      return { error: `RESULT FAILED (${code}): ${body}` };
    }

    // helpful debug if HTML comes back again
    if (!body.trim().startsWith("{")) {
      return { error: `Non-JSON response (${code}): ${body.slice(0, 200)}` };
    }

    return JSON.parse(body);
  } catch (e) {
    return { error: "RESULT EXCEPTION: " + e };
  }
}



/***************
 * HELPERS
 ***************/
function basicAuthHeader_(user, pass) {
  const token = Utilities.base64Encode(user + ":" + pass);
  return "Basic " + token;
}

function makeCacheKey_(op, a, b) {
  // keep stable key formatting
  return `pyjob:${op}:${a}:${b}`;
}