#! /bin/bash
/usr/bin/python /root/allport_res_update.py > /root/allport_res_update.log 2>&1
echo 'python end'
set -ex
cd /root/sts_sdk_sample_jar/
/root/jdk1.8.0_161/bin/java -jar sts-sdk-sample.jar > java_scan.log 2>&1
echo 'java end'
