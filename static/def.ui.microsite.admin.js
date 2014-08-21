$(document).bind('click', function(){
    field_length_check();
});

function field_length_check(){
    /**
    Initiation point for field length checks. Assigned event triggers to matched
    fields.
    
    Inputs:
        None
            
    **/
    field_set=[]; //holder or matching fields 
    $("p.help").each(function(){
        //check each form element and store it if it is a match
        field = check_text_max_length($(this));        
        if(field){
            field_set.push(field);
        }
    });
    //assign a keyup event listener to matched fields.
    for(i=0;i<field_set.length;i++){
        $("#"+field_set[i]).keyup(function(){
            check_text_max_length($(this).parent().children(".help"))
        });
    }
}
function check_text_max_length(obj){
    /**
    Use the help text of an admin field as key to display X of Y Max characters.
    
    Inputs:
        :obj:   p.help instanc
    
    Returns:
        :target:    id of matched form field element OR false.
    
    **/
    help_text_raw = $(obj).html(); // preserve the help text
    if(help_text_raw.indexOf(" of ")>-1){ //reset if the help text is modified
        help_text_raw = help_text_raw.substr(help_text_raw.indexOf(" of ")+4);
    }
    help_text = help_text_raw.toLowerCase(); // lower case for comparison
    if( help_text.indexOf("max") > -1 &&
        help_text.indexOf("char") > -1   ){
        max_length = help_text.match(/[0-9]+/); // assumes int is field max
        target = $(obj).parent().children("label").attr("for");
        text_count = $("#"+target).val().length;
        if(text_count/max_length>1){
            mod = " style='color: #F00'";
        }else if(text_count/max_length>.8){
            mod = " style='color: #F90'";
        }else{
            mod="";
        }
        count_text = "<b"+mod+">"+text_count+"</b>";
        $(obj).html(count_text+" of "+help_text_raw);
    }else{
        target =  false;
    }
    return(target);
}
