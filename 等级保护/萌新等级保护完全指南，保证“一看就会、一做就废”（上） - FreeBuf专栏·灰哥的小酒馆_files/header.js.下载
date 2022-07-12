var  _value_tab = '';
$(function() {
	//菜单栏效果
	var _that = '', _show_flag = 0;
    $('.header .header-container .nav .nav-child > li:not(input[data-value])').mouseover(function() {
        $('.header .dropdown-menu').stop().slideUp(50);
    });
    $('.header').mouseout(function() {
        $('.header .dropdown-menu').stop().slideUp(50);
    });
    $(".header .header-container .nav .nav-child > li").hoverDelay({
        hoverDuring: 500,
        hoverEvent: function(){
            $('#'+_value_tab).siblings('.dropdown-menu').stop().slideUp(50);
            $('#'+_value_tab).stop().slideDown(100);
        }
    });
    $('.header .dropdown-menu').mouseover(function() {
        _value_tab = $(this).attr('id');
        _that = this;
        $('.nav-child li[data-value="'+_value_tab+'"]').addClass('hover');
        $(this).stop().slideDown(50);
    }).mouseout(function() {
        $('.nav-child li[data-value="'+_value_tab+'"]').removeClass('hover');
        $(_that).stop().slideUp(50);
    });

    $(".nav-small .nav-child > li").click(function(event){
        var ev = ev || event;
        ev.stopPropagation();

        if($(this).find('.nav-child2').is(":hidden")) {
            _show_flag = 1;
            $(this).find('.nav-child2').slideDown();
            $(this).find('.icon-arrow').addClass('bottom');
        }else {
            _show_flag = 0;
            $(this).find('.nav-child2').slideUp();
            $(this).find('.icon-arrow').removeClass('bottom');
        }
        $(this).siblings().find('.nav-child2').slideUp();
        $(this).siblings().find('.icon-arrow').removeClass('bottom');
    });
    //头部投稿按钮hover状态展开菜单
    $(".btn-publish-child > ul > li").hover(function(){
        $(this).addClass("active");
        $(this).siblings().removeClass("active");
    });

    $(document).click(function(event){
        var ev = ev || event;
        $(".login-after").find(".login-after-child").hide();
    });
    //点击用户信息，出现下拉菜单
    $("#user-info").click(function(event){
        var ev = ev || event;
        ev.stopPropagation();
        $(".login-after").find(".login-after-child").toggle();
    });
    //顶部导航
    $(".nav-small").click(function(){
        $(this).find(".nav-child").slideToggle();
    });
    var that = '';
    $('.header .header-container .nav .nav-child > li').mouseover(function() {
        that = this;
        $(this).find('.dropdown-menu').stop().slideDown(200);
    }).mouseout(function() {
        $(that).find('.dropdown-menu').stop().slideUp(200);
    });
	//头部搜索
	$('.search-form-inner .searchdisplayico').click(function(event) {
        var evt = evt || event;
        evt.stopPropagation();
        $(this).siblings('.search-col').show(350);
    });
    $('.search-form-inner .search-col').click(function(event) {
        var evt = evt || event;
        evt.stopPropagation();
        $('.search-form-inner .search-col').show(350);
    });
    $(document).click(function() {
        $('.search-form-inner .search-col').hide(350);
    });

    if ($(window).width() > 480) {
        $(".main-header").sticky({topSpacing: 0});
    } else {
        $(".main-header nav").removeClass("navbar-fixed-top");
    }
});
//鼠标经过(hover)事件的延时处理
(function($){
    $.fn.hoverDelay = function(options){
        var defaults = {
            hoverDuring: 100,
            outDuring: 100,
            hoverEvent: function(){
                $.noop();
            },
            outEvent: function(){
                $.noop();
            }
        };
        var sets = $.extend(defaults,options || {});
        var hoverTimer, outTimer;
        return $(this).each(function(){
            $(this).hover(function(){
                _value_tab = $(this).attr('data-value');
                clearTimeout(outTimer);
                hoverTimer = setTimeout(sets.hoverEvent, sets.hoverDuring);
            },function(){
                clearTimeout(hoverTimer);
                outTimer = setTimeout(sets.outEvent, sets.outDuring);
            });
        });
    }
})(jQuery);
