FROM minio/minio:RELEASE.2023-10-07T15-07-38Z

COPY create_buckets.sh .

RUN chmod +x ./create_buckets.sh

ENTRYPOINT [ "./create_buckets.sh" ]
