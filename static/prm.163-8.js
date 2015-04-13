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

    /*
    Fancy pushState next and previous buttons for everyone
    but IE8 and IE9
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

    // Removes span and adds input ready to be edited
    $("body").on("click", "#per-page span", function() {
        $(this).remove();
        var value = $(this).text();
        var input = document.createElement("input");
        input.setAttribute("id", "per-page-input");
        input.setAttribute("type", "text");
        input.setAttribute("value", value);
        var pp = document.getElementById("per-page");
        pp.insertBefore(input, pp.firstChild);
        $("#per-page-input").focus().select();
    });

    // New input from clicking #per-page span if user hits enter remove this
    $("body").on("keypress", "#per-page-input", function(e) {
        if(e.which == 13) {
            $(this).hide();
            if($(this).is(":focus")) $(this).focusout();
        }
    });

    /*
    When the user stops focusing or if this input is removed
    add back the span to #per-page with new info
    */
    $("body").one("blur", "#per-page-input", function() {
        if($(this).is(":visible")) $(this).hide();
        if(!$("#per-page span").length > 0) {
            var value = $(this).val();
            var span = document.createElement("span");
            var span_node = document.createTextNode(value);
            span.appendChild(span_node);
            var pp = document.getElementById("per-page");
            pp.insertBefore(span, pp.firstChild);
            run_ajax();
        }
    });

    // switch sort status and run ajax
    $("body").on("click", ".sort-by", function() {
        if($(this).hasClass("active")) {
            if($(this).hasClass("ascending")) {
                $(this).removeClass("ascending").addClass("descending");
            } else {
                $(this).removeClass("descending").addClass("ascending");
            }
        } else {
            $(".sort-by.active").removeClass("active descending ascending");
            // clicking sorts ascending by default unless sorting activity
            if($(this).text() == 'Activity'){
                $(this).addClass("active descending");
            } else {
                $(this).addClass("active ascending");
            }
        }
        run_ajax();
    });

    /*
    Saves both partner forms; init form and new/edit partner form

    :e: "Save" button on profile unit forms
     */
    $('#init-partner-save').on("click", function(e) {
        // interrupts default functionality of the button with code below
        e.preventDefault();

        var form = $('#partner-form');

        var serialized_data = form.serialize();

        var get_data = window.location.search;
        if (get_data.length) {
            get_data = '&' + get_data.substr(1);
        }
        serialized_data += get_data;

        var company_id = $('[name=company_id]').val();

        $.ajax({
            type: 'POST',
            url: '/prm/view/save',
            data: serialized_data,
            success: function(data, status) {
                if (data == ''){
                    if (status != 'prevent-redirect') {
                        window.location = '/prm/view';
                    }
                } else {
                    // form was a json-encoded list of errors and error messages
                    var json = jQuery.parseJSON(data);

                    // remove color from labels of current errors
                    $('[class*=required]').parent().prev().removeClass('error-text');

                    // remove current errors
                    $('[class*=required]').children().unwrap();

                    if($.browser.msie){
                        $('[class*=msieError]').remove()
                    }

                    for (var index in json) {
                        var $error = $('[name="'+index+'"]');
                        var $labelOfError = $error.parent().prev();

                        // insert new errors after the relevant inputs
                        $error.wrap('<div class="required" />');
                        $error.attr("placeholder",json[index][0]);
                        $error.val('');
                        $labelOfError.addClass('error-text');
                    }
                }
            }
        });
    });

    $(".datepicker").on("click", function(e) {
        $(this).pickadate({
            format: "mm/dd/yyyy",
            selectYears: true,
            selectMonths: true,
            today: false,
            clear: false,
            close: false,
            onOpen: function() {
                if(this.get("id") === "activity-start-date"){
                    var end_date = $("#activity-end-date").val();
                    this.set("max", new Date(end_date || new Date()));
                } else if(this.get("id") === "activity-end-date"){
                    var start_date = $("#activity-start-date").val();
                    this.set("min", new Date(start_date || new Date(0)))
                }
            },
            onClose: function() {
                run_ajax();
            }
        });
    });

    $('#item-save, #contact-save').on("click", function(e) {
        // interrupts default functionality of the button with code below
        e.preventDefault();

        var is_c_form_there = $('#contact-form').length;
        if (is_c_form_there > 0) {
            var form = $('#contact-form');
        }
        else {
            var form = $('#partner-form');
        }

        var serialized_data = form.serialize();

        var get_data = window.location.search;
        if (get_data.length) {
            get_data = '&' + get_data.substr(1);
        }
        serialized_data += get_data + '&ct=' + $('[name=ct]').val();

        var company_id = $('[name=company_id]').val();
        var partner_id = $('[name=partner_id]').val();

        $.ajax({
            type: 'POST',
            url: '/prm/view/details/save',
            data: serialized_data,
            success: function(data, status) {

                if (data == ''){
                    if (status != 'prevent-redirect') {
                        window.location = '/prm/view/details?partner=' + partner_id;
                    }
                } else {
                    // form was a json-encoded list of errors and error messages
                    var json = jQuery.parseJSON(data);

                    // remove color from labels of current errors
                    $('[class*=required]').parent().prev().removeClass('error-text');

                    // remove current errors
                    $('[class*=required]').children().unwrap();

                    if($.browser.msie){
                        $('[class*=msieError]').remove()
                    }

                    for (var index in json) {
                        var $error = $('[id$="-'+index+'"]');
                        var $labelOfError = $error.parent().prev();

                        // insert new errors after the relevant inputs
                        $error.wrap('<div class="required" />');
                        $error.attr("placeholder",json[index][0]);
                        $error.val('');
                        $labelOfError.addClass('error-text');
                    }
                }
            }
        });
    });

    // Onclick span will check the checkbox it is next to
    $("#library-modal-check span").on("click", function() {
        if(!$(this).prev().prop("checked"))
            $(this).prev().prop("checked", true);
        else
            $(this).prev().prop("checked", false);
    });

    // Filter location by clicking location on product cards then run ajax
    $("body").on("click", ".sub-title > small span", function(e) {
        e.preventDefault();
        e.stopPropagation();
        var value = $(this).text().trim(),
            split = value.replace(";", "").split(","),
            city,
            state;
        if(/^([A-Z]{2,})$/.test(split[0]))
            state = split[0];
        else
            city = split[0];
        if(split.length > 1)
            state = split[1];
        if(city)
            $("#lib-city").val(city);
        if(state)
            $("#state option[value="+ state +"]").attr("selected", "selected");

        run_ajax();
    });

    // Add check mark icon next to partner-tags then run ajax
    $(".partner-filters .partner-tag[title='Click to filter']").on("click", function() {
        if ($(this).children('i').hasClass('icon-ok')) {
            $(this).children('i').remove();
            $(this).addClass("disabled-tag");
        } else {
            var i = document.createElement('i');
            $(i).addClass("icon icon-ok");
            $(this).append(i);
            $(this).removeClass("disabled-tag");
        }
        run_ajax();
    });

    $(".partner-tag.days").on("click", function() {
        $(".date-picker-widget").hide();
        $(".partner-tag.custom").show();

        if ($(this).hasClass("disabled-tag")) {
            // add dates to input boxes
            var start_date = new Date();
            start_date.setDate(start_date.getDate() - $(this).data("days"));
            $("#activity-start-date").val(format_date(start_date));
            $("#activity-end-date").val(format_date(new Date()));

            // add checkbox
            $(".partner-tag.days").addClass("disabled-tag");
            $(".partner-tag.days").children("i").remove();
            $(this).removeClass("disabled-tag");
            $(this).append("<i class='icon icon-ok'></i>");
        } else {
            // remove dates from input boxes
            $("#activity-start-date").val("");
            $("#activity-end-date").val("");
            
            $(this).addClass("disabled-tag");
            $(this).children('i').remove();
        }

        run_ajax();
    });

    $(".partner-tag.custom").on("click", function() {
        $(".partner-tag.custom").hide();
        $(".date-picker-widget").show();
        $("#reset-date-range").css("visibility", "visible");

        $(".partner-tag.days").addClass("disabled-tag");
        $(".partner-tag.days > i.icon-ok").remove();
    });

    $("#reset-date-range").on("click", function() {
        // disable all day filters
        $(".partner-tag.days").addClass("disabled-tag");
        $(".partner-tag.days > i.icon-ok").remove();
        // show the custom date range button
        $(".partner-tag.custom").show();
        $(".date-picker-widget").hide();
        // remove dates from date inputs
        $("#activity-start-date").val("");
        $("#activity-end-date").val("");
        run_ajax();
    });

    // Waits till typing is completed for 1 sec (3 if tablet <) then runs ajax
    $(".partner-filters :input:not(select)").on("keyup paste", function() {
        /* Variables */
        var wait_time,
            that = $(this);
        if($(window).width() < 993) wait_time = 3000;
        else wait_time = 1000;

        if(this.timer) clearTimeout(this.timer);

        /* Ajax */
        this.timer = setTimeout(function() {
            $(that).addClass("loading");
            run_ajax();
        }, wait_time);
    });

    $(".partner-filters :input:has(option)").on("change", function() {
        run_ajax();
    });

    // Partner Library only logic
    if(location.pathname == '/prm/view/partner-library/'){
        // make sure add button is enabled by default
        // Partner Library product card click
        $("body").on("click",".product-card:not(.product-card.disabled-card)", function() {
            $("#add-partner-library").removeClass("disabled");
            /* Variables */
            var library_id = $(this).attr("id").split("-")[1],
                library_title = $(this).children("div.big-title").children("b").text() +"*",
                company_name = $("h1").children("a").text(),
                body_message = "Would you like to add OFCCP partner: <br /><br /><b id=\"modal-partner-name\">"+
                    library_title+"</b><br /><br />Clicking 'Add' will copy this partner to <b id=\"modal-company-name\">"+
                    company_name+"'s</b> Partner Relationship Manager.";
            $(".modal-body").children(":not(p:first-child)").remove();
            $(".modal-body").children("p").html(body_message);

            var for_completion = ["name", "email", "phone", "state"];
            $(this).children("div.product-details").children("input").each(function() {
                // if partner has name, email, or phone they will be added via template with type hidden
                if($(this).is("[type=hidden]")) {
                    var info = $(this).attr("class").split("-")[1];
                    if(for_completion.indexOf(info) >= 0) {
                        // remove from for_completion list if :info: in list
                        for_completion.splice(for_completion.indexOf(info), 1);
                    }
                }
            });
            // Add Note: section
            if(for_completion.length > 0) {
                var p = document.createElement("p");
                var note = document.createElement("span");
                var note_node = document.createTextNode("Note: ");
                note.appendChild(note_node);
                note.setAttribute("style", "color: red");
                var text = "This partner is missing information from the primary contact. " +
                    "Please contact the partner to obtain this missing data.";
                var ul = document.createElement("ul");
                for(var i = 0; i < for_completion.length; i++) {
                  var li = document.createElement("li");
                  var li_node = document.createTextNode(for_completion[i]);
                  li.appendChild(li_node);
                  ul.appendChild(li);
                }

                var node = document.createTextNode(text);
                p.appendChild(note);
                p.appendChild(node);

                optional = $("<p>These fields are missing but can be added " +
                             "later:</p>");
                $(".modal-body").append(p)
                
                $(".modal-body").append(optional).append(ul);

            }

            var disclaimer = document.createElement("span"),
                source = $(this).data("source"),
                d_text = "*This partner's information was provided by the " + source + ". " +
                    "To confirm its accuracy, DirectEmployers highly recommends following up directly " +
                    "with the partner. ";
            disclaimer.appendChild(document.createTextNode(d_text));
            disclaimer.setAttribute("style", "font-size: 0.85em;");
            $(".modal-body").append(disclaimer);

            /* Important */
            $("#add-partner-library").data("num", library_id);
            $("#partner-library-modal").modal("show");
        });
    }

    // When user clicks "Add" in Partner Library modal
    $(document.body).on("click", "#add-partner-library:not(.disabled)", function(){
        var data_to_send = {};
        // data("num") comes from clicking a product-card. Remember "Important"?
        data_to_send.library_id = $(this).data("num");
        if($("#new_select").length > 0)
          data_to_send.state = $("#new_select").val();
        if($("#go-to-partner").is(":checked")) data_to_send.redirect = true;
        $.ajax({
            type: "GET",
            url: "/prm/view/partner-library/add/",
            data: data_to_send,
            success: function(data) {
                var json = JSON.parse(data);
                var r_location = location.protocol + "//" + location.host +
                        "/prm/view/overview?partner="+json.partner;
                if(json.redirect === true) {
                    window.location = r_location;
                }
                $("#partner-library-modal").modal("hide");

                /* creating alert */
                var partner_name = $(".modal-body #modal-partner-name").text().slice(0, -1);
                var company_name = $(".modal-body #modal-company-name").text();
                var alert_html = "<div class=\"alert alert-success\"><button type=\"button\" " +
                    "class=\"close\" data-dismiss=\"alert\">x</button><a style=\"text-decoration: underline\" " +
                    "href="+r_location+">" + partner_name+"</a> was added to "+company_name+" " +
                    "Partner Relationship Manager.</div>"

                $("#lib-alerts").html(alert_html);
                if (typeof(isIE) == "number" && isIE > 9 || typeof(isIE) == 'boolean' && isIE == false) {
                    var filter_data = build_data();
                    filter_data.page = get_page(filter_data);
                    send_filter(filter_data);
                } else {
                    var selector = "#library-" + String(data_to_send.library_id);
                    $(selector).remove();
                }

            }
        });
    });

    if($("#p-tags").length > 0) {
        /* Partner Tagging */
        $("#p-tags").hide();
        $("#p-tags").tagit({
            allowSpaces: true,
            tagSource: function(search, showChoices) {
                var value = $(".tagit-new > input").val(),
                    search = {value: value},
                    that = this;
                $.ajax({
                    type: "GET",
                    url: "/prm/view/records/get-tags",
                    data: search,
                    success: function(data) {
                        var jdata = jQuery.parseJSON(data);
                        showChoices(that._subtractArray(jdata, that.assignedTags()))
                    }
                });
            },
            beforeTagAdded: function(event, ui) {
                ui.tag.hide();
                var name = ui.tag.children("span").html();
                $.ajax({
                    type: "GET",
                    url: "/prm/view/records/get-tag-color",
                    data: {"name": name},
                    success: function(data) {
                        var jdata = jQuery.parseJSON(data);
                        if(jdata.length > 0)
                            ui.tag.css("background-color", "#"+jdata[0]);
                        ui.tag.show();
                    }
                })
            },
            autocomplete: {delay: 0, minLength: 1},
            placeholderText: "Add Tag"
        });
    }
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

