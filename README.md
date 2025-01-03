# Instagram Post Notifier

A Python script that monitors specified Instagram accounts for new posts and sends email notifications when new content is detected.

## Features

- Monitors multiple Instagram accounts for new posts
- Sends email notifications when new posts are found
- Runs on a configurable schedule (default: every 15 minutes)
- Tracks previously seen posts to avoid duplicate notifications
- Handles Instagram login and cookie popups automatically
- Age verification handling for restricted accounts
- Detailed logging

## Requirements

- Python 3.6+
- Playwright
- Schedule
- Loguru
- python-dotenv

## Setup

1. Install dependencies:

```
pip install -r requirements.txt
```

2. Create a .env file with the following variables:

```
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
GMAIL_ADDRESS=your_gmail_address
GMAIL_APP_PASSWORD=your_gmail_app_password
NOTIFICATION_EMAIL=your_notification_email
```

If you don't have a gmail app password, you can create one here: https://myaccount.google.com/apppasswords

3. Run the script:

```
python main.py
```

## Author

**Zack Plauché**
- GitHub: [@zackplauche](https://github.com/zackplauche)
- Website: [zackplauche.com](https://zackplauche.com)
- Twitter: [@zackplauche](https://twitter.com/zackplauche)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.