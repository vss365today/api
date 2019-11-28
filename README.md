# #vss365 today API

> REST API for [#vss365 today](https://vss365today.com)

## Required Configuration Keys

* Flask secret key
* JWT secret key

## Install

1. Install Python 3.8+ and [Poetry](https://poetry.eustace.io/) 1.0.0b6+
1. `mv oss.env .env`
1. Set missing configuration keys
1. `poetry install`
1. `poetry run flask run`


## Build/Deploy

1. `docker build -f "docker/Dockerfile" -t vss365today-api:latest .`
1. `docker-compose -f "docker/docker-compose.yml" up -d`

## License

2019-2020 Caleb Ely

[MIT](LICENSE)
