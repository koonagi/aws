#!/bin/bash

if [ $# != 4 ]; then
        echo "+++ Argument Error +++"
        echo Usage: ./s3select_cli.sh "<s3_bucket_name>"  "<s3_Object_key>" "<file_format Parquet|CSV>" "<SQL>" 
        echo Example: ./s3select_cli.sh nyc-tlc misc/uber_nyc_data.csv CSV "select * from s3object limit 10"
        exit 1
fi

BucketName=$1
KeyName=$2
Format=$3
SQL=$4

aws s3api select-object-content --bucket ${BucketName} --key "${KeyName}" --expression "${SQL}" --expression-type 'SQL'  --input-serialization '{"'${Format}'": {}, "CompressionType": "NONE"}'  --output-serialization '{"CSV": {}}' "tmp_output.csv" && cat tmp_output.csv && rm tmp_output.csv
