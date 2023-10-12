include .env

up:
	docker compose up --build -d

run:
	docker compose up

down:
	docker compose down

libdb-shell:
	docker-compose exec library-db psql -d ${LIBRARY_DB_NAME} -U ${LIBRARY_DB_USER} -p ${LIBRARY_DB_PORT}

airflow-init:
	docker compose up airflow-init
