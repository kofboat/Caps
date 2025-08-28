from __future__ import annotations

import datetime as dt
import logging
import os
import sqlite3
from typing import Iterable, List, Optional, Tuple

from dateutil import tz as dateutil_tz

from .sheets import GoogleSheetsClient, Shift
from .twilio_client import TwilioClient


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sent_reminders (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	reminder_key TEXT NOT NULL UNIQUE,
	created_at_utc TEXT NOT NULL
);
"""


class ReminderState:
	def __init__(self, db_path: str):
		os.makedirs(os.path.dirname(db_path), exist_ok=True)
		self.conn = sqlite3.connect(db_path)
		self.conn.execute(SCHEMA_SQL)
		self.conn.commit()

	def has_sent(self, reminder_key: str) -> bool:
		cur = self.conn.execute("SELECT 1 FROM sent_reminders WHERE reminder_key = ?", (reminder_key,))
		row = cur.fetchone()
		return row is not None

	def mark_sent(self, reminder_key: str) -> None:
		self.conn.execute(
			"INSERT OR IGNORE INTO sent_reminders (reminder_key, created_at_utc) VALUES (?, ?)",
			(reminder_key, dt.datetime.now(dt.timezone.utc).isoformat()),
		)
		self.conn.commit()


def _reminder_key(prefix: str, shift: Shift) -> str:
	return f"{prefix}:{shift.shift_key}"


def _format_time_local(d: dt.datetime, tz: str) -> str:
	tzinfo = dateutil_tz.gettz(tz) or dateutil_tz.UTC
	return d.astimezone(tzinfo).strftime("%Y-%m-%d %I:%M %p %Z")


def find_due_reminders(now_utc: dt.datetime, shifts: Iterable[Shift], minutes_before: int) -> Tuple[List[Tuple[str, Shift]], List[Tuple[str, Shift]]]:
	start_due: List[Tuple[str, Shift]] = []
	end_due: List[Tuple[str, Shift]] = []
	lead = dt.timedelta(minutes=minutes_before)
	for s in shifts:
		start_remind_at = s.start_at - lead
		if start_remind_at <= now_utc < s.start_at:
			start_due.append(("start", s))
		if s.end_at is not None:
			end_remind_at = s.end_at - lead
			if end_remind_at <= now_utc < s.end_at:
				end_due.append(("end", s))
	return start_due, end_due


def run_once(
	*,
	sheets: GoogleSheetsClient,
	texter: TwilioClient,
	state: ReminderState,
	minutes_before: int,
	default_tz: str,
) -> int:
	shifts = sheets.fetch_shifts()
	now_utc = dt.datetime.now(dt.timezone.utc)
	start_due, end_due = find_due_reminders(now_utc, shifts, minutes_before)

	sent = 0
	for kind, shift in start_due:
		key = _reminder_key("start", shift)
		if state.has_sent(key):
			continue
		msg = f"Hi {shift.caregiver_name}, please clock IN by {_format_time_local(shift.start_at, shift.timezone or default_tz)}. Reply YES when done."
		texter.send_sms(shift.caregiver_phone_e164, msg)
		state.mark_sent(key)
		sent += 1

	for kind, shift in end_due:
		key = _reminder_key("end", shift)
		if state.has_sent(key):
			continue
		msg = f"Hi {shift.caregiver_name}, please clock OUT by {_format_time_local(shift.end_at or shift.start_at, shift.timezone or default_tz)}. Reply YES when done."
		texter.send_sms(shift.caregiver_phone_e164, msg)
		state.mark_sent(key)
		sent += 1

	return sent