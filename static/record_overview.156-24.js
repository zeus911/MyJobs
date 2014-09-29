/*
onpopstate happens when a user goes back in history
function gathers event state data that was pushed from pushState
and builds the page back to which it was.
*/
window.onpopstate = function(event) {
    fill_in_history_state(event.state);
    send_filter(event.state);
};


// isIE is used a lot, so lets make it a variable!
isIE = isIE();

// indexOf fix for IE8
if (typeof(isIE) == "number" && isIE < 9) {
    if (!Array.prototype.indexOf)
    {
      Array.prototype.indexOf = function(elt /*, from*/)
      {
        var len = this.length >>> 0;

        var from = Number(arguments[1]) || 0;
        from = (from < 0)
             ? Math.ceil(from)
             : Math.floor(from);
        if (from < 0)
          from += len;

        for (; from < len; from++)
        {
          if (from in this &&
              this[from] === elt)
            return from;
        }
        return -1;
      };
    }
}


$(document).ready(function() {
    /*
    If someone loads the page with request.GET info
    (not from ajax) fill page with info
    */
    if(location.search) show_selected();

    $(".sidebar :input:has(option)").on("change", function() {
        run_ajax();
    });

    /*
    Fancy pushState next and previous buttons for everyone but IE8 and IE9
     */
    if (typeof(isIE) == "number" && isIE > 9 || typeof(isIE) == 'boolean' && isIE == false) {
        $("body").on("click", "#next_page", function(e) {
            e.preventDefault();
            var data = build_data();
            data.page = get_page(data);
            data.page++;
            update_search_url(data);
            send_filter(data);
        });

        $("body").on("click", "#previous_page", function(e) {
            e.preventDefault();
            var data = build_data();
            data.page = get_page(data);
            data.page--;
            update_search_url(data);
            send_filter(data);
        });
    }

    $("#record-download").on("click", function() {
        $(this).children().toggleClass("show-drop");
    });

    $("#candidate-time-filter").on("click", function() {
        $(this).children().toggleClass("show-drop");
    });

    $("#date-range-list li:not(#date-drop)").on("click", function(e) {
        e.stopPropagation();
    });

    $("#date-drop").on("click", function() {

    });
});


/*
 Checks to see if browser is IE.
 If it is then get version.
*/
function isIE() {
    var myNav = navigator.userAgent.toLowerCase();
    return (myNav.indexOf('msie') != -1) ? parseInt(myNav.split('msie')[1]) : false;
}


/*
For DRY
Build data, update the URL (pushState or refresh page), run ajax if not IE 9 or <
 */
function run_ajax() {
    var data = build_data();
    update_search_url(data);
    if (typeof(isIE) == "number" && isIE > 9 || typeof(isIE) == 'boolean' && isIE == false) {
        send_filter(data);
    }
}


// get page
function get_page(data) {
    var page = parseInt(getParameterByName("page"));
    if(page) {
        return data.page = parseInt(getParameterByName("page"))
    } else {
        return data.page = 1;
    }
}


/*
Gets the param from URL
:name:  Is the key
 */
function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}


/*
Make the page look like it did location.history.go(-1) ago.

Input:
:data:  is the event.state from window.onpopstate
 */
function fill_in_history_state(data){
    if(!data){
        $("#record_contact option[value='all']").attr("selected", "selected");
        $("#record_contact_type option[value='all']").attr("selected", "selected");
        return false
    }
    if(typeof(data.contact) != "undefined")
        $("#record_contact option[value='"+ data.contact +"']").attr("selected", "selected");
    else
        $("#record_contact option[value='all']").attr("selected", "selected");
    if(typeof(data.contact_type) != "undefined")
        $("#record_contact_type option[value='"+ data.contact_type +"']").attr("selected", "selected");
    else
        $("#record_contact_type option[value='all']").attr("selected", "selected");

    return false
}


/*
build data object from all sources on the page.
 */
function build_data() {
    var data = {};

    data['partner'] = $(".sidebar #p-id").val();

    $(".sidebar :input:has(option)").each(function() {
        if($(this).val() != 'all') {
            var data_key = $(this).prev('label').html().replace(":", "").replace(" ","_").toLowerCase();
            data[data_key] = $(this).val();
        }
    });

    return data
}


/*
Builds URL from data that is usually built from build_data()

Uses new HTML5 history API or if IE8, 9 reloads the page.
 */
function update_search_url(data) {
    // IE8 hates me
    if (!Object.keys) {
      Object.keys = function(obj) {
        var keys = [];

        for (var i in obj) {
          if (obj.hasOwnProperty(i)) {
            keys.push(i);
          }
        }

        return keys;
      };
    }
    var search_url = "?",
        data_keys = Object.keys(data);
    for(var i = 0; i < data_keys.length; i++) {
        var key = data_keys[i],
            value = data[key];
        if(typeof(value) == "object"){
            for(var j = 0; j < value.length; j++){
                if(i != 0 || j != 0) search_url += "&";
                search_url += key + "=" + value[j];
            }
        } else {
            if(i != 0) search_url += "&";
            search_url += key + "=" + value;
        }
    }

    if (typeof(isIE) == "number" && isIE > 9 || typeof(isIE) == 'boolean' && isIE == false) {
        history.pushState(data, "filter", search_url);
    } else {
        location.search = search_url;
    }
}


function send_filter(data_to_send) {
    if(data_to_send == null) data_to_send = {partner: $(".sidebar #p-id").val()};
    $.ajaxSettings.traditional = true;
    $.ajax({
        type: 'GET',
        url: location.pathname,
        data: data_to_send,
        success: function(data) {
            $(".span8").html(data);
        }
    });
}


/*
If someone loads the page with request.GET info (not from ajax) fill page with info
*/
function show_selected() {
    var q = location.search,
        params = q.replace("?", "").split("&");
    if (typeof(isIE) == "number" && isIE < 9) {
        if(q === "?") return false;
    }
    for(var i = 0; i < params.length; i++) {
        var s = params[i].split("="),
            key = s[0];
        var value = s[1].replace("%20", "-");
        value = value.replace(" ", "-");

        if(key == "contact") {
            $("select#record_contact option").each(function(){
                if($(this).val() == value)
                    $(this).attr("selected", "selected");
            });
        }
        if(key == "contact_type") {
            $("select#record_contact_type option").each(function(){
                if($(this).val() == value)
                    $(this).attr("selected", "selected");
            });
        }
    }
}