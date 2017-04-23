# Bookmyshow tickets notifier
Python code to check if movie tickets are available in in.bookmyshow.com


## Note : 
- Configured to work for Hyderabad city.
- Looks for tickets that cost <= 150 INR . Price range of the non-recliner multiplex seats in Hyderabad
- This script DOEST NOT book tickets. It only sends you a notification.

## Dependencies:
- You will need Python 3.x to run this script. Get it from https://www.python.org/downloads/
- Once python 3 is installed you need a 'beautifulsoup4' dependency to run the script.
- To install the dependency run from your favorite terminal:
```
pip install beautifulsoap4
```


## Usage :
- Open `bookmyshow.py` in your favorite editor.
- Look for `YOUR_GMAIL_ID_HERE` (occurs 2 times in the script) and replace it with any of your gmail id.
- Look for `YOUR_GMAIL_PASSWORD_HERE` and replace it with the corresponding gmail password
- The above gmail id is used to send you email notifications once the script finds tickets.
- Your gmail id and password are completely safe and exist only locally. If you don't want to or cant use your current gmail id for some reason create a secondary gmail to receive notifications.
- The above gmail id is different from the "email" prarm you pass to the script(Look below). The above gmail id is used to send notifications. The "email" param is used to send notifications.

You are ready!!

Example usage:  
```
$ python3 bookmyshow.py --movie "Baahubali,conclusion" --theaters "Inorbit,Forum" --email "your@email.com" --searchFrom "20170304" --searchFor "3"
```

The above code searches for Movie tickets of 'Baahubali - The Conclusion'(The movie whos name has both the words 'Baahubali' and 'conclusion'. Can add more terms if needed. Case insensitive) in theaters 'Inorbit and Forum' for 4th March 2017 and the next 2 days (3 days in total)

Parameters 'searchFrom' and 'searchFor' are optional. Defaults to searching for only TODAY.

Once the script finds tickets it will notify you by email with appropriate links to book the tickets. 


## Things to do
- Ability to give price range
- Ability to limit location instead of theaters
- Ability to notify if the seats are available in the top 5 rows.