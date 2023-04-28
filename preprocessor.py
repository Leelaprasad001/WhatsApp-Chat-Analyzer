import re
import pandas as pd

def preprocess(data):
    # Regular expression pattern
    pattern = r'(\d{1,2}\/\d{1,2}\/\d{2}),?\s(\d{1,2}:\d{2})\s?(am|pm)?\s-\s(.+?):\s(.+)'

    # Create an empty list to store the rows of the DataFrame
    rows = []

    # Loop over the messages and extract the date, time, am/pm, username, and message using the pattern
    for message in data.split('\n'):
        match = re.search(pattern, message)
        if match is not None:
            date = match.group(1)
            time = match.group(2)
            ampm = match.group(3)
            username = match.group(4)
            msg = match.group(5)
    
            # Append the row to the list
            rows.append({
                'only_date': date,
                't': time,
                'ampm' : ampm,
                'username': username,
                'message': msg
            })

    # Create a Pandas DataFrame from the list of rows
    df = pd.DataFrame(rows)
    
    df['only_date'] = pd.to_datetime(df['only_date'], format='%d/%m/%y')
    # Convert the date column to the '%Y-%m-%d' format
    df['only_date'] = df['only_date'].dt.strftime('%Y-%m-%d')
    
    # converting into 24hrs
    df['time'] = df.apply(lambda x: f"{x['t']} {x['ampm']}", axis=1)
    df = df.drop(['t', 'ampm'], axis=1)
    
    def convert_time(time_str):
        time_obj = pd.to_datetime(time_str, format='%I:%M %p')
        return time_obj.strftime('%H:%M')

    df['only_time'] = df['time'].apply(convert_time)

    # Drop the original 'time' column if desired
    df = df.drop('time', axis=1)
    # converting into 24hrs
    df['date'] = df.apply(lambda x: f"{x['only_date']} {x['only_time']}", axis=1)
    df[['year', 'month_num', 'day']] = df['only_date'].str.split('-', expand=True)

    # Convert the month number to month name
    df['month'] = pd.to_datetime(df['month_num'], format='%m').dt.strftime('%B')

    # Convert the date to day name
    df['day_name'] = pd.to_datetime(df['only_date']).dt.strftime('%A')
    
    # Split the time column into two separate columns for hour and minute
    df[['hour', 'minute']] = df['only_time'].str.split(':', expand=True)
    
    #add period column that shows data capture between which 24 hour format
    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        h = int(hour)+1
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(h))
    df['period'] = period
    
    
    return df