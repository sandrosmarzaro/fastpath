# FastPath
>
> API to calculate the fast delivery path.

## Overview

This a async RESTful API with endpoints, that's receive a coordinate of pickup
point and a list of dropoff coordinates from a user, and integrate call to
backend service to build a cost matrix, and pass to optimization library for
finally improve the route and return a list of coordinates ordered by reduce
path.

## Why?

This a mixed overengenieering side project with trade-offs to practice my
skills mainly in technologies used in this repository ~~(and help-me found a job)~~.
Instead a create many small repos for each idea, I resolved focus in one big
project, and increase the size them bit by bit _(quality is better than quantity)_.
The insight of API is from my [undergraduate thesis](https://repositorio.ifes.edu.br/items/2c7b3208-4d14-4238-89b6-d173e5270498) about metaheuristics.

## Tech Stack

### Standalone Services

They are the main jobs running in [Docker](https://www.docker.com/) containers
orchestrated by [Compose](https://docs.docker.com/compose/) at the moment.

- [FastAPI](https://fastapi.tiangolo.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)
- [OSRM](https://project-osrm.org/)
- [OTel LGTM](https://grafana.com/docs/opentelemetry/docker-lgtm/)

## How To Run

### In Developing Environments

1. Download repository in your machine.

    ```bash
    git clone git@github.com:sandrosmarzaro/fastpath.git
    ```

2. Create & configure environment variables in [.devcontainer](.devcontainer/)
based [.env.example](.env.example) in root directory.

    ```bash
    cp .env .devcontainer/.env
    ```

3. Download [Open Street Map](https://www.openstreetmap.org/#map=5/-15.13/-53.19) of location that do want to use. In this case, I
using [Brazil](https://download.geofabrik.de/south-america/brazil.html), and put in [osrm_data](osrm_data/) folder.

4. Following OSRM documentation, extract the map using his container.

    ```bash
    docker run -t -v "${PWD}/osrm_data:/data" osrm/osrm-backend:v5.25.0 osrm-extract -p /opt/car.lua /data/brazil-251129.osm.pbf
    docker run -t -v "${PWD}/osrm_data:/data" osrm/osrm-backend:v5.25.0 osrm-partition /data/brazil-251129.osrm;
    docker run -t -v "${PWD}/osrm_data:/data" osrm/osrm-backend:v5.25.0 osrm-customize /data/brazil-251129.osrm;
    ```

5. Now, we able to build and compile the API and all services using Docker too.

    ```bash
    docker compose build && docker compose up
    ```

### Special Links

When API is running there are some links to access your resources.

| Resource | Link                                                  |
|----------|-------------------------------------------------------|
| API      | <https://localhost:8000>                                |
| Grafana  | <https://localhost:3000>                                |
| Docs     | <https://localhost:8000/api/v1/docs/>                   |
| Coverage | <https://app.codecov.io/github/sandrosmarzaro/fastpath> |
