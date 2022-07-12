jQuery(document).ready( function($) {
    $('.wpfp-link').live('click', function() {
        dhis = $(this);
        wpfp_do_js( dhis, 1 );
        // for favorite post listing page
        if (dhis.hasClass('remove-parent')) {
            dhis.parent("li").fadeOut();
        }
        return false;
    });
});

function wpfp_do_js( dhis, doAjax ) {
    loadingImg = dhis.prev();
    loadingImg.show();
    beforeImg = dhis.prev().prev();
    beforeImg.hide();
    url = document.location.href.split('#')[0];
    params = dhis.attr('href').replace('?', '') + '&ajax=1';
    action = dhis.attr('href').split('&')[0].split('=')[1];
    if ( doAjax ) {
        jQuery.get(url, params, function(data) {
                if(action=='add'){
                    jQuery(".info-alert").show();
                    jQuery(".info-alert").html("收藏成功");
                    setTimeout(function(){
                        jQuery('.info-alert').hide();
                    },2000);
                }else {
                    jQuery(".info-alert").show();
                    jQuery(".info-alert").html("取消收藏");
                    setTimeout(function(){
                        jQuery('.info-alert').hide();
                    },2000);
                }
                dhis.parent().html(data);
                if(typeof wpfp_after_ajax == 'function') {
                    wpfp_after_ajax( dhis ); // use this like a wp action.
                }
                loadingImg.hide();
            }
        );
    }
}
