;(function($){
    /*
     * 文本域光标操作（选、添、删、取）的jQuery扩展
     */
    $.fn.extend({
        /*
         * 获取光标所在位置
         */
        iGetFieldPos:function(){
            var field=this.get(0);
            if(document.selection){
                //IE
                $(this).focus();
                var sel=document.selection;
                var range=sel.createRange();
                var dupRange=range.duplicate();
                dupRange.moveToElementText(field);
                dupRange.setEndPoint('EndToEnd',range);
                field.selectionStart=dupRange.text.length-range.text.length;
                field.selectionEnd=field.selectionStart+ range.text.length;
            }
            return field.selectionStart;
        },
        /*
         * 选中指定位置内字符 || 设置光标位置
         * --- 从start起选中(含第start个)，到第end结束（不含第end个）
         * --- 若不输入end值，即为设置光标的位置（第start字符后）
         */
        iSelectField:function(start,end){
            var field=this.get(0);
            //end未定义，则为设置光标位置
            if(arguments[1]==undefined){
                end=start;
            }
            if(document.selection){
                //IE
                var range = field.createTextRange();
                range.moveEnd('character',-$(this).val().length);
                range.moveEnd('character',end);
                range.moveStart('character',start);
                range.select();
            }else{
                //非IE
                field.setSelectionRange(start,end);
                $(this).focus();
            }
        },
        /*
         * 选中指定字符串
         */
        iSelectStr:function(str){
            var field=this.get(0);
            var i=$(this).val().indexOf(str);
            i != -1 ? $(this).iSelectField(i,i+str.length) : false;
        },
        /*
         * 在光标之后插入字符串
         */
        iAddField:function(str){
            var field=this.get(0);
            var v=$(this).val();
            var len=$(this).val().length;
            if(document.selection){
                //IE
                $(this).focus()
                document.selection.createRange().text=str;
            }else{
                //非IE
                var selPos=field.selectionStart;
                $(this).val($(this).val().slice(0,field.selectionStart)+str+$(this).val().slice(field.selectionStart,len));
                this.iSelectField(selPos+str.length);
            };
        },
        /*
         * 删除光标前面(-)或者后面(+)的n个字符
         */
        iDelField:function(n){
            var field=this.get(0);
            var pos=$(this).iGetFieldPos();
            var v=$(this).val();
            //大于0则删除后面，小于0则删除前面
            $(this).val(n>0 ? v.slice(0,pos-n)+v.slice(pos) : v.slice(0,pos)+v.slice(pos-n));
            $(this).iSelectField(pos-(n<0 ? 0 : n));
        }
    });
})(jQuery);
jQuery(function() {
	var sWidth = jQuery("#focus").width(); 
	var sWidth_desc = jQuery("#focus_desc").width(); 
	var sWidth_desc = jQuery("#focus_headline").width(); 
	var len = jQuery("#focus ul li").length; 
	var index = 0;
	var picTimer;
	
	
	var btn = "<div class='btnBg'></div><div class='btn'>";
	for(var i=0; i < len; i++) {
		btn += "<span></span>";
	}
	btn += "</div><div class='preNext pre'></div><div class='preNext next'></div>";
	jQuery("#focus").append(btn);
	jQuery("#focus .btnBg").css("opacity",0.5);


	jQuery("#focus .btn span").css("opacity",0.4).mouseover(function() {
		index = jQuery("#focus .btn span").index(this);
		showPics(index);
		showDesc(index);
		showHeadline(index);
	}).eq(0).trigger("mouseover");


	jQuery("#focus .preNext").css("opacity",0.2).hover(function() {
		jQuery(this).stop(true,false).animate({"opacity":"0.5"},300);
	},function() {
		jQuery(this).stop(true,false).animate({"opacity":"0.2"},300);
	});

	
	jQuery("#focus .pre").click(function() {
		index -= 1;
		if(index == -1) {index = len - 1;}
		showPics(index);
		showDesc(index);
		showHeadline(index);
	});

	
	jQuery("#focus .next").click(function() {
		index += 1;
		if(index == len) {index = 0;}
		showPics(index);
		showDesc(index);
		showHeadline(index);
	});

	
	
	
	jQuery("#focus ul").css("width",sWidth * (len));
	jQuery("#focus_desc ul").css("width",sWidth_desc * (len));
	jQuery("#focus_headline ul").css("width",sWidth_desc * (len));
	
	jQuery("#focus").hover(function() {
		clearInterval(picTimer);
	},function() {
		picTimer = setInterval(function() {
			showPics(index);
			showDesc(index);
			showHeadline(index);
			index++;
			if(index == len) {index = 0;}
		},4000); 
	}).trigger("mouseleave");
	
	$('#comment-smiley').click(function() {
        $('#smileys').toggle()
    }); $('#smileys a').click(function() {
        $(this).parent().hide()
    }); 
	function showPics(index) { 
		var nowLeft = -index*sWidth; 
		jQuery("#focus ul").stop(true,false).animate({"left":nowLeft},300); 
		jQuery("#focus .btn span").stop(true,false).animate({"opacity":"0.4"},300).eq(index).stop(true,false).animate({"opacity":"1"},300); 
	}
	function showDesc(index) { 
		var nowLeft_desc = -index*sWidth_desc; 
		jQuery("#focus_desc ul").stop(true,false).animate({"left":nowLeft_desc},300); 
		//alert(nowLeft_desc);
	}
	

	function showHeadline(index) { 
		var nowLeft_headline = -index*sWidth_desc; 
		jQuery("#focus_headline ul").stop(true,false).animate({"left":nowLeft_headline},300); 
	}
	
});


  $(document).on("click","#imageThumb",function(){
    $("#uploadUnit").trigger("click");
    $('#uploadUnit').change(function(){
      $.ajaxFileUpload({url:'https://www.freebuf.com/buf/plugins/ueditor/ueditor/php/imageUp.php?&post_id=', //你处理上传文件的服务端
        secureuri:false,
        fileElementId:'uploadUnit',
        dataType: 'json',
        success: function (data){
          if(data.state=="SUCCESS"){
            var addr = $("#comment").iGetFieldPos();
            var url = data.url;
            if(url.substr(url.length-6,6)=='!small'){
                url = url.substr(0,url.length-6);
            }
            var str = "[img]https://image.3001.net/"+url+"[/img]";
            $("#comment").iAddField(str);
            $("#comment").iSelectField(addr+str.len());
          }else{
          	alert(data.msg);
          }
        }
      })
    });
  })

	function grin(tag) {
    tag = ' ' + tag + ' ';
    myField = document.getElementById('comment');
    document.selection ? (myField.focus(), sel = document.selection.createRange(), sel.text = tag, myField.focus()) : insertTag(tag)
};
function insertTag(tag) {
    myField = document.getElementById('comment');
    myField.selectionStart || myField.selectionStart == '0' ? (startPos = myField.selectionStart, endPos = myField.selectionEnd, cursorPos = startPos, myField.value = myField.value.substring(0, startPos) + tag + myField.value.substring(endPos, myField.value.length), cursorPos += tag.length, myField.focus(), myField.selectionStart = cursorPos, myField.selectionEnd = cursorPos) : (myField.value += tag, myField.focus())
};