"""MVP-Benachrichtigungen.

Für die Fallstudie wird kein SMTP-Server vorausgesetzt. Der Service erzeugt
deshalb nachvollziehbare Bestätigungsdaten, die später durch echten Mailversand
ersetzt werden können.
"""


class NotificationService:
    def booking_confirmation(self, user, booking, target_name: str = "") -> dict:
        recipient = getattr(user, "email", "")
        subject = f"RePlan Buchungsbestätigung: {booking.title}"
        message = (
            f"Ihre Buchung '{booking.title}'"
            f"{' für ' + target_name if target_name else ''} "
            f"von {booking.start_time} bis {booking.end_time} wurde angelegt."
        )
        return {
            "sent": bool(recipient),
            "recipient": recipient,
            "subject": subject,
            "message": message,
        }

    def booking_invitations(self, booking, target_name: str = "") -> list:
        """Erzeugt manuell teilbare Einladungen ohne externen SMTP-Dienst."""
        return [
            {
                "sent": False,
                "delivery": "manual",
                "recipient": email,
                "subject": f"RePlan Einladung: {booking.title}",
                "message": (
                    f"Sie wurden zu '{booking.title}'"
                    f"{' in ' + target_name if target_name else ''} eingeladen. "
                    f"Einladungscode: {booking.invitation_code}"
                ),
            }
            for email in booking.invitation_emails
        ]
