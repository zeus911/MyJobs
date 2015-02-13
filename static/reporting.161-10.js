/**
 * Report manages the Page objects.  Can retrieve current page object being
 * used, move to next page, or go back to previous page.  Lastly, Report
 * also handles submission.
 * @param types
 * @constructor
 */
var Report = function(types) {
    this.types = types;
    this.pages = this.create_pages(this.types);

    this.generate_sidebar();
};

Report.prototype.bind_event = function() {
    var report = this;
    $(document).on("click", "#next:not(.disabled)", function(e) {
        e.preventDefault();
        report.current_page().save_data();
        report.next_page();
    });

    $(document).on("click", "#back", function(e) {
        e.preventDefault();
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
};

// Generates a list of Page objects based on report types.
// Different virtual reports go here.
Report.prototype.create_pages = function(report_types) {
    // page lists
     var p_lists = {"PRM": [new Page(true, "myreports/date_location", "Date and/or Location"),
                            new FilterPage(false, "myreports/includes/prm/partners",
                                "Select Partners", "/reports/ajax/mypartners/partner", "partner"),
                            new FilterPage(false, "myreports/includes/prm/contacts",
                                "Select Contacts", "/reports/ajax/mypartners/contact", "contact")]},
         pages = []; // Initialize array that will be returned

    // When multiple report types have been selected this will combine.
    for (var key in report_types) {
        if (p_lists.hasOwnProperty(report_types[key])) {
            pages.push.apply(pages, p_lists[report_types[key]]);
        }
    }
    return pages;
};


// Grabs a Page object that has page.active === true
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

// Can be called to load the current page independently from
// next/prev page calls. See Report.prototype.current_page to see
// how current page is found.
Report.prototype.load_active_page = function(filters) {
    var current_page = this.current_page(),
        data = {"csrfmiddlewaretoken": read_cookie("csrftoken"),
                "output": current_page.output},
        url = location.protocol + "//" + location.host; // https://secure.my.jobs
    if(typeof filters !== "undefined") {
        $.extend(data, filters);
    }
    if (current_page instanceof FilterPage) {
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
            if(current_page.data != null)
                current_page.load_data();
        }
    });
};

// Move active status to the next page in Report.pages.
// Adds extra filtering if needed, calls load_active_page,
// and updates sidebar accordingly.
Report.prototype.next_page = function() {
    var current_page = this.current_page(),
        current_page_index = this.pages.indexOf(current_page),
        next_page = this.pages[current_page_index + 1],
        filter = {};
    current_page.active = false;
    next_page.active = true;
    // if FilterPage, grab all the data prior to next_page
    if(next_page instanceof FilterPage) {
        // Extend filter for every page from index 0 up to index next_page
        for(var i = 0; i < this.pages.indexOf(next_page); i++) {
            $.extend(filter, this.pages[i]["data"])
        }
    // else page prior is good enough
    } else {
        filter = current_page.data;
    }
    filter["ignore_cache"] = true;
    this.load_active_page(filter);
    this.next_sidebar();
    if(current_page_index + 1 === this.pages.length - 1) {
        this.activate_generate_report();
    }
};


// Move active status to the previous page in Report.pages.
// Adds extra filtering if needed, calls load_active_page,
// and updates sidebar accordingly.
Report.prototype.previous_page = function() {
    var current_page = this.current_page(),
        current_page_index = this.pages.indexOf(current_page),
        prev_page_index = Math.max(0, current_page_index - 1),
        prev_page = this.pages[prev_page_index],
        prev_data_to_load = this.pages[Math.max(0, current_page_index - 2)].data,
        filter = {};
    current_page.active = false;
    prev_page.active = true;
    if(prev_page instanceof FilterPage && prev_page_index !== 0) {
        for(var i = 0; i < prev_page_index; i++) {
            $.extend(filter, this.pages[i]["data"]);
        }
    } else {
        filter = prev_data_to_load;
    }
    this.load_active_page(filter);
    this.prev_sidebar();
};

// Builds out the steps based on Report.pages,
// more specifically Page.step.
Report.prototype.generate_sidebar = function() {
    var sidebar_content = $("#sidebar-content"),
        ul = $("<ul></ul>");
    // Generate top heading
    // TODO: Make "PRM Report" programmatic
    sidebar_content.prepend($("<h2 class=\"top\">PRM Report</h2>"));
    // Generate step 1, selecting a topic.
    ul.append($("<li><i class=\"fa fa-check success\"></i>Select topic(s)</li>"));
    for(var page in this.pages) {
        var li = $("<li id=\"step-"+ page +"\"></li>"), // <li></li>
            i; // <i></i>
        if(page === "0") {
            li.addClass("active");
        }
        i = $("<i class=\"fa fa-minus\"></i>");
        li.html(" " + this.pages[page].step);
        li.prepend(i);
        ul.append(li);
    }
    sidebar_content.prepend(ul);
};

// Removes .active from current step, changes "-" to a check,
// and adds .active to the next step
Report.prototype.next_sidebar = function() {
    var active = $(".sidebar li.active");
    $(active).removeClass("active").children("i").removeClass("fa-minus")
        .addClass("fa-check success");
    $(active).next().addClass("active");
};


