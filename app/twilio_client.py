from __future__ import annotations

import logging
from typing import Optional

from twilio.rest import Client as TwilioRestClient


class TwilioClient:
	def __init__(self, account_sid: Optional[str], auth_token: Optional[str], from_number: Optional[str], dry_run: bool = False):
		self.account_sid = account_sid
		self.auth_token = auth_token
		self.from_number = from_number
		self.dry_run = dry_run or not (account_sid and auth_token and from_number)
		self._client: Optional[TwilioRestClient] = None

		if not self.dry_run:
			self._client = TwilioRestClient(self.account_sid, self.auth_token)

	def send_sms(self, to_number_e164: str, body: str) -> None:
		if self.dry_run:
			logging.info("[DRY_RUN] Would send SMS to %s: %s", to_number_e164, body)
			return
		assert self._client is not None and self.from_number is not None
		self._client.messages.create(
			to=to_number_e164,
			from_=self.from_number,
			body=body,
		)