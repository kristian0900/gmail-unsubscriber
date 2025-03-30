import time

def log_to_google_sheets(results):
    creds = service_account.Credentials.from_service_account_file(
        'credentials.json',
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)

    spreadsheet = client.open("Gmail Unsubscribe Logs")
    sheet_title = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    worksheet = spreadsheet.add_worksheet(title=sheet_title, rows="100", cols="20")

    worksheet.append_row(["Unsubscribe URL", "Result", "Email Subject"])
    
    for item in results:
        worksheet.append_row([item["url"], item["result"], item["subject"]])
        time.sleep(1.2)  # 💤 Wait to avoid quota limit
