## README

### What this project does

This project runs a small Python web server that exposes two functions: `ADD` and `MULTIPLY`.

Google Sheets can call the server through Google Apps Script. The server does not compute results immediately. Instead, it puts each request into a background queue and returns `"processing"` until the job is finished.

The server is exposed to the internet using ngrok.

---

### Requirements

* Python 3.9+
* An ngrok account and auth token

---

### Install

```bash
pip install -r requirements.txt
```

Set your ngrok token:

```bash
export NGROK_AUTHTOKEN="YOUR_TOKEN"
```

---

### Run the server

```bash
python main.py
```

This will print a public ngrok URL. Use that URL in the Google Apps Script configuration.

---

### API endpoints

#### Submit a job

`POST /submit`

Example body:

```json
{"op":"ADD","a":5,"b":7}
```

Response:

```json
{"status":"pending","job_id":"..."}
```

#### Get a result

`GET /result/{job_id}`

While running:

```json
{"status":"processing","result":null}
```

When finished:

```json
{"status":"done","result":12}
```

---

### Google Sheets setup

1. Open your Google Sheet
2. Go to Extensions → Apps Script
3. Paste the provided script into `Code.gs`
4. Set `BASE_URL`, `USERNAME`, and `PASSWORD`

Then use formulas like:

```excel
=PY_ADD(5,7)
=PY_MULTIPLY(3,4)
```
