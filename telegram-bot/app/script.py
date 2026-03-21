import requests
import traceback

BOT_TOKEN = "8796380258:AAGM0lR-s4FrjdOCdnOMswE0bcvrKhkfR64"
CHAT_ID = "656121499"

def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })
    
    print("Status:", response.status_code)
    print("Response:", response.text)

def main():
    try:
        print("Test error...")
        x = 1 / 0
    except Exception as e:
        error_message = f"❌ ERROR\n{str(e)}\n{traceback.format_exc()}"
        send_alert(error_message)

if __name__ == "__main__":
    main()
