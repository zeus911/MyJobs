/**
This document handles user interaction event tracking for DotJobs Microsites.
(C) 2012 DirectEmployers Association
**/
$(document).ready(function(){
    // track when a user opens a hotspot
    $(".hotspotButton").each(function(){
        catStr = "billboard homepage";
        actionStr_enter = "hotspot activation";
        labelStr = $(this).attr("data-name");
        valueStr = $(this).attr("data-url");
        assignEvent('mouseenter',$(this),catStr,actionStr_enter,labelStr,valueStr);
    })
    // track when a user leaves/closes a hotspot
    $(".hotspotWrapper").each(function(){
        catStr = "billboard homepage";
        actionStr_leave = "hotspot deactivation";
        labelStr = $(this).attr("data-name");
        valueStr = $(this).attr("data-url");
        assignEvent('mouseleave',$(this),catStr,actionStr_leave,labelStr,valueStr);        
    })
    // track when a user clicks on a hotspot
    $(".hotspotDetail").each(function(){
        catStr = "billboard homepage";
        actionStr_click = "hotspot click";
        labelStr = $(this).attr("data-name");
        valueStr = $(this).attr("data-url");
        assignEvent('click',$(this),catStr,actionStr_click,labelStr,valueStr);
    })
    //track the user's interaction with the billboard carousel controls
    $("#direct_dotJobsImageControls .imageControl").each(function(){
        catStr = "billboard homepage";
        actionStr_click = "billboard carousel click";
        actionStr_mouseenter = "billboard carousel mouse enter";
        actionStr_mouseleave = "billboard carousel mouse leave";
        labelStr = "image control";
        if($(this).attr('id').indexOf("_prev")){
            valueStr = "previous";
        }else if($(this).attr('id').indexOf("_next")){
            valueStr = "next";
        }else{
            valueStr = $(this).html();
        }
        assignEvent('click',$(this),catStr,actionStr_click,labelStr,valueStr);
        assignEvent('mouseenter',$(this),catStr,actionStr_mouseenter,labelStr,valueStr);
        assignEvent('mouseleave',$(this),catStr,actionStr_mouseleave,labelStr,valueStr);
    })
     
    
})
function assignEvent(event,object,catStr,actionStr,labelStr,valStr){
    /**
    Assigns a tracking event to a given dom object.
    
    Inputs:
        :event:     the trigger event to track (ie 'click')
        :object:    the object to which the event should be bound
        :catStr:    analytics category
        :actionStr: action description
        :labelStr:  action label
        :valStr:    action value
    
    **/
    $(object).bind(event,{
        category: catStr, 
        action: actionStr, 
        label: labelStr, 
        value: valStr
        },
        trackEvent);
}
function trackEvent(e){    
    /**
    Pushes a tracking event to the ga (Google Analytics object).
    
    Inputs:
        :e: The event object
    
    **/
    category = e.data.category;
    action = e.data.action;
    label = e.data.label;
    value = e.data.value;
    ga('send', category, action, label, value);
}
