/**
 *
 * @param types
 * @constructor
 */
var Report = function(types) {
    this.types = types;
    this.pages = [];
};

/**
 *
 * @param report_types
 * @returns {Array}
 */
Report.prototype.create_pages = function(report_types) {
     var pages = {"PRM": [new Page(true, "date_location", "Date and/or Location"),
                          new ListPage(false, "/includes/prm/partners", "Select Partners", "/reports/ajax/partner"),
                          new ListPage(false, "/includes/prm/contacts", "Select Contacts", "/reports/ajax/contact")]},
         data = []; // Initialize array that will be returned

    // When multiple report types have been selected this will combine.
    for (var key in report_types) {
        if (pages.hasOwnProperty(report_types[key])) {
            data.push.apply(data, pages[report_types[key]]);
        }
    }
    return data
};

Report.prototype.current_page = function() {
    for (var page in this.pages) {
        if (this.pages[page].active === true) {
            return this.pages[page];
        }
    }

    // if no active pages give first page.
    this.pages[0].active = true;
    return this.pages[0];
};

Report.prototype.update_pages = function(current_page_index, direction) {
    this.pages[current_page_index].active = false;
    if(direction === "next") {
        this.pages[current_page_index + 1].active = true;
    } else {
        this.pages[Math.max(0, current_page_index - 1)].active = true;
    }
};

Report.prototype.load_active_page = function(filters) {
    var current_page = this.current_page(),
        data = {"csrfmiddlewaretoken": read_cookie("csrftoken"),
                "html": current_page.html},
        url = location.protocol + "//" + location.host; // https://secure.my.jobs
    if(typeof filters !== "undefined") {
        delete data["html"];
        $.extend(data, filters);
    }
    if (current_page instanceof ListPage) {
        url += current_page.url;
    } else {
        url += location.pathname;
    }
    $.ajax({
        type: 'POST',
        url: url,
        data: $.param(data, true),
        success: function(data) {
            $("#content").html(data);
        },
        error: function () {
            // TODO: change when testing is done to something more useful.
            throw "Something horrible happened.";
        },
        complete: function() {
            current_page.load_data();
        }
    });
};

Report.prototype.next_page = function() {
    var current_page = this.current_page(),
        current_page_index = this.pages.indexOf(current_page),
        next_page = this.pages[current_page_index + 1];
    current_page.active = false;
    next_page.active = true;
    this.load_active_page(current_page.data);
};

Report.prototype.previous_page = function() {
    var current_page = this.current_page(),
        current_page_index = this.pages.indexOf(current_page),
        prev_page = this.pages[Math.max(0, current_page_index - 1)],
        prev_data_to_load = this.pages[Math.max(0, current_page_index - 2)].data;
    current_page.active = false;
    prev_page.active = true;
    this.load_active_page(prev_data_to_load);
};

/**
 *
 * @param active
 * @param html
 * @param step
 * @constructor
 */
var Page = function(active, html, step) {
    this.active = active;
    this.data = null;
    this.html = html;
    this.step = step;
};

/**
 * Overwrite toString function for better object name
 * @returns {string}
 */
Page.prototype.toString = function() {
    return '<Page: ' + this.step + '>';
};

Page.prototype.save_data = function() {
    var inputs = $("#content input, #content select:not([class*=__select])"),// all inputs and selects on page.
        data = {};
    for(var i = 0; i < inputs.length; i++) {
        data[inputs[i].id] = inputs[i].value;
    }
    this.data = data;
};

Page.prototype.load_data = function() {
    for(var key in this.data) {
        if(this.data.hasOwnProperty(key))
            $("#"+key).val(this.data[key]);
    }
};

/**
 *
 * @param active
 * @param html
 * @param step
 * @constructor
 */
var ListPage = function(active, html, step, url) {
    this.url = url;
    Page.call(this, active, html, step)
};

ListPage.prototype = Object.create(Page.prototype);

// Overwrite Page's toString
ListPage.prototype.toString = function() {
    return "<ListPage: " + this.step + ">";
};

$(document).ready(function() {
    // Simulate page 1 (page 1 is where the user selects what types of reporting)
    report = new Report(["PRM"]);
    report.pages = report.create_pages(report.types);
    report.load_active_page();

    $(document).on("click", ".datepicker",function(e) {
       $(this).pickadate({
           format: "mm/dd/yyyy",
           selectYears: true,
           selectMonths: true,
           today: false,
           clear: false,
           close: false,
           onOpen: function () {
               if (this.get("id") === "start-date") {
                   var end_date = $("#end-date").val();
                   this.set("max", new Date(end_date || new Date()));
               } else if (this.get("id") === "end-date") {
                   var start_date = $("#start-date").val();
                   this.set("min", new Date(start_date || new Date(0)))
               }
           }
       });
    });

    $(document).on("click", "#next:not(.disabled)", function(e) {
        e.preventDefault();
        report.current_page().save_data();
        report.next_page();
    });

    $(document).on("click", "#back", function(e) {
        e.preventDefault();
        report.current_page().save_data();
        report.previous_page();
    });

    $(document).on("click", "#submit_report", function(e) {
        e.preventDefault();
        report.current_page().save_data();
        report.submit_report();
    });

    // All partner/contact checkbox logic
    $(document).on("click", "input[type='checkbox']#all", function(e) {
        var all_checkboxes = $("#content input:not(#all)"),
            next_btn = $("#next");
        // if #all is checked onclick
        if($(this).is(":checked")) {
            // turn all checks on
            $(all_checkboxes).each(function(element) {
                $(all_checkboxes[element]).prop("checked", true);
            });

            // remove disabled on next button if it is disabled
            if($(next_btn).hasClass("disabled")) {
                $(next_btn).removeClass("disabled");
            }
        } else {
            // turn all checks off
            $(all_checkboxes).each(function(element) {
               $(all_checkboxes[element]).prop("checked", false);
            });
            // disable next button
            $("#next").addClass("disabled");
        }
    });

    // The other checkboxes
    $(document).on("click", "input[type='checkbox']:not(#all)", function(e) {
        var all_checkboxes = $("#content input:not(#all)"),
            all_are_checked = true,
            all_are_not_checked = true,
            next_btn = $("#next");
        $(all_checkboxes).each(function(element) {
            // Check to see if all checkboxes are checked
            if(!$(all_checkboxes[element]).is(":checked")){
                all_are_checked = false;
                // exit .each function. Mimics break
                return false;
            }
        });
        var all_checkbox = $("#content input#all"); // the all partner/contact checkbox
        if(all_are_checked === false)
            $(all_checkbox).prop("checked", false);
        else
            $(all_checkbox).prop("checked", true);

        // disabling next button logic
        if($(this).is(":checked")) {
            if($(next_btn).hasClass("disabled")) {
                $(next_btn).removeClass("disabled");
            }
        } else {
            if(all_are_checked === false) {
                $(all_checkboxes).each(function(element) {
                    if($(all_checkboxes[element]).is(":checked")){
                        all_are_not_checked = false;
                        // exit .each function. Mimics break
                        return false;
                    }
                });
                if(all_are_not_checked == true) {
                    $("#next").addClass("disabled");
                } else {
                    if($(next_btn).hasClass("disabled")) {
                        $(next_btn).removeClass("disabled");
                    }
                }
            }
        }
    });
});

function read_cookie(cookie) {
    var nameEQ = cookie + "=",
        ca = document.cookie.split(';');
    for (var i=0; i< ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === ' ')
            c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0)
            return c.substring(nameEQ.length, c.length);
    }
    return null;
}