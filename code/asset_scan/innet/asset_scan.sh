/usr/bin/nmap -sP -n 10.20.0.0/16 -oN /home/renhongwei/portscan/ip_list.txt
echo 'nmap host scan end'
/usr/bin/python2.7 /home/renhongwei/portscan/ip_find.py > /home/renhongwei/portscan/ip_find.log
echo 'ip end'
