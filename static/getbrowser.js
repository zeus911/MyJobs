    function getBrowser(){
        //init variables
        var appVersion = navigator.userAgent.toLowerCase();
        var browserName = "";
        var browserVersion = "";
        var browserMajorVersion = "";
        var browserPlatform = "";
        var browserWidth = 0;
        var browserHeight = 0;
        if(appVersion.indexOf('msie')>0){//IE specific assignments
            browserName = "ie";
            version = appVersion.substring(appVersion.indexOf('msie ')+5,appVersion.length);
            version = version.substring(0,version.indexOf(';'));
            browserVersion = version;
            browserWidth = document.documentElement.clientWidth;
            browserHeight = document.documentElement.clientHeight;
        }else if(appVersion.indexOf('chrome')>0){//chrome specific assignments
            browserName = "chrome";
            version = appVersion.substring(appVersion.indexOf('chrome/')+7,appVersion.length);
            version = version.substring(0,version.indexOf(' '));
            browserVersion = version;
            browserWidth = window.innerWidth;
            browserHeight = window.innerHeight;
        }else if(appVersion.indexOf('applewebkit')>0){//Safari specific assignments
            browserName = "safari";
            version = appVersion.substring(appVersion.indexOf('version/')+8,appVersion.length);
            version = version.substring(0,version.indexOf(' '));
            browserVersion = version;
            browserWidth = window.innerWidth;
            browserHeight = window.innerHeight;
        }else if(appVersion.indexOf('firefox')>0){//FF specific assignments
            browserName = "ff";
            version = appVersion.substring(appVersion.indexOf('firefox/')+8,appVersion.length);
            version = version.substring(0,version.indexOf(' '));
            browserVersion = version;
            browserWidth = window.innerWidth;
            browserHeight = window.innerHeight;
        }
        //set platform - default to windows unelss there is a match otherwise
        if(appVersion.indexOf("os x")>0){
            browserPlatform = "mac";
        }else if(appVersion.indexOf("linux")>0){
            browserPlatform = "linux";
        }else if(appVersion.indexOf("iphone")>0){
            browserPlatform = "iphone";
        }else if(appVersion.indexOf("android")>0){
            browserPlatform = "android";
        }else{
            browserPlatform = "windows";
        }
        browserMajorVersion = version.substring(0,version.indexOf("."));//browser major version
        //create the object
        var browser = new Object();
        //create object properties
        browser.name = browserName;
        browser.version = browserVersion;
        browser.majorVersion = browserMajorVersion;
        browser.width = browserWidth;
        browser.height = browserHeight;
        browser.platform = browserPlatform;
        //return the object to the calling location
        return browser;
    }
