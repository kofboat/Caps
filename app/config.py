import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


load_dotenv()


@dataclass
class AppConfig:
	# Google Sheets
	google_sheet_id: str
	google_worksheet_name: str
	google_credentials_json_path: Optional[str]

	# Twilio
	twilio_account_sid: Optional[str]
	twilio_auth_token: Optional[str]
	twilio_from_number: Optional[str]

	# Behavior
	default_timezone: str
	reminder_minutes_before: int
	poll_interval_seconds: int
	dry_run: bool

	# State
	state_db_path: str

	@staticmethod
	def from_env() -> "AppConfig":
		return AppConfig(
			google_sheet_id=os.getenv("GOOGLE_SHEET_ID", ""),
			google_worksheet_name=os.getenv("GOOGLE_WORKSHEET_NAME", "Shifts"),
			google_credentials_json_path=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_PATH"),
			twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID"),
			twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN"),
			twilio_from_number=os.getenv("TWILIO_FROM_NUMBER"),
			default_timezone=os.getenv("DEFAULT_TIMEZONE", "America/New_York"),
			reminder_minutes_before=int(os.getenv("REMINDER_MINUTES_BEFORE", "5")),
			poll_interval_seconds=int(os.getenv("POLL_INTERVAL_SECONDS", "60")),
			dry_run=os.getenv("DRY_RUN", "true").lower() in {"1", "true", "yes", "y"},
			state_db_path=os.getenv("STATE_DB_PATH", "/workspace/data/reminders.db"),
		)

	def assert_minimum(self) -> None:
		if not self.google_sheet_id:
			raise ValueError("GOOGLE_SHEET_ID must be set in environment")