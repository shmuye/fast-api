import logging

import httpx

from api.config import config

logger = logging.getLogger(__name__)

class APIResponseError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API Error {status_code}: {detail}")

async def send_simple_email(to: str, subject: str, body: str):
    logger.debug(f"Sending email to {to} with subject '{subject}'")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://api.mailgun.net/v3/{config.MAILGUN_DOMAIN}/messages",
                auth=("api", config.MAILGUN_API_KEY),
                data={
                    "from": f"Shumye Ayalneh <mailgun@{config.MAILGUN_DOMAIN}>",
                    "to": [to],
                    "subject": subject,
                    "text": body
                }
            )
            response.raise_for_status()
            logger.debug(response.content)
            return response
        
        except httpx.HTTPStatusError as err:
            logger.error(f"Failed to send email to {to}: {err}")
            raise APIResponseError(
                f"API request failed with status code {err.response.status_code} "
            ) from err
    
async def send_registeration_email(email: str, confirmation_url: str):
    return await send_simple_email(
        email,
        "successfully signed up",
        f"Hi, {email} you have successfully signed up to the REST API,"
        "please verify your email by clicking on the following ${confirmation_url}"

    )


