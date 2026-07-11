"""Universal Email MCP server — IMAP/SMTP backed, supports Gmail/Outlook/Yahoo/any provider via app passwords. Free, no paid APIs."""

from __future__ import annotations

import imaplib
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from src.config.settings import settings

logger = logging.getLogger(__name__)


class EmailMCPServer:
    def __init__(self) -> None:
        self.tools = [
            {"name": "list", "description": "List recent emails via IMAP", "inputSchema": {"type": "object", "properties": {"max_results": {"type": "integer", "default": 10}, "folder": {"type": "string", "default": "INBOX"}}, "required": []}},
            {"name": "draft", "description": "Draft a new email", "inputSchema": {"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}, "required": ["to", "subject", "body"]}},
            {"name": "send", "description": "Send an email via SMTP (requires explicit confirmation)", "inputSchema": {"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}, "required": ["to", "subject", "body"]}},
        ]

    async def call_tool(self, tool: str, arguments: dict[str, Any]) -> Any:
        if tool == "list":
            return await self._list(int(arguments.get("max_results", 10)), str(arguments.get("folder", "INBOX")))
        elif tool == "draft":
            return await self._draft(str(arguments["to"]), str(arguments["subject"]), str(arguments["body"]))
        elif tool == "send":
            return await self._send(str(arguments["to"]), str(arguments["subject"]), str(arguments["body"]))
        else:
            raise ValueError(f"Unknown tool: {tool}")

    async def _list(self, max_results: int, folder: str) -> list[dict[str, Any]]:
        if not settings.email_api_key:
            raise RuntimeError("email_api_key not configured. Set EMAIL_API_KEY in .env (format: user:app_password)")
        try:
            user, password = settings.email_api_key.split(":", 1)
            imap_host = self._imap_host_for(user)
            loop = __import__("asyncio").get_event_loop()
            def _sync_fetch():
                conn = imaplib.IMAP4_SSL(imap_host)
                conn.login(user, password)
                conn.select(folder)
                status, data = conn.search(None, "ALL")
                ids = data[0].split()[-max_results:]
                results = []
                for msg_id in ids:
                    status, msg_data = conn.fetch(msg_id, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
                    header = msg_data[0][1].decode("utf-8", errors="replace")
                    results.append({"id": msg_id.decode(), "header": header})
                conn.logout()
                return results
            return await loop.run_in_executor(None, _sync_fetch)
        except Exception as exc:
            logger.error("email_list_failed", error=str(exc))
            return []

    async def _draft(self, to: str, subject: str, body: str) -> dict[str, Any]:
        logger.info("email_draft", to=to, subject=subject)
        return {"status": "drafted", "to": to, "subject": subject, "body": body, "requires_confirmation": True}

    async def _send(self, to: str, subject: str, body: str) -> dict[str, Any]:
        if not settings.email_api_key:
            raise RuntimeError("email_api_key not configured")
        user, password = settings.email_api_key.split(":", 1)
        smtp_host = self._smtp_host_for(user)
        try:
            msg = MIMEMultipart()
            msg["From"] = user
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))
            loop = __import__("asyncio").get_event_loop()
            def _sync_send():
                with smtplib.SMTP_SSL(smtp_host, 465) as server:
                    server.login(user, password)
                    server.sendmail(user, [to], msg.as_string())
                return True
            await loop.run_in_executor(None, _sync_send)
            logger.info("email_sent", to=to, subject=subject)
            return {"status": "sent", "to": to, "subject": subject}
        except Exception as exc:
            logger.error("email_send_failed", error=str(exc))
            raise RuntimeError(f"SMTP send failed: {exc}") from exc

    @staticmethod
    def _imap_host_for(email: str) -> str:
        domain = email.split("@")[-1].lower()
        if domain in ("gmail.com",):
            return "imap.gmail.com"
        if domain in ("outlook.com", "hotmail.com", "live.com", "msn.com"):
            return "outlook.office365.com"
        if domain in ("yahoo.com", "yahoo.co.in", "yahoo.co.uk"):
            return "imap.mail.yahoo.com"
        return f"imap.{domain}"

    @staticmethod
    def _smtp_host_for(email: str) -> str:
        domain = email.split("@")[-1].lower()
        if domain in ("gmail.com",):
            return "smtp.gmail.com"
        if domain in ("outlook.com", "hotmail.com", "live.com", "msn.com"):
            return "smtp.office365.com"
        if domain in ("yahoo.com", "yahoo.co.in", "yahoo.co.uk"):
            return "smtp.mail.yahoo.com"
        return f"smtp.{domain}"