/*
Make the page look like it did location.history.go(-1) ago.

Input:
:data:  is the event.state from window.onpopstate
 */
function fill_in_history_state(data){
    /* Grab inputs */
    var kw_input = $("#lib-keywords"),
        ct_input = $("#lib-city");
    var si_list = ["veteran", "female", "minority", "disabled",
                       "disabled veteran", "unspecified"];

    
    if(!data){
        $(kw_input.val(""));
        $("#state option[value='']").attr("selected", "selected");
        $(ct_input).val("");
        $(".partner-tag").children('i').remove();
        $(".partner-tag").addClass("disabled-tag");
        $("#reset-date-range").css("visibility", "hidden");
        return false
    }

    // calculate which day buttons should be checked 
    var start_date = new Date(data.start_date || new Date(0)),
        end_date = new Date(data.end_date || new Date()),
        days = (end_date.getTime() - start_date.getTime()) /
               (1000 * 60 * 60 * 24); // msecs, secs, hours, days
        var button = $(".partner-tag.days[data-days='" + days + "']");

    // disable all buttons
    $(".partner-tag").children('i').remove();
    $(".partner-tag").addClass("disabled-tag");
    if(button.length) {
        button.append("<i class='icon icon-ok'></i>").removeClass("disabled-tag");
        $(".partner-tag.custom").show();
        $(".date-picker-widget").hide();
        $("#reset-date-range").css("visibility", "visible");
    } else {
        // no day button is clicked, so show the date picker widget
        $("#activity-start-date").val(data.start_date);
        $("#activity-end-date").val(data.end_date);
        $(".partner-tag.custom").hide();
        $(".date-picker-widget").show();
        $("#reset-date-range").css("visibility", "visible");
    }

    if(typeof(data.keywords) != "undefined")
        $(kw_input).val(String(data.keywords));
    else
        $(kw_input.val(""));
    if(typeof(data.state) != "undefined")
        $("#state option[value="+ data.state +"]").attr("selected", "selected");
    else
        $("#state option[value='']").attr("selected", "selected");
    if(typeof(data.city) != "undefined")
        $(ct_input).val(String(data.city));
    else
        $(ct_input).val("");
    if(typeof(data.special_interest) == "undefined") data.special_interest = [];
    for(var i = 0; i < data.special_interest.length; i++){
        if(si_list.indexOf(data.special_interest[i]) >= 0){
            var value = data.special_interest[i];
            si_list.splice(si_list.indexOf(value), 1);
            var cl = String(value).replace(" ", "-");
            $(".sidebar .partner-tag").each(function() {
                if($(this).hasClass(cl)) {
                    if (!$(this).children('i').hasClass('icon-ok')) {
                        var i = document.createElement('i');
                        $(i).addClass("icon icon-ok");
                        $(this).append(i);
                        $(this).removeClass("disabled-tag");
                    }
                }
            });
        }
    }
    return false
}

