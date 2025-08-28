from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Dict, List, Optional

import gspread
from dateutil import parser as date_parser
from google.oauth2.service_account import Credentials


@dataclass
class Shift:
	shift_key: str
	caregiver_name: str
	caregiver_phone_e164: str
	start_at: dt.datetime
	end_at: Optional[dt.datetime]
	timezone: str


class GoogleSheetsClient:
	def __init__(self, google_sheet_id: str, worksheet_name: str, credentials_json_path: Optional[str]):
		self.google_sheet_id = google_sheet_id
		self.worksheet_name = worksheet_name
		self.credentials_json_path = credentials_json_path

	def _open_worksheet(self):
		if self.credentials_json_path:
			creds = Credentials.from_service_account_file(self.credentials_json_path, scopes=[
				"https://www.googleapis.com/auth/spreadsheets.readonly",
			])
			gc = gspread.authorize(creds)
		else:
			# Attempt without creds (only works if sheet is publicly readable)
			gc = gspread.client.Client(None)
		return gc.open_by_key(self.google_sheet_id).worksheet(self.worksheet_name)

	def fetch_shifts(self) -> List[Shift]:
		ws = self._open_worksheet()
		rows: List[Dict[str, str]] = ws.get_all_records()

		shifts: List[Shift] = []
		for row in rows:
			# Expected headers: id, caregiver_name, phone, start, end, timezone
			shift_id = str(row.get("id") or "").strip()
			caregiver_name = str(row.get("caregiver_name") or row.get("name") or "").strip()
			phone = str(row.get("phone") or row.get("phone_number") or "").strip()
			start_raw = str(row.get("start") or row.get("start_time") or row.get("start_at") or "").strip()
			end_raw = str(row.get("end") or row.get("end_time") or row.get("end_at") or "").strip()
			tz = str(row.get("timezone") or row.get("tz") or "").strip() or "UTC"

			if not caregiver_name or not phone or not start_raw:
				continue

			start_at = _parse_datetime(start_raw, tz)
			end_at = _parse_optional_datetime(end_raw, tz)

			derived_key = f"{phone}|{start_at.isoformat()}"
			shift_key = shift_id or derived_key

			shifts.append(Shift(
				shift_key=shift_key,
				caregiver_name=caregiver_name,
				caregiver_phone_e164=_normalize_phone(phone),
				start_at=start_at,
				end_at=end_at,
				timezone=tz,
			))

		return shifts


def _parse_datetime(value: str, timezone: str) -> dt.datetime:
	"""Parse a date/time string and attach timezone.
	Accepts ISO, 'YYYY-MM-DD HH:MM', or Google Sheets datetime strings.
	"""
	parsed = date_parser.parse(value)
	if parsed.tzinfo is None:
		# Attach timezone if naive
		from dateutil import tz as dateutil_tz
		tzinfo = dateutil_tz.gettz(timezone) or dateutil_tz.UTC
		parsed = parsed.replace(tzinfo=tzinfo)
	return parsed.astimezone(dt.timezone.utc)


def _parse_optional_datetime(value: str, timezone: str) -> Optional[dt.datetime]:
	value = (value or "").strip()
	if not value:
		return None
	return _parse_datetime(value, timezone)


def _normalize_phone(phone: str) -> str:
	# Very basic E.164 normalization; assumes US by default if no '+' present
	digits = "".join(c for c in phone if c.isdigit())
	if phone.strip().startswith("+"):
		return "+" + digits
	# Assume US country code if 10 digits
	if len(digits) == 10:
		return "+1" + digits
	if len(digits) > 10 and not digits.startswith("1"):
		return "+" + digits
	return "+" + digits