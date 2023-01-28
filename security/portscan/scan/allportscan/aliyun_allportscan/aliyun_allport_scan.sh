/usr/bin/python /home/renhongwei/allportscan/aliyun_host_find.py > /home/renhongwei/allportscan/aliyun_host_find.log 2>&1
echo 'asset get end'
/usr/bin/masscan -iL /home/data/allportscan/all_port_scan_ip_list.txt -p1-65535 --wait 3 --max-rate 5000 -oJ /home/data/allportscan/all_port_scan_jresult_know_$(date "+%Y-%m-%d").json
echo 'port scan end'
/usr/bin/python /home/data/allportscan/allport_scan_aliyun.py > /home/data/allportscan/allport_scan_aliyun.log 2>&1
echo 'allport end'
