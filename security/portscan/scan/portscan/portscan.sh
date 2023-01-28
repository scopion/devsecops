/usr/bin/python2.7 /home/work/portscan/scan/portwesens_scan.py > /home/work/portscan/scan/log/portscan.log 2>&1
echo 'portscan dinish'
cd /home/work/portscan/second_scan/sts_sdk_sample_jar
/usr/bin/java -jar port-scan.jar > /home/work/portscan/scan/log/java_second_scan.log 2>&1
echo 'java code end'
/usr/bin/python2.7 /home/work/portscan/notice/everyou.py >  /home/work/portscan/notice/log/ev.log 2>&1
echo 'notice end'
