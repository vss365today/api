# #vss365 today API

> REST API for [#vss365 today](https://vss365today.com)

## Required Configuration

- Flask secret key (`SECRET_KEY_API`)
- MariaDB instance + login keys (`DB_USERNAME`, `DB_PASSWORD`, `DB_HOST`, `DB_DBNAME`)
- Mailgun API key authorized domain and mailing list address (`MG_API_KEY`, `MG_DOMAIN`, `MG_MAILING_LIST_ADDR`)
- Twitter API v1 consumer key and consumer secret, read-only (`TWITTER_APP_KEY`, `TWITTER_APP_SECRET`)

## Install

1. Install Python 3.9+ and [Poetry](https://poetry.eustace.io/) 1.1.0+
1. Set missing configuration keys in appropriate `configuration/*.json` files
1. Run `poetry install`
1. Launch the app using the provided VS Code launch configuration

Note: when running in development mode, all email sending will be disabled and
all email-related operations will pretend that they suceeded.


## Build

1. `docker build -t vss365today-api:latest .`

## License

2019-2021 Caleb

[MIT](LICENSE)
