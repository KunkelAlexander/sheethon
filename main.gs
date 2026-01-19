/***************
 * CONFIG
 ***************/
const BASE_URL = "https://YOUR_NGROK_DOMAIN.ngrok-free.app"; // <-- change this
const USERNAME = "user"; // <-- must match server
const PASSWORD = "pass"; // <-- must match server



/***************
 * PUBLIC SHEET FUNCTIONS
 ***************/
function PY_ADD(a, b) {
  return compute_("ADD", a, b);
}

function PY_MULTIPLY(a, b) {
  return compute_("MULTIPLY", a, b);
}


/***************
 * CORE
 ***************/
function compute_(op, a, b) {
  a = Number(a);
  b = Number(b);
  if (isNaN(a) || isNaN(b)) return "ERROR: inputs must be numbers";

  const res = fetchJson_("/compute", { op, a, b });

  const res = fetchJson_("/compute", { op, a, b });
  if (res.error)                   return "SERVER ERROR: " + res.error;
  if (res.result === undefined)    return "ERROR: missing result";
  if (res.status === "done")       return res.result;
  if (res.status === "processing") return "PROCESSING";
  
  return "ERROR: undefined state";
}


/***************
 * HTTP HELPER
 ***************/
function fetchJson_(path, data) {
  try {
    const resp = UrlFetchApp.fetch(BASE_URL + path, {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(data),
      headers: {
        Authorization: "Basic " + Utilities.base64Encode(USERNAME + ":" + PASSWORD),
        "ngrok-skip-browser-warning": "1",
      },
      muteHttpExceptions: true,
    });

    const code = resp.getResponseCode();
    const text = resp.getContentText();

    if (code !== 200) return { error: `HTTP ${code}: ${text}` };
    return JSON.parse(text);
  } catch (e) {
    return { error: String(e) };
  }
}
