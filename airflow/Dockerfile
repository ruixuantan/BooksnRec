FROM apache/airflow:slim-2.7.1-python3.10

COPY requirements.txt .

RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r requirements.txt
