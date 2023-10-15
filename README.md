# Books and Rec
A data engineering project.

## Architecture
![Architecture](./images/architecture_diagram.png)

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