/*
format a Date object to %m/%d/%Y
*/
function format_date(date) {
    // months are indexed at 0, while date and year are not
    return (date.getMonth() + 1) + "/" + date.getDate() + "/"
                                 + date.getFullYear();
}

/*
build data object from all sources on the page.
 */
function build_data() {
    var data = {},
        special_interest = [],
        start_date = null,
        end_date = null;

    $(".partner-filters label + :input").each(function() {
        if($(this).val()) {
            var data_key = $(this).prev('label').html().replace(":", "").toLowerCase();
            data[data_key] = $(this).val();
        }
    });
    $(".partner-tag:has(i):not(.partner-tag.days)").each(function() {
        special_interest.push($(this).text().toLowerCase());
    });
    if(special_interest.length > 0)
        data.special_interest = special_interest;
    if($(".date-picker-widget").is(":visible")) {
        start_string = $("#activity-start-date").val();
        end_string = $("#activity-end-date").val();
        if(start_string)
            start_date = new Date(start_string);
        if(end_string)
            end_date = new Date(end_string);
    } else if($(".partner-tag.days").has("i").text()) {
        var days = $(".partner-tag.days").has("i").data('days');
        start_date = new Date();
        end_date = new Date();
        start_date.setDate(start_date.getDate() - days);
    }
    if(start_date)
        data.start_date = format_date(start_date);
    if(end_date)
        data.end_date = format_date(end_date);

    var sort_by = $(".sort-by.active").text().toLowerCase();
    if(sort_by)
        data.sort_by = sort_by;
    if($(".sort-by.active").hasClass("descending"))
        data.desc = 1;

    var per_page = $("#per-page span").text();
    if(per_page && per_page != "10") {
        data.per_page = per_page;
    }

    if($(".row-filler").children("input").is(":checked")) data.a=1;

    return data
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

function send_filter(data_to_send) {
    var path = location.pathname;
    $.ajaxSettings.traditional = true;
    $.ajax({
        type: 'GET',
        url: path,
        data: data_to_send,
        success: function(data) {
            $("#partner-holder").html(data);
            $(".partner-filters :input:not(select)").each(function() {
                if($(this).hasClass("loading"))
                    $(this).removeClass("loading")
            });
            // Very important, don't touch
            if(data_to_send && data_to_send.a) {
                var the_list = $("#partner-holder").children("div.product-card");
                $(the_list).each(function() {
                    $(this).hide();
                });
                var loop = function(index, list) {
                    if(index == list.length) return false;
                    var direction = 'left',
                        num = Math.ceil(Math.random()*4);
                    if(num==1) direction = 'up';
                    else if(num==2) direction = 'right';
                    else if(num==3) direction = 'down';
                    $(list[index]).show("drop", {direction: direction}, 125, function() {
                        loop(index + 1, list);
                    });
                };
                setTimeout(function() {
                    loop(0, the_list);
                }, 10);
            }
        }
    });
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
    if(data.start_date || data.end_date) {
        $("#reset-date-range").css("visibility", "visible");
    } else {
        $("#reset-date-range").css("visibility", "hidden");
    }

    if (typeof(isIE) == "number" && isIE > 9 || typeof(isIE) == 'boolean' && isIE == false) {
        history.pushState(data, "filter", search_url);
    } else {
        location.search = search_url;
    }
}

/*
If someone loads the page with request.GET info (not from ajax) fill page with info
*/
function show_selected() {
    var q = location.search,
        params = q.replace("?", "").split("&"),
        partners = $(".sidebar .partner-tag"),
        start_date = null,
        end_date = null;
    if (typeof(isIE) == "number" && isIE < 9) {
        if(q === "?") return false;
    }
    for(var i = 0; i < params.length; i++) {
        var s = params[i].split("="),
            key = s[0];
        var value = s[1].replace("%20", "-");
        value = value.replace(" ", "-");
        if(key == "start_date") {
            start_date = new Date(value || new Date(0));
        }
        if(key == "end_date") {
            end_date = new Date(value || new Date());
        }
        if(key == "special_interest") {
            partners.each(function() {
                if($(this).hasClass(value)) {
                    var i = document.createElement('i');
                    $(i).addClass("icon icon-ok");
                    $(this).append(i);
                    $(this).removeClass("disabled-tag");
                }
            });
        }
        if(key == "state") {
            $("select option").each(function(){
                if($(this).val() == value)
                    $(this).attr("selected", "selected");
            });
        }
        if(key == "sort_by") {
            $(".sort-by").each(function() {
                if(value == $(this).text().toLowerCase()) {
                    $(this).addClass("active ascending");
                } else {
                    $(this).removeClass("active descending ascending");
                }
            });
        }
        if(key == "desc") {
            $(".sort-by.active").removeClass("ascending").addClass("descending");
        }
        if(key == "per_page") {
            $("#per-page span").text(value);
        }
    }

    // disable all buttons
    $(".partner-tag.days").children('i').remove();
    $(".partner-tag.days").addClass("disabled-tag");
    if(start_date && end_date) {
        var days = (end_date.getTime() - start_date.getTime()) /
                   (1000 * 60 * 60 * 24); // msecs, secs, hours, days
            var button = $(".partner-tag.days[data-days='" + days + "']");
        if(button.length) {
            button.append("<i class='icon icon-ok'></i>").removeClass("disabled-tag");
            $(".partner-tag.custom").show();
            $(".date-picker-widget").hide();
            $("#reset-date-range").css("visibility", "visible");
        } else {
            // no day button is clicked, so show the date picker widget
            $("#activity-start-date").val(format_date(start_date));
            $("#activity-end-date").val(format_date(end_date));
            $(".partner-tag.custom").hide();
            $(".date-picker-widget").show();
            $("#reset-date-range").css("visibility", "visible");
        }
    }

    $('#add-primary-contact').click(function() {
        $(this).remove();
        $('#primary-contact').removeClass('mobile_hide');
    })
}
