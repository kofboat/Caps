import logging
import sys
import time

from app.config import AppConfig
from app.engine import ReminderState, run_once
from app.sheets import GoogleSheetsClient
from app.twilio_client import TwilioClient


def setup_logging():
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s %(levelname)s %(message)s",
	)


def main():
	setup_logging()
	cfg = AppConfig.from_env()
	try:
		cfg.assert_minimum()
	except Exception as e:
		logging.error("Configuration error: %s", e)
		sys.exit(1)

	sheets = GoogleSheetsClient(cfg.google_sheet_id, cfg.google_worksheet_name, cfg.google_credentials_json_path)
	texter = TwilioClient(cfg.twilio_account_sid, cfg.twilio_auth_token, cfg.twilio_from_number, cfg.dry_run)
	state = ReminderState(cfg.state_db_path)

	logging.info("Reminder service starting. Dry run: %s", cfg.dry_run)
	while True:
		try:
			count = run_once(
				sheets=sheets,
				texter=texter,
				state=state,
				minutes_before=cfg.reminder_minutes_before,
				default_tz=cfg.default_timezone,
			)
			if count:
				logging.info("Sent %d reminders", count)
		except Exception as e:
			logging.exception("Error in run loop: %s", e)
		finally:
			time.sleep(cfg.poll_interval_seconds)


if __name__ == "__main__":
	main()