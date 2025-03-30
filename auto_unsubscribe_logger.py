import asyncio
from playwright.async_api import async_playwright
import os

# ✅ Your real unsubscribe links from Zillow and SoundCloud
unsubscribe_links = [
    "https://click.mail.zillow.com/f/a/J-wlXyjl5G4rAI6linj9_g~~/AAAAARA~/AhK_SJbvxbf2MUW5W2_U1gIH2f0-dsKRtz4TsY54HzuYoaWJHNR8sdfmlPpHhPjTMgVBKvlP0kyYJj44X9WvE788cPrUOD4-pFKw8_8EJWvjyni0JjH2zvtjDu5F5-yQ4rPFjwMdUkJjSS8DYQF7Mw~~?target=https%3A%2F%2Fwww.zillow.com%2Femail%2FUnsubscribeEnrollment.htm%3Ftoken%3DenV3.1742932276544.GcgIaF8U0aE282MMEwI51g.6t_86Z6OL6VxjvOcFHkclHnDl5k1P0g0vxhFr2-teUI.EWQUTuMtfNtI1T0AQ9QQNol3ddN-CG00KYY8IIQzL0U%26rtoken%3Daa95b81e-7b0d-44ff-8ce9-51d72510eadb%257EX1-ZUtox5fzpu4hs9_7rj5o%26utm_campaign%3Demo-instant_home_recs_email%26utm_source%3Demail%26utm_term%3Durn%3Amsg%3A2025032519511653b107723c0e924a%26utm_medium%3Demail%26utm_content%3Dfooterunsub",

    "https://lurl.soundcloud.com/wf/unsubscribe?upn=u001.OCJbE0NEyXP7p1sxQrGA3exXN7tUKE7bjHwUFXt4-2Bv7Fi72CEcTWgGZPSOXqsCtL3pkFJa119CUQ6HPzA03G0ztgiGWh3Lm2z0oeRT7K0xy22-2FIUsaX0Pz-2FwptXPRdNDC5nFatShBAmZSzz5QMiqYGLw4nAYhhkn0I7RtBMtSDreEb-2FXkl35IP0cCdFG4MGt6INLqHfNWrAKGDbUL7WnaGHT5mqvMBFOEZjbNm288X3-2FV-2BQh9N9Lga1Ou76-2Bk3V3bkVfNzJ3lXlwSnIwURqJTT1jGaLGO2B9ZMbQTysFWoEP9ovPqxdyav-2FaAhyNTQhHXyNXU2vdrqt5CqLAi1XAjrW-2BXCBewSezET-2FIjrpqAQLz6-2Fegf4fTA8R2xFTBSSdh6Y7-2FpZdH-2BTt-2BrayDGiWv11Xt-2Bk7h-2BC77ovDvJOHXDjnMkUtCA6wVLYpm10y7xGscFKYx1PpSwBiNciKpvAIzKcZtL93DtU3KH4-2BcO2qS605CKEGzeituImWXP8aGAxBdftXNCQyZsoP1KGhdB9bklYD-2FefJFg4oidW7-2B-2BhAc7Dr1LkWLtwAgd20RwVlJHbXxtlmGmlKm9fKRhyfzBO7RXA-3D-3D"
]

# Common text to click
CLICK_TEXTS = ["Unsubscribe", "Confirm", "Stop", "Submit", "Yes", "Remove Me"]

# Keywords to detect login walls
LOGIN_KEYWORDS = ["login", "sign in", "log in", "account access", "enter credentials"]

# Make sure screenshots folder exists
os.makedirs("unsubscribe_screenshots", exist_ok=True)

async def auto_unsubscribe_logger():
    async with async_playwright() as p:
        print("🚀 Launching browser...")
        browser = await p.chromium.launch(headless=False, slow_mo=200)
        context = await browser.new_context()
        page = await context.new_page()

        for i, link in enumerate(unsubscribe_links):
            print(f"\n🔗 Opening ({i+1}/{len(unsubscribe_links)}): {link}")
            try:
                await page.goto(link, timeout=20000)
                await page.wait_for_timeout(2000)

                # Check for login-type content
                content = await page.content()
                is_login_page = any(word in content.lower() for word in LOGIN_KEYWORDS)

                if is_login_page:
                    print("🔐 Login page detected — skipping click.")
                    result = "❌ Login Required"
                else:
                    # Try to click unsubscribe button
                    clicked = False
                    for text in CLICK_TEXTS:
                        try:
                            button = page.get_by_role("button", name=text, exact=False)
                            if await button.is_visible():
                                print(f"🖱️ Clicking button: {text}")
                                await button.click()
                                await page.wait_for_timeout(2000)
                                clicked = True
                                break
                        except:
                            continue

                    result = "✅ Clicked" if clicked else "🕒 Opened Only"

                # Save screenshot
                screenshot_path = f"unsubscribe_screenshots/page{i+1}.png"
                await page.screenshot(path=screenshot_path)
                print(f"📸 Saved screenshot: {screenshot_path}")
                print(f"📌 Result: {result}")

            except Exception as e:
                print(f"⚠️ Error processing link:")
                print(f"   {e}")

        await browser.close()
        print("\n✅ All unsubscribe links processed.")

# Run it
asyncio.run(auto_unsubscribe_logger())

