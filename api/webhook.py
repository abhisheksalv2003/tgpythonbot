# api/webhook.py
from telegram import Update
from main import application
import json

async def webhook(request):
    try:
        # Get the request body
        body = await request.json()
        
        # Create Update object
        update = Update.de_json(body, application.bot)
        
        # Process Update
        await application.process_update(update)
        
        return {"statusCode": 200, "body": "success"}
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}

# Handler for Vercel serverless function
async def handler(request):
    if request.method == "POST":
        return await webhook(request)
    return {"statusCode": 405, "body": "Method not allowed"}
