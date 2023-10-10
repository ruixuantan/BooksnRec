include .env

up:
	docker compose up --build -d

down:
	docker compose down

libdb-shell:
	docker-compose exec library-db psql -d ${LIBRARY_DB_DB} -U ${LIBRARY_DB_USER}

.PHONY: library cassandra
