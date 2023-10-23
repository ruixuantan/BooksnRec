# Books and Rec
A data engineering project.

Suppose we want do some analysis on reader's preferences for books, for a library.
Data we can access are as follows:
* Metadata of books in the library
* Profile of library members
* Loan history of books

## Architecture
![Architecture](./images/architecture_diagram.png)

1. Every time a books is loaned, the library database is updated via the library server's API.
1. On a daily basis, an airflow DAG is triggered to extract the day's loans from the library database and load it into minio.
1. Also, the books' metadata is extracted from a csv file and loaded into minio.
1. All these data are then loaded into clickhouse.
1. Metabase is then used to visualize the data in clickhouse.

## Prerequisites
Versions used at the time of implementation:

* Docker version 24.0.6, build ed223bc
* Docker Compose version v2.22.0-desktop.2
* Python 3.10.1


## Setting up
1. Create a python virtual environment at the root of this project and install the requirements.
    ```sh
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
1. Run `python scripts/library_db_data.py` to create the seed data for the library database.
1. Run `make up` to build and start the docker containers. Use `make run` on subsequent runs. Use `make down` to teardown the containers.
1. Once the containers are up, run `make setup` to setup airflow and seed data.
1. Goto `localhost:8080` to access the airflow UI. The username and password is `airflow`, as in the `.env` file. Under Admin >> Connections, add the Postgres connection with variables specified in the `.env` file.
1. Trigger the airflow DAGs to populate Clickhouse.
1. Metabase can be accessed at `localhost:3000`. Clickhouse variables are specified under the `.env` file, but leave the database as default. Schema of Clickhouse can be found [here](clickhouse/init.sql).
