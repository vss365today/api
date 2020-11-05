# #vss365 today API

> REST API for [#vss365 today](https://vss365today.com)

## Required Configuration

* Flask secret key
* MySQL/MariaDB instance + login keys
* Mailgun API key, authorized domain, and mailing list address
* Twitter API and app keys

## Install

1. Install Python 3.8+ and [Poetry](https://poetry.eustace.io/) 1.0.0+
1. Set missing configuration keys in appropriate `configuration/*.json` files
1. `poetry install`
1. `poetry run flask run`


## Build/Deploy

1. `docker build -f "docker/Dockerfile" -t vss365today-api:latest .`
1. `docker-compose -f "docker/docker-compose.yml" up -d`

## License

2019-2020 Caleb Ely

[MIT](LICENSE)
