include .env

up:
	docker compose up --build -d

run:
	docker compose up

down:
	docker compose down

libdb-shell:
	docker-compose exec library-db psql -d ${LIBRARY_DB_NAME} -U ${LIBRARY_DB_USER} -p ${LIBRARY_DB_PORT}

clickhouse-shell:
	docker-compose exec clickhouse clickhouse-client

airflow-init:
	docker compose up airflow-init

service-setup:
	python scripts/transfer_dataset.py
	python scripts/gen_library_loans.py

setup: service-setup airflow-init
