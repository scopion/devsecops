$(function(){

	var $bottomTools = $('.bottom_tools');
	var $qrTools = $('.coin');
	var qrImg = $('.qr_img');
	
	$(window).scroll(function () {
		var scrollHeight = $(document).height();
		var scrollTop = $(window).scrollTop();
		var $windowHeight = $(window).innerHeight();
		scrollTop > 50 ? $("#scrollUp").fadeIn(200).css("display","block") : $("#scrollUp").fadeOut(200);			
		$bottomTools.css("bottom", scrollHeight - scrollTop > $windowHeight ? 40 : $windowHeight + scrollTop + 40 - scrollHeight);
	});
	
	$('#scrollUp').click(function (e) {
		e.preventDefault();
		$('html,body').animate({ scrollTop:0});
		$('.main-header .header').removeClass('op0');
		$('.main-header .header').addClass('op1');
	});
	
	$qrTools.hover(function () {
		qrImg.fadeIn();
	}, function(){
		 qrImg.fadeOut();
	});
	
});

