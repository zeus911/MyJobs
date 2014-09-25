/**
Microsite Javascript Functions
(C) 2013 DirectEmployers Association/DirectEmployers Foundation
**/

$(document).ready(function(){
    /**
    Things to do every time the document is loaded
    **/
    ExternalReferrerCheck(); // check for visitors from external sites
});

function ExternalReferrerCheck(){
    /**
    This function checks to see if there is an external referrer, and then
    does things needed to preserve anything from that external site.
    
    **/    
    var referrer_domain = document.referrer.substr( //strip protocol
        document.referrer.indexOf("http://")+7
        );    
    if(referrer_domain.indexOf("/")>0){ // strip trailing slash, if present
    referrer_domain = referrer_domain.substr(0,
        referrer_domain.lastIndexOf("/")
        );
    }    
    if(referrer_domain.indexOf(":")>0){ // strip port number, if present
        referrer_domain = referrer_domain.substr(0,
            referrer_domain.lastIndexOf(":")
            );
    }
    // For ext. referrers check for and store external google analytics
    if(referrer_domain!=document.location.hostname)
        CheckForExternalCampaign();

}

function CheckForExternalCampaign(){
    the_url = document.location+""; // convert the url to a string
    cookie = setExternalCampaignCookie(the_url);
}

function setExternalCampaignCookie(the_url){
    /**
    This function checks the incoming url for Google Analytics query
    paramaters. If it finds them, it stores them in a client side cookie
    for use on the apply link, thus passing them on to the ATS.

    Inputs:
        :the_url:   A string containg the sites full URL. It is either derived
                    from document.location, or passed as literal by qUnit.
    Return:
        :remainder: The remains of the query string once google analtics
                    and internal query string params have been removed.
 
    **/
    if(the_url.indexOf("?")<0)  //abort the cookie setting if there is no QS
        return false;

    the_url = the_url.substring(the_url.indexOf("?")+1);  // only need the QS
    utm_string = {};
    query_string = [];
    pairs = {};
    // Look for the key prefix "utm_" and use it as the boolean for 
    // detecting external campaigns. If true,build out the query string 
    // as an array
    
    pairs = the_url.split("&");
    // establish which quary parameters to ignore (usually internal)
    ignore_list = ['location','q'];
    for(i=0;i<pairs.length;i++){
        pair = pairs[i].split("=");
        if(pair[0].indexOf("utm_")>=0){
            utm_string[""+pair[0]]=pair[1];
        }else if($.inArray(pair[0],ignore_list)==-1){
            // for cookie values that are not related to google analytics,
            // and are not intentionally being ignored, store them so that
            // we can pass them on to the ATS.
            query_string.push(pair[0]+":eq:"+pair[1]);
        }        
    }
    cookie_handler = new CookieHandler();  // instatiate a cookie handler object

    // set the cookies for each key pair
    if(utm_string.utm_campaign)
        cookie_handler.setCookie("external_utm_campaign", utm_string.utm_campaign);

    if(utm_string.utm_medium)
        cookie_handler.setCookie("external_utm_medium", utm_string.utm_medium);

    if(utm_string.utm_content)
        cookie_handler.setCookie("external_utm_content", utm_string.utm_content);

    if(utm_string.utm_source)
        cookie_handler.setCookie("external_utm_source", utm_string.utm_source);

    if(utm_string.utm_term)
        cookie_handler.setCookie("external_utm_term", utm_string.utm_term);

    var remainder = "";
    for(i=0;i<query_string.length;i++)
        remainder += "&"+query_string[i];

    if(remainder != "")
        cookie_handler.setCookie("external_pairs", remainder);

    return remainder
}


function RetrieveExternalCampaignCookie(){
    /**
    This function retrieves external campaign cookie values and then calls
    RebuildApplyURL to replace the google analytics campaign keys on the 
    apply link.
    **/
    cookie_handler= new CookieHandler();
    cookie_vals = {};
    cookie_vals.campaign = cookie_handler.getCookie("external_utm_campaign");
    if(cookie_vals.campaign != null){
        cookie_vals.medium = cookie_handler.getCookie("external_utm_medium");
        cookie_vals.content = cookie_handler.getCookie("external_utm_content");
        cookie_vals.source = cookie_handler.getCookie("external_utm_source");
        cookie_vals.term = cookie_handler.getCookie("external_utm_term");
    }
    cookie_vals.pairs = cookie_handler.getCookie("external_pairs");
    RebuildApplyURL(cookie_vals);
}

