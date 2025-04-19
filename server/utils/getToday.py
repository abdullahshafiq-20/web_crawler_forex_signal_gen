from datetime import datetime



def get_today_data(data):
    today = datetime.now().strftime('%Y-%m-%d')
    todays_data = [entry for entry in data if entry.get('date') == today]
    return todays_data

