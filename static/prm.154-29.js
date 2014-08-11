$(document).ready(function() {
    if(location.search) show_selected();
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
                        $error.val('')
                        $labelOfError.addClass('error-text');
                    }
                }
            }
        });
    });

    $('#item-save').on("click", function(e) {
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

    $(".partner-filters .partner-tag").on("click", function() {
        if ($(this).children('i').hasClass('icon-ok')) {
            $(this).children('i').remove();
            $(this).addClass("disabled-tag");
        } else {
            var i = document.createElement('i');
            $(i).addClass("icon icon-ok");
            $(this).append(i);
            $(this).removeClass("disabled-tag");
        }
        var data = build_data();
        update_search_url(data);
        send_filter(data);
    });

    $(".partner-filters :input:not(select)").on("keyup paste", function() {
        /* Variables */
        var wait_time,
            that = $(this);
        if($(window).width() < 993) wait_time = 3000;
        else wait_time = 1000;

        if(this.timer) clearTimeout(this.timer);

        /* Ajax */
        this.timer = setTimeout(function() {
            var data = build_data();
            $(that).addClass("loading");
            update_search_url(data);
            send_filter(data);
        }, wait_time);
    });

    $(".partner-filters :input:has(option)").on("change", function() {
        var data = build_data();
        update_search_url(data);
        send_filter(data);
    });

    if(location.pathname == '/prm/view/partner-library/'){
        $("body").on("click",".product-card:not(.product-card.disabled-card)", function() {
            var library_id = $(this).attr("id").split("-")[1],
                library_title = $(this).children("div.big-title").children("b").text() +"*",
                company_name = $("h1").children("a").text(),
                body_message = "Would you like to add OFCCP partner: <br /><br /><b>"+
                    library_title+"</b><br /><br />Clicking 'Add' will copy this partner to <b>"+
                    company_name+"'s</b> Partner Relationship Manager.";
            $(".modal-body").children(":not(p:first-child)").remove();
            $(".modal-body").children("p").html(body_message);

            var for_completion = ["name", "email", "phone"];
            $(this).children("div.product-details").children("input").each(function() {
                if($(this).is("[type=hidden]")) {
                    var info = $(this).attr("class").split("-")[1];
                    if(for_completion.indexOf(info) >= 0) {
                        for_completion.splice(for_completion.indexOf(info), 1);
                    }
                }
            });
            if(for_completion.length > 0) {
                var p = document.createElement("p");
                var note = document.createElement("span");
                var note_node = document.createTextNode("Note: ");
                note.appendChild(note_node);
                note.setAttribute("style", "color: red");
                var text = "This partner is missing information from the primary contact. " +
                    "Please contact the partner to obtain this missing data:"
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
                $(".modal-body").append(p).append(ul);
            }


            var disclaimer = document.createElement("span"),
                d_text = "*This partner's information was provided by the OFCCP Referral Directory. " +
                    "To confirm its accuracy, DirectEmployers highly recommends following up directly " +
                    "with the partner. ";
            disclaimer.appendChild(document.createTextNode(d_text));
            disclaimer.setAttribute("style", "font-size: 0.85em;");
            $(".modal-body").append(disclaimer);

            $("#add-partner-library").data("num", library_id);
            $("#partner-library-modal").modal("show");
        });
    }

    $("#add-partner-library").on("click", function(){
        var data = {};
        data.library_id = $(this).data("num");
        if($("#go-to-partner").is(":checked")) data.redirect = true;
        $.ajax({
            type: "GET",
            url: "/prm/view/partner-library/add/",
            data: data,
            success: function(data) {
                var json = JSON.parse(data);
                if(json.redirect === true) {
                    window.location = location.protocol + "//" + location.host +
                        "/prm/view/overview?partner="+json.partner;
                }
                $("#partner-library-modal").modal("hide");
            }
        });
    })
});

function build_data() {
    var data = {},
        special_interest = [];
    $(".partner-filters :input").each(function() {
        if($(this).val()) {
            var data_key = $(this).prev('label').html().replace(":", "").toLowerCase();
            data[data_key] = $(this).val();
        }
    });
    $(".partner-tag:has(i)").each(function() {
        special_interest.push($(this).text().toLowerCase());
    });
    if(special_interest.length > 0)
        data.special_interest = special_interest;

    if($(".row-filler").children("input").is(":checked")) data.a=1;

    return data
}

function send_filter(data_to_send) {
    var path = location.pathname;
    $.ajaxSettings.traditional = true;
    $.ajax({
        type: 'GET',
        url: path,
        global: false,
        data: data_to_send,
        success: function(data) {
            $("#partner-holder").html(data);
            $(".partner-filters :input:not(select)").each(function() {
                if($(this).hasClass("loading"))
                    $(this).removeClass("loading")
            });
            // Very important, don't touch
            if(data_to_send.a) {
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

function update_search_url(data) {
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
    //location.search = search_url;
}

function show_selected() {
    var q = location.search,
        params = q.replace("?", "").split("&"),
        partners = $(".sidebar .partner-tag");
    for(var i = 0; i < params.length; i++) {
        var s = params[i].split("="),
            key = s[0],
            value = s[1].replace("%20", "-");
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
    }
}