// Removes .active from current step and adds .active to previous step.
// If previous step has a check change it back to a "-".
Report.prototype.prev_sidebar = function() {
    var active = $(".sidebar li.active"),
        report_btn = $("#gen-report");
    $(active).removeClass("active");
    $(active).prev().addClass("active");
    // if previous step has check.
    if($(active).prev().children("i").hasClass("fa-check")) {
        $(active).prev().children("i").removeClass("fa-check success").addClass("fa-minus");
    }
    // if generate report is not disabled.
    if(!report_btn.hasClass("disabled")) {
        report_btn.addClass("disabled").unbind("click");
    }
};


// Actives the generate report button on sidebar.
// Also binds a click event to the button.
Report.prototype.activate_generate_report = function() {
    var that = this;
    $("#gen-report").removeClass("disabled").on("click", function test() {
        that.submit_report();
    });
};

// Submits the report
Report.prototype.submit_report = function() {
    var pages = this.pages,
        data = {"csrfmiddlewaretoken": read_cookie("csrftoken")},
        url = location.protocol + "//" + location.host; // https://secure.my.jobs
    // combine all data together
    for (var page in pages) {
        $.extend(data, pages[page]["data"]);
    }
    $.ajax({
        type: 'POST',
        dataType: "json",
        url: url + "/reports/ajax/mypartners/contactrecord",
        data: $.param(data, true),
        success: function(data) {
            // TODO: Do something useful here.
            $("#content").html(JSON.stringify(data.records));
        },
        error: function () {
            // TODO: change when testing is done to something more useful.
            throw "Something horrible happened.";
        }
    });
};

/**
 * Page handles saving and loading of data.
 *
 * @param active    Boolean that is used to determine if a page is the one
 *                  currently loaded.
 * @param output    String that tells the view that is hit by load_active_page
 *                  what template to use.
 * @param step      String that is used for sidebar to show the user what the
 *                  main purpose of this page.
 * @constructor
 */
var Page = function(active, output, step) {
    this.active = active;
    this.data = null;
    this.output = output;
    this.step = step;
};


// Overwrite toString function for better object name. Useful for debugging.
// @returns {string}
Page.prototype.toString = function() {
    return '<Page: ' + this.step + '>';
};

// Looks at every input and select in the #content div and follows this pattern:
// {"element's ID": "element's value"}
Page.prototype.save_data = function() {
    var inputs = $("#content input, #content select:not([class*=__select])"),// all inputs and selects on page.
        data = {};
    for(var i = 0; i < inputs.length; i++) {
        data[inputs[i].id] = inputs[i].value;
    }
    this.data = data;
};

// Looks at every key which is based on element's ID and adds element's value.
Page.prototype.load_data = function() {
    for(var key in this.data) {
        if(this.data.hasOwnProperty(key))
            $("#"+key).val(this.data[key]);
    }
};


// FilterPage is PRM specific. Needs extra filters and hits different
// filtering views to grab additional information.
var FilterPage = function(active, output, step, ajax_url, record_type) {
    this.url = ajax_url;
    this.record_type = record_type;
    Page.call(this, active, output, step)
};

// Creates a FilterPage.prototype that inherits from Page.prototype.
// Part of the Page.call() in FilterPage constructor
FilterPage.prototype = Object.create(Page.prototype);

// Overwrite Page's toString
FilterPage.prototype.toString = function() {
    return "<FilterPage: " + this.step + ">";
};

// Overwrites Page.prototype.save_data
FilterPage.prototype.save_data = function() {
    var records = [],
        all_checkbox = $("input#all"), // Button that acts like "Select All"
        all_checkboxes = $("#content input[type='checkbox']:not(#all)"), // All other checkboxes
        record_type = this.record_type;
    if($(all_checkbox).is(":checked")) {
        this.data = {}; // initialize this.data;
        this.data[record_type] = "";
    } else {
        // iterate through all checkboxes and find all the ones that are checked
        // and add to data.
        $(all_checkboxes).each(function(element) {
            if($(all_checkboxes[element]).is(":checked")){
                records.push(all_checkboxes[element].value);
            }
        });
        // if there were no partners selected ignore saving data.
        if(records.length > 0) {
            this.data = {}; // initialize this.data;
            this.data[record_type] = records;
        } else {
            return false;
        }
    }
};

// Overwrites Page.prototype.load_data
FilterPage.prototype.load_data = function() {
    var record_type = this.record_type;
    if(this.data[record_type] != "") {
        var all_checkboxes = $("#content input"); // all checkboxes in content
        $(all_checkboxes).each(function(element) {
            $(all_checkboxes[element]).prop("checked", false);
        });
        for(var i = 0; i < this.data[record_type].length; i++) {
            $("input[value='"+this.data[record_type][i]+"']").prop("checked", true);
        }
    }
};

$(document).ready(function() {
    // Simulate page 1 (page 1 is where the user selects what types of reporting)
    var report = new Report(["PRM"]);
    //report.load_active_page();

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

    $(document).on("click", "#start-report", function(e) {
        e.preventDefault();
        var report = new Report();
        report.bind_events();
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
