$(document).ready(function(){
	var arr_evedyTit = [
		"成功的第一步就是，<br/>你要敢和别人不一样。",
		"一切成就都缘于一个<br/>梦想和毫无根据的自信。",
		"有三种东西必须尊敬：<br/>坚毅、自尊和仁慈。",
		"要相信自己的眼睛，<br/>不要相信别人的嘴。",
		"如果你面前是阴影，<br/>那你背后肯定有阳光。",
		"让别人快乐是慈悲，<br/>让自己快乐是智慧。",
		"有棱有角的害处是，<br/>别人啃起你来十分方便。"
	]
	var setIntdate = new Date();//现在时刻
	var dateIntenow = parseInt(setIntdate.getHours())
	$(".everdyTit").html(arr_evedyTit[setIntdate.getDay()-1])
	if(dateIntenow>5 && dateIntenow<22){//白天
		var dateIntegralPoint = new Date();//用户登录时刻的下一个整点，也可以设置成某一个固定时刻
		dateIntegralPoint.setHours(22);//设置22点
		dateIntegralPoint.setMinutes(0);
		dateIntegralPoint.setSeconds(0);
		setTimeout(function(){
			$(".eclogite").show();
		},dateIntegralPoint-setIntdate)
	}else if(dateIntenow<5 || dateIntenow>=22){//晚上
		$(".eclogite").show();
	}
})




/*var date = new Date();//现在时刻
 console.log(date)
var dateIntegralPoint = new Date();//用户登录时刻的下一个整点，也可以设置成某一个固定时刻
dateIntegralPoint.setHours(22);//小时数增加1
console.log(dateIntegralPoint.getHours())
dateIntegralPoint.setMinutes(0);
dateIntegralPoint.setSeconds(0);

console.log(dateIntegralPoint-date)
setTimeout("nextIntegralPointAfterLogin();",dateIntegralPoint-date);//用户登录后的下一个整点执行。


function nextIntegralPointAfterLogin(){
         IntegralPointExecute();//在整点执行的函数，在每个整点都调用该函数
setInterval("IntegralPointExecute();",60*60*1000);//一个小时执行一次，那么下一个整点，下下一个整点都会执行
}*/