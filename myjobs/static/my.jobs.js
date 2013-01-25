/******
My.jobs Share window functions. Assigns click events and builds share window. 
*******/
$('#twitter').live('click',function() {        
    q=location.href;
    share_url = '/auth/twitter/?&url='+encodeURIComponent(q);
    openShareWindow(share_url,"Twitter");
});
$('#facebook').live('click',function() {
    q=location.href;
    share_url = '/auth/facebook/?&url='+encodeURIComponent(q);
    openShareWindow(share_url,"Twitter");
});
$('#linkedin').live('click',function() {
    q=location.href;
    share_url = '/auth/linkedin/?&url='+encodeURIComponent(q);
    openShareWindow(share_url,"LinkedIn");
});
$(document).ready(function(){
    /*Explicit control of main menu, primarily for mobile but also provides
    non hover and cover option if that becomes an issue.*/
    $("#nav .main-nav").click(function(){
        $("#nav").toggleClass("active");
        return false;
    });
    $("#pop-menu").mouseleave(function(){
        $("#nav").removeClass("active");
    });
});
function openShareWindow(url,name){
    /*
    Opens a new window using OAuth to share content.
    
    Inputs:
        :url:   The share url to use
        :name:  The name of the social network
    
    Returns:
        None - opens a new window.
    
    */
    title = 'Share this on '+name;
    atts = 'toolbar=no,width=568,height=360';
    share_window = window.open(url, title,atts);
}
