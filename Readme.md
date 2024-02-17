# docker build

```sh
docker build -t my-email-app .
```

# docker start

```sh
docker run --env-file .env -v ${PWD}\config.py:/app/config.py -v ${PWD}\ticket_statuses.json:/app/ticket_statuses.json my-email-app
```

# dot env

```ini
TELEGRAM_BOT_TOKEN=
CHAT_ID=

EMAIL_USERNAME=
EMAIL_PASSWORD=
IMAP_URL=imap.yandex.ru
```