function RebuildApplyURL(cookie_vals){
    /**
    This function rewrites the query string on the apply URL, replacing local
    google analytics key-name pairs with the external values stored in
    a client side cookie.
    **/
    apply_link = $("#direct_applyButton a");
    apply_href = apply_link.attr("href");
    if(apply_href.indexOf("utm_campaign=")>0){
        // If there are campaign pairs defined, replace the values where ever 
        // they are in the query string.
        apply_link_parts = apply_link.attr("href").split("?");
        apply_link_query_strings = apply_link_parts[1].split("&");
        
        for(i=0;i<apply_link_query_strings.length;i++){
            pair=apply_link_query_strings[i].split("=");
            switch (pair[0]){
                case "utm_campaign":
                    pair[1]=cookie_vals.campaign;
                    break;
                case "utm_medium":
                    pair[1]=cookie_vals.medium;
                    break;
                case "utm_content":
                    pair[1]=cookie_vals.content;
                    break;
                case "utm_source":
                    pair[1]=cookie_vals.source;
                    break;
                case "utm_term":
                    pair[1]=cookie_vals.term;
                    break;
            }
            apply_link_query_strings[i]=pair[0]+"="+pair[1];
        }
        querystring = apply_link_query_strings.join("&");
        querystring += cookie_vals.pairs;
        apply_link_parts[1] = querystring;
        apply_href = apply_link_parts.join("?");
    }else{
        // Otherwise just append them to the end
        campaign_string = "";
        if(cookie_vals.campaign != null && cookie_vals.campaign.length>0)
            campaign_string += "utm_campaign="+cookie_vals.campaign;

        if(cookie_vals.medium != null && cookie_vals.medium.length>0)
            campaign_string += "&utm_medium="+cookie_vals.medium;

        if(cookie_vals.content != null && cookie_vals.content.length>0)
            campaign_string += "&utm_content="+cookie_vals.content;

        if(cookie_vals.source != null && cookie_vals.source.length>0)
            campaign_string += "&utm_source="+cookie_vals.source;

        if(cookie_vals.term != null && cookie_vals.term.length>0)
            campaign_string += "&utm_term="+cookie_vals.term;

        // preserve any non-matched query string values
        if(cookie_vals.pairs!=null&&cookie_vals.pairs!="")
            campaign_string += cookie_vals.pairs.replace(/:eq:/g,"=");

        /**
        add the preserved strings to aby existing querys trings present on
        the apply link. Also, because this is not the only place params are
        added to the apply link (views.py does in some palces), run a dedupe
        method on the query string to prevent duplicate n/v pairs.
        **/
        if(campaign_string!=''){
            if (apply_href.indexOf("?")>-1){
                campaign_string = apply_href.split("?")[1]+campaign_string;
                campaign_string = dedupe_string(campaign_string, "&");
                apply_href = apply_href.split("?")[0]+"?"+campaign_string;
            }else{
                campaign_string = dedupe_string(campaign_string, "&");
                apply_href = apply_href+"?"+campaign_string;
            }
        }
    }
    apply_href=apply_href.replace("?&","?");
    apply_href=apply_href.replace("&&","&");
    apply_link.attr("href",apply_href);
    // now grab the bottom link and apply the same value
    bottom_apply_link = $("#direct_applyButtonBottom a");
    bottom_apply_link.attr("href",apply_href);
}
function dedupe_string(string,delimiter){
    /***
    Splits a string object, dedupes it, and returns a string. Intended use is
    on query strings, but could be used for other strings as well.
    
    Inputs:
    string:     delimited string object to dedupe
    delimiter:  delimiter string sequence to split and rejoin on  
    ***/
    var list = string.split(delimiter);
    var set  = {};
    for (var i = 0; i < list.length; i++){
        set[list[i]] = true;
    }
    list = [];
    for (var node in set){
        list.push(node);
    }
    return list.join(delimiter);
}
function CookieHandler() {
    /**
    This function uses cookies to preserve data in a client side cookie.
    It includes te following methods:
    
    setCookie
    method for setting the cookie name, value, and expiration.
    
    getCookie
    method for retreiving a cookie valu by name.
    
    deleteCookie
    method for removing a cookie by name.
    
    Based on "Javascript Cookies" code from http://www.webtoolkit.info/
    **/
 
    this.setCookie = function (name, value, seconds) {

        if (typeof(seconds) != 'undefined') {
            var date = new Date();
            date.setTime(date.getTime() + (seconds*1000));
            var expires = "; expires=" + date.toGMTString();
        }
        else {
            var expires = "";
        }

        document.cookie = name+"="+value+expires+"; path=/";
    };

    this.getCookie = function (key_name) {
        var cookie_array = document.cookie.split(';');
        for(var i=0;i < cookie_array.length;i++) {
            var cookie = cookie_array[i];
            local_cookie={};
            stored_key=cookie.split("=")[0];
            stored_value=cookie.split("=")[1];
            if(stored_key.indexOf(" ")==0){
                stored_key=stored_key.substring(1);
            }
            local_cookie["key"]=stored_key;
            if(local_cookie.key==key_name){
                return stored_value;
            }
        }
        return null;
    };

    this.deleteCookie = function (name) {
        this.setCookie(name, "", -1);
    };
 
    return this;
}
function getBrowser(){
    /**
    This function returns an object containing useful information about the
    visitors browser.
    
    **/
    //init variables
    var uAgent=navigator.userAgent.toLowerCase();
    var uAgentLen = uAgent.length;
    var browserName="";
    var browserVersion="";
    var browserMajorVersion="";
    var browserPlatform="";
    var browserWidth=0;
    var browserHeight=0;
    if(uAgent.indexOf('msie')>0){//IE specific assignments
        browserName="ie";
        version=uAgent.substring(uAgent.indexOf('msie ')+5,uAgentLen);
        version=version.substring(0,version.indexOf(';'));
        browserVersion=version;
        browserWidth=document.documentElement.clientWidth;
        browserHeight=document.documentElement.clientHeight;
    }else if(uAgent.indexOf('chrome')>0){//chrome specific assignments
        browserName="chrome";
        version=uAgent.substring(uAgent.indexOf('chrome/')+7,uAgentLen);
        version=version.substring(0,version.indexOf(' '));
        browserVersion=version;
        browserWidth=window.innerWidth;
        browserHeight=window.innerHeight;
    }else if(uAgent.indexOf('applewebkit')>0){//Safari specific assignments
        browserName="safari";
        version=uAgent.substring(uAgent.indexOf('version/')+8,uAgentLen);
        version=version.substring(0,version.indexOf(' '));
        browserVersion=version;
        browserWidth=window.innerWidth;
        browserHeight=window.innerHeight;
    }else if(uAgent.indexOf('firefox')>0){//FF specific assignments
        browserName="ff";
        version=uAgent.substring(uAgent.indexOf('firefox/')+8,uAgentLen);
        version=version.substring(0,version.indexOf(' '));
        browserVersion=version;
        browserWidth=window.innerWidth;
        browserHeight=window.innerHeight;
    }
    //set platform - default to windows unelss there is a match otherwise
    if(uAgent.indexOf("os x")>0){
        browserPlatform="mac";
    }else if(uAgent.indexOf("linux")>0){
        browserPlatform="linux";
    }else if(uAgent.indexOf("iphone")>0){
        browserPlatform="iphone";
    }else if(uAgent.indexOf("android")>0){
        browserPlatform="android";
    }else{
        browserPlatform="windows";
    }
    browserMajorVersion=version.substring(0,version.indexOf("."));
    //create the object
    var browser={};
    //create object properties
    browser.name=browserName;
    browser.version=browserVersion;
    browser.majorVersion=browserMajorVersion;
    browser.width=browserWidth;
    browser.height=browserHeight;
    browser.platform=browserPlatform;
    //return the object to the calling location
    return browser;
}
function validate_email(email){
    /***
    Validate a string as a valid email format.
    Inputs:
        :email: string fo the email to test
    Returns:
        true|false
    ***/
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}
