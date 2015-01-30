/**
 * Report manages the Page objects.  Can retrieve current page object being
 * used, move to next page, or go back to previous page.  Lastly, Report
 * also handles submission.
 * @param types - An Array of report types. i.e. ["PRM", "Compliance"]
 * @constructor
 */
var Report = function(types) {
    this.types = types;
    this.pages = [new Page()];
    this.current_page_num = 1;
    this.has_prm_report = function() {
        return Boolean(this.types.indexOf("PRM") > -1);
    };
    // Retrieves a page if it already exists otherwise make a new one,
    // django-esque!
    this.get_or_create_page = function(page_num) {
        var index = Math.max(0, page_num - 1),
            page;
        try {
            if(this.pages[index] == undefined) throw "No page exists";
        }
        catch(err) {
            this.pages.push(new Page());
        }
        finally {
            page = this.pages[index];
        }
        return page;
    };
    // Uses ajax to retrieve the next page's template. Adjust
    // current_page_num then get_or_create_page based on adjusted
    // current page number.
    this.next_page = function() {
        var current_page = this.current_page(),
            that = this,
            url = location.protocol + "//" + location.host, // https://secure.my.jobs
            data = {"page": this.current_page_num + 1}; // Default data
        // page.filter is used to tell ajax to hit a different url.
        // exception pages from default.
        if(current_page.filter === "partner" || current_page.filter === "contact") {
            url += "/reports/ajax/"+ current_page.filter +"s";
            data = current_page.data;
        }
        else url = location.path;
        $.ajax({
            type: 'GET',
            url: url,
            data: data,
            success: function(data) {
                // replace content.
                $("#content").html(data);
            },
            error: function() {
                // TODO: change when testing is done to something more useful.
                throw "Something horrible happened.";
            },
            complete: function() {
                // let report know the new current page.
                that.current_page_num += 1;
                // 90% of the time this will create a new page.
                var page = that.get_or_create_page(that.current_page_num),
                    current_page_num = that.current_page_num;

                // Add custom fields to exception pages
                if(that.has_prm_report() && (
                        current_page_num == 2 ||
                        current_page_num == 3 ||
                        current_page_num == 4
                    )) {
                    if(current_page_num == 2) {
                        page.filter = "partner";
                    } else if(current_page_num == 3) {
                        page.filter = "contact";
                        page.custom_save = "partner";
                    } else if(current_page_num == 4) {
                        page.custom_save = "contact";
                    }
                }
                // A newly made page's .data will be null
                if(that.current_page().data != null)
                    that.current_page().load_data();
            }
        });
    };
    // Uses ajax to retrieve previous page. On complete adjust
    // current_page and load page data
    this.previous_page = function() {
        var current_page = this.current_page(),
            that = this,
            url = location.protocol + "//" + location.host,
            data = {"page": Math.max(1, this.current_page_num - 1)};
        // TODO: fix exception page logic
        if(current_page.custom_save === "contact") {
            url += "/reports/ajax/partners";
            data = current_page.data;
        }
        else url = location.path;
        $.ajax({
            type: 'GET',
            url: url,
            data: data,
            success: function(data) {
                $("#content").html(data);
            },
            error: function() {
                // TODO: change when testing is done to something more useful.
                throw "Something horrible happened.";
            },
            complete: function() {
                that.current_page_num -= 1;
                that.current_page().load_data();
            }
        });
    };
    // Retrieves the current page based off of current_page_num
    this.current_page = function() {
        return this.pages[this.current_page_num - 1];
    };
    // Submits the report via ajax
    this.submit_report = function() {
        var data = {};
        for(var i = 0; i < this.pages.length; i++) {
            $.extend(data, this.pages[i].data);
        }
        // TODO: correctly connect to backend.
        $.ajax({
            type: 'POST',
            url: location.protocol + "//" + location.host + "/reports/search",
            data: data,
            success: function(data) {
                console.log("success");
            }
        });
    }
};
/**
 * Page handles data.
 * @constructor
 */
var Page = function() {
    // Data is used for filtering purposes.  If a key = "" means "all".
    this.data = null;
    // Saves page data. Usually is called during page change forward or back.
    this.save_data = function() {
        // Check to see if there is a custom save associated with this page.
        if(this.custom_save == undefined) {
            // Run default save funciton
            var inputs = $("#content input, #content select:not([class*=__select])"),// all inputs and selects on page.
                data = {};
            for(var i = 0; i < inputs.length; i++) {
                data[inputs[i].id] = inputs[i].value;
            }
            this.data = data;
        } else {
            // Run exception save functions
            if(this.custom_save === "partner") {
                var partners = [],
                    all_checkbox = $("input#all"), // Button that acts like "Select All"
                    all_checkboxes = $("#content input[type='checkbox']:not(#all)"); // All other checkboxes
                if($(all_checkbox).is(":checked")) {
                    this.data = {"partner": ""};
                } else {
                    // iterate through all checkboxes and find all the ones that are checked
                    // and add to data.
                    $(all_checkboxes).each(function(element) {
                        if($(all_checkboxes[element]).is(":checked")){
                            partners.push(all_checkboxes[element].value);
                        }
                    });
                    // if there were no partners selected ignore saving data.
                    if(partners.length > 0) {
                        this.data = {"partner": partners};
                    } else {
                        return false;
                    }
                }
            } else if (this.custom_save === "contact") {
                var contacts = [],
                    all_checkbox = $("input#all"),
                    all_checkboxes = $("#content input[type='checkbox']:not(#all)");
                // TODO: Can probably refactor this with partner's custom save (does same thing).
                if($(all_checkbox).is(":checked")) {
                    this.data = {"contact": ""};
                } else {
                    $(all_checkboxes).each(function(element) {
                        if($(all_checkboxes[element]).is(":checked")){
                            contacts.push(all_checkboxes[element].value);
                        }
                    });
                    // if there were no contacts selected ignore saving data.
                    if(contacts.length > 0) {
                        this.data = {"contact": contacts};
                    } else {
                        return false;
                    }
                }
            }
        }
    };
    this.load_data = function() {
        if(this.custom_save == undefined) {
            // run default load
            for(var key in this.data) {
                if(this.data.hasOwnProperty(key)) {
                    $("#"+key).val(this.data[key]);
                }
            }
        } else {
            // run exception load
            if(this.custom_save === "partner") {
                // if data.partner not all
                if(this.data.partner != "") {
                    var all_checkboxes = $("#content input"); // all checkboxes in content
                    // TODO: refactor this.
                    $(all_checkboxes).each(function(element) {
                        $(all_checkboxes[element]).prop("checked", false);
                    });
                    for(var i = 0; i < this.data.partner.length; i++) {
                        $("input[value='"+this.data.partner[i]+"']").prop("checked", true);
                    }
                }
            } else if(this.custom_save === "contact") {
                // if data.contact not all
                if(this.data.contact != "") {
                    var all_checkboxes = $("#content input"); // all checkboxes in content
                    // all are unchecked on load
                    // TODO: refactor this.
                    $(all_checkboxes).each(function(element) {
                        $(all_checkboxes[element]).prop("checked", false);
                    });
                    for(var i = 0; i < this.data.contact.length; i++) {
                        $("input[value='"+this.data.contact[i]+"']").prop("checked", true);
                    }
                }
            }
        }
    }
};

$(document).ready(function() {
    // Simulate page 1 (page 1 is where the user selects what types of reporting)
    var report = new Report(["PRM"]);
    report.next_page();

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
            // turn all chekcs off
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
