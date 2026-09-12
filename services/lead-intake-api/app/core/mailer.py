import asyncio
import httpx
class MailgunDeliveryError(RuntimeError): pass
class MailgunMailer:
    def __init__(self,settings): self.settings=settings
    async def _send(self,to:str,subject:str,text:str)->None:
        url=f"{self.settings.mailgun_api_base_url.rstrip('/')}/v3/{self.settings.mailgun_domain}/messages"
        payload={"from":self.settings.mailgun_from,"to":to,"subject":subject,"text":text,"h:Reply-To":self.settings.mail_reply_to}
        async with httpx.AsyncClient(timeout=15) as client:
            for attempt in range(3):
                try:
                    response=await client.post(url,auth=("api",self.settings.mailgun_api_key),data=payload)
                    response.raise_for_status(); return
                except (httpx.HTTPError,httpx.TimeoutException) as exc:
                    if attempt==2: raise MailgunDeliveryError("Mailgun delivery failed") from exc
                    await asyncio.sleep(2**attempt)
    async def send_submission(self,first_name:str,last_name:str,email:str)->None:
        await self._send(email,"We received your information",f"Hi {first_name},\n\nThank you for contacting us. We received your submission and will be in touch.")
        await self._send(self.settings.attorney_intake_email,"New lead submitted",f"New lead: {first_name} {last_name} <{email}>. Please review it in the attorney dashboard.")