from security.decryptAmt import decryptt
from security.encrypyAmt import encryptt
from utils.IST import ISTdate, ISTTime
import random
from config.otp_configs import sender_email, sender_key
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import asyncio


async def get_amount(mesh:str):
    try:
        amount_mesh = mesh.split("#")[1]
        key_mesh = mesh.split("#")[-1]
        amount_en = amount_mesh.encode()

        data = await decryptt(token=amount_en, key= key_mesh.encode())
        return str(data)
    except IndexError:
        pass

async def share_ticket(ticket: str, email:str):

    message = Mail(
        from_email=sender_email,  # must be verified in SendGrid
        to_emails=email,
        subject="Trendy Ticket Service.",
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; background-color:#f9f9f9; padding:20px;">
            <div style="max-width:500px; margin:auto; background:#ffffff; padding:20px; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
                <h2 style="color:#333; text-align:center;">🎟️ Trendy Ticket Service</h2>
                <p style="color:#444; font-size:15px;">Hi there,</p>
                <p style="color:#444; font-size:15px;">
                    We’re excited to let you know that your ticket has been <b>successfully booked!</b>
                </p>
                <div style="text-align:center; margin:20px 0;">
                    <span style="display:inline-block; font-size:22px; font-weight:bold; letter-spacing:1px; color:#2196f3; padding:10px 20px; border:2px dashed #2196f3; border-radius:6px;">
                        Ticket ID: {ticket}
                    </span>
                </div>
                <p style="color:#444; font-size:15px;">
                    You can generate and view your ticket using the link below:
                </p>
                <div style="text-align:center; margin:20px 0;">
                    <a href="https://trendyticketservices.onrender.com/generate/ticket/event" style="display:inline-block; background-color:#4CAF50; color:#ffffff; padding:12px 24px; text-decoration:none; border-radius:6px; font-size:16px;">
                        🎫 Generate Your Ticket
                    </a>
                </div>
                <p style="color:#444; font-size:15px;">
                    Thank you for choosing <b>Trendy Ticket Service</b>. We hope you have a great experience!
                </p>
                <p style="color:#444; font-size:15px; margin-top:30px;">
                    Best regards,<br>
                    <b>Trendy Team</b>
                </p>
                <hr style="margin:20px 0; border:none; border-top:1px solid #eee;">
                <p style="font-size:12px; color:#888; text-align:center;">
                    If you didn’t make this booking, please contact our support team immediately.
                </p>
            </div>
        </body>
        </html>
        """

            )

    try:
        sg = SendGridAPIClient(sender_key)
        sg.send(message)
    except Exception as e:
        print(f"Error sending email: {e}")