from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json
import asyncio
from playwright.async_api import async_playwright

load_dotenv()

# -------- GPT Extraction -------- #
chat_model = ChatOpenAI()

user_instruction = "Make me a Reddit account called greenwave77 with password SweetSun5 and email greenwave77@email.com"

prompt = f"""
Extract the following fields from this instruction:
- username
- password
- email

Respond ONLY in JSON like this:
{{
  "username": "value",
  "password": "value",
  "email": "value"
}}

Instruction: {user_instruction}
"""

try:
    response = chat_model.invoke(prompt)
    creds = json.loads(response.content)
    username = creds["username"]
    password = creds["password"]
    email = creds["email"]

    print(f"\n✅ GPT Extracted:")
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print(f"  Email: {email}\n")

except Exception as e:
    print(f"❌ GPT extraction failed: {e}")
    exit()

# -------- Playwright Automation -------- #
async def run():
    browser = None
    try:
        async with async_playwright() as p:
            print("🚀 Launching browser...")
            browser = await p.chromium.launch(headless=False, slow_mo=100)
            context = await browser.new_context()
            page = await context.new_page()

            print("🌐 Navigating to Reddit signup...")
            await page.goto("https://www.reddit.com/register", wait_until='networkidle')

            # Handle cookie popup if present
            try:
                await page.click('button:has-text("Accept all")', timeout=5000)
                print("🍪 Accepted cookies.")
            except:
                print("🔕 No cookie popup found.")

            # STEP 1: Fill Email
            print("✍️ Filling email...")
            await page.wait_for_selector('input[type="email"]', timeout=30000)
            # Click the email field to ensure focus
            await page.click('input[type="email"]')
            await page.fill('input[type="email"]', email)

            print("👉 Clicking Continue...")
            await page.click('button.AnimatedForm__submitButton')

            # STEP 2: Fill Username and Password
            print("⏳ Waiting for username/password fields...")
            await page.wait_for_selector('input#regUsername', timeout=30000)
            await page.fill('input#regUsername', username)
            await page.fill('input#regPassword', password)

            print("✅ Username and password filled.")
            await page.wait_for_timeout(10000)

    except Exception as e:
        print(f"❌ Playwright automation failed: {e}")
        if browser:
            try:
                page = browser.contexts[0].pages[0]
                await page.screenshot(path="reddit_signup_error.png")
                print("📸 Screenshot saved as reddit_signup_error.png")
            except:
                print("⚠️ Failed to take screenshot.")

    finally:
        if browser:
            await browser.close()

# Run the flow
asyncio.run(run())


