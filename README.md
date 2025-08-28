# Caps Pharmacy
This project is based on data from my pharmacy in Ghana that I am tracking
using R and shinyapp to develop a dashboard 
for my staff and investors to know where we are financially

### Caregiver Clock In/Out Reminder Service

Sends SMS reminders via Twilio to caregivers 5 minutes before scheduled start and end times, sourced from a Google Sheet.

### Google Sheet Schema
Use header names (case-insensitive):
- **id**: optional stable row identifier; if blank, a derived key is used
- **caregiver_name**: recipient name
- **phone**: caregiver phone (any format; normalized to E.164)
- **start**: shift start (e.g., `2025-08-28 09:00`)
- **end**: shift end (optional)
- **timezone**: IANA tz (e.g., `America/New_York`). If blank, `UTC` used

Accepted alternates: `name`, `phone_number`, `start_time`, `start_at`, `end_time`, `end_at`, `tz`.

### Setup
1. Copy `.env.example` to `.env` and fill values.
2. For private sheets, create a Google Service Account and share the Sheet with the service account email. Save the JSON at `GOOGLE_SERVICE_ACCOUNT_JSON_PATH`.
3. Create a Twilio account and set `TWILIO_*` env vars. Keep `DRY_RUN=true` to test without sending.

### Install
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run
```bash
python main.py
```

### Notes
- Deduplication: reminders are recorded in `STATE_DB_PATH` to prevent duplicates per shift and kind (start/end).
- Timezones: shift datetimes are stored as UTC internally and presented in the shift timezone for messages.
- Public sheet mode: if `GOOGLE_SERVICE_ACCOUNT_JSON_PATH` is empty and the sheet is public-readable, access works without auth.
