#!/bin/sh

mkdir -p /data/$MINIO_RAW_BUCKET \
    && mkdir -p /data/$MINIO_STAGE_BUCKET \
    && minio server /data
