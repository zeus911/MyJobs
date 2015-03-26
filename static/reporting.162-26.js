// Variable to get through beforeunload listener without displaying message.
var reload = false;

// Handles storing data, rendering fields, and submitting report. See prototype functions
var Report = function(types) {
  this.types = types;
  this.data = {};
  this.fields = this.create_fields(types);
};


// Pulls the fields required for report type(s)
// Field Params: label, type, required, value
Report.prototype.create_fields = function(types) {
   var reports = {"prm":        [new Field("Select Date", "date"),
                                 new Field("State", "state"),
                                 new Field("City", "text"),
                                 new List("Select Partners", "partner", true),
                                 new List("Select Contacts", "contact", true)]},
        fields = [],
        key;

  for (key in types) {
    if (reports.hasOwnProperty(types[key])) {
      fields.push.apply(fields, reports[types[key]]);
    }
  }
  fields.unshift(new Field("Report Name", "text", true, format_date(new Date())));
  return fields;
};


// Bind events for report, events that use the report object need to be here.
Report.prototype.bind_events = function() {
  var report = this,
      container = $("#main-container");

  // Send the user a message when they try to unload the page saying their
  // progress will not be saved and will be lost.
  /*
  window.addEventListener("beforeunload", function(e) {
    if (!reload) {
      e.returnValue = "You have unsaved changes!";
    }
  });
  */

  // Because this is pre-filled and will normally be a pretty long this
  // just selects text on focus for easy editing. UX-goodness
  container.on("focus", "#report_name", function() {
    $(this).select();
  });


  // Updates data field of Report. Also, if needed, updates Partner and Contact Lists
  container.on("change", "input:not([id$=-all-checkbox]), select:not([class^=picker])", function(e) {
    var in_list = $(this).parents(".list-body").attr("id"),
        contact_wrapper = $("#contact-wrapper"),
        c_field = report.find_field("Select Contacts");

    // Check to see if the triggering even was in a list.
    if (typeof in_list !== "undefined") {
      var all_records = $(this).parents(".list-body").prev().children("input"),
          records = $($(this).parents(".list-body").find("input")),
          values = [];

      if (all_records.is(":checked") && $(this).is(":checked")) {
        if (typeof report.data.partner !== "undefined") {
          delete report.data.partner;
        }
      } else {
        // iterate through all checkboxes and find all the ones that are checked
        // and add to data.
        $(records).each(function(element) {
          if ($(records[element]).is(":checked")) {
            values.push(records[element].value);
          }
        });

        // If false suppose to return 0 contacts
        // List filter uses IDs which no object will ever have id=0
        report.data[in_list] = values.length ? values : "0";
      }

      if (in_list === "partner") {
        if (typeof report.data.contact !== "undefined") {
          delete report.data.contact;
        }
        contact_wrapper.html(c_field.render(report)).children().unwrap();
      }
    } else {
      var partner_wrapper = $("#partner-wrapper"),
          p_field = report.find_field("Select Partners"),
          is_prm_field = function(e) {
            // This list will need to be updated if more is added to the PRM report
            // if they filter down partners/contacts
            var prm_field = ["start_date", "end_date", "state", "city"],
                e_id = $(e.currentTarget).attr("id");

            // returns true or false
            return (prm_field.indexOf(e_id) >= 0);
          };

      // Default update/save data
      report.data[$(e.currentTarget).attr("id")] = $(e.currentTarget).val();

      if (is_prm_field(e)) {
        if (typeof report.data.partner !== "undefined") {
          delete report.data.partner;
        }
        if (typeof report.data.contact !== "undefined") {
          delete report.data.contact;
        }
        partner_wrapper.html(p_field.render(report)).children().unwrap();
        contact_wrapper.html(c_field.render(report)).children().unwrap();
      }
    }
  });


  // For date widget.
  container.on("focus", ".datepicker", function(e) {
   $(this).pickadate({
     format: "mm/dd/yyyy",
     selectYears: true,
     selectMonths: true,
     today: false,
     clear: false,
     close: false,
     onOpen: function() {
       if (this.get("id") === "start-date") {
         var end_date = $("#end-date").val();
         this.set("max", new Date(end_date || new Date()));
       } else if (this.get("id") === "end-date") {
         var start_date = $("#start-date").val();
         this.set("min", new Date(start_date || new Date(0)));
       }
     }
   });
  });


  // Slides the associated list up or down.
  container.on("click", ".list-header", function() {
    var icon = $(this).children("i");

    if (icon.hasClass("fa-plus-square-o")) {
      icon.removeClass("fa-plus-square-o").addClass("fa-minus-square-o");
    } else {
      icon.removeClass("fa-minus-square-o").addClass("fa-plus-square-o");
    }
    $(this).next(".list-body").stop(true, true).slideToggle();
  });


  container.on("click", ".list-body :checkbox", function(e) {
    e.stopPropagation();

    update_items_selected(this);
    update_all_checkbox(this);
  });


  // Clicking on an li in the lists will click the checkbox.
  container.on("click", ".list-body li", function() {
    var checkbox = $(this).children("input");

    checkbox.prop("checked", !checkbox.prop("checked")).change();

    update_items_selected(this);
    update_all_checkbox(this);
  });


  // Clicking on all "type" checkbox will check/uncheck all checkboxes in associated list.
  container.on("click", "input[id$=-all-checkbox]", function(e) {
    e.stopPropagation();
    var checkboxes = $(this).parent().next().find("input"),
        num_selected = $(this).siblings("span").children("span"),
        i;

    for (i = 0; i < checkboxes.length; i++) {
      var checkbox = $(checkboxes[i]);
      checkbox.prop("checked", $(this).prop("checked"));

      // Run ajax on last checkbox to be changed.
      // Avoids running AJAX checkbox.length times but still triggers update event.
      if (i === checkboxes.length - 1) {
        checkbox.change();
      }
    }

    // Update how many items in the list is selected based on this' current state. All or nothing.
    num_selected.html($(this).prop("checked") ? checkboxes.length : "0");
  });


  // Clicking this button will show the modal with human readable data to review.
  container.on("click", "#show-modal", function(e) {
    var modal = $("#report-modal"),
        body = modal.children(".modal-body"),
        footer = modal.children(".modal-footer");

    if (typeof report.data['report_name'] === "undefined") {
      report.data['report_name'] = $("#report_name").val();
    }

    body.html(report.readable_data());
    modal.modal("show");
  });


  // Actually submits the report's data to create a Report object in db.
  $(document.body).on("click", "#gen-report", function(e) {
    var csrf = read_cookie("csrftoken"),
        data = {"csrfmiddlewaretoken": csrf},
        url = location.protocol + "//" + location.host + "/reports/view/mypartners/contactrecord";
    if (report.data) {
      $.extend(data, report.data);
    }
    if (data.contact) {
      var new_list = [];
      for (var i = 0; i < data.contact.length; i++) {
        var value = data.contact[i],
            name = $("#contact input[value='" + value + "']").next("span").html();
        new_list.push(name);
      }
      delete data.contact;
      data.contact_name = new_list;
    }
    $.ajaxSettings.traditional = true;
    $.ajax({
      type: 'POST',
      url: url,
      data: $.param(data, true),
      dataType: "json",
      success: function (data) {
        reload = true;
        var new_url = location.protocol + '//' + location.host + location.pathname,
            form = $('<form action="'+ new_url +'" method="POST" style="display: none;">' +
          '<input type="hidden" name="csrfmiddlewaretoken" value="' + csrf + '" />"' +
          '<input type="hidden" name="success" value="true" /> </form>');
        $('body').append(form);
        form.submit();
      }
    });
  });
};


Report.prototype.unbind_events = function() {
  $("#main-container").off("click");
  $(document.body).off("click", "#gen-report");
};


// Changes report.data from having PKs in lists to show more human friendly data such as names.
Report.prototype.readable_data = function() {
  var data = this.data,
      html = '',
      key,
      value;

  for (key in data) {
    if (data.hasOwnProperty(key)) {
      html += "<div>";
      value = data[key];

      // Replace all '_' instances with spaces
      key = key.replace(/_/g, " ");

      if (value) {
        html += "<label>" + key.capitalize() + ":</label>";
      }

      // If value is an object (aka a list). Check if not null as null is an object in js.
      if (typeof value === "object" && value !== null) {
        var items = [],
            i;

        // grab names associated by value.
        for (i = 0; i < value.length; i++) {
          items.push($("#" + key + " input[value='" + value[i] + "']").next("span").html());
        }

        html += "<ul><li>" + items.join('</li><li>') + '</li></ul>';
      } else {
        html += key === "state" ? $("#state option[value=" + value + "]").html() : value;
      }
      html += "</div>";
    }
  }
  if (typeof data.partner === "undefined") {
    if ($("#partner-all-checkbox").is(":checked")) {
      html += "<div><label>Partners:</label>All Partners</div>";
    }
  }

  if (typeof data.contact === "undefined") {
    if ($("#contact-all-checkbox").is(":checked")) {
      html += "<div><label>Contacts:</label>All Contacts</div>";
    }
  }

  return html;
};


// Takes a field label (or name) and finds the associated field/list/widget.
Report.prototype.find_field = function(field_label) {
  return ($.grep(this.fields, function(field) {
    return field.label === field_label;
  })[0]);
};


// Takes a list of Fields and renders them.
Report.prototype.render_fields = function(fields) {
  var container = $("#container"),
      html = '',
      i;

  // for field in fields render.
  for (i = 0; i < fields.length; i++) {
    html += fields[i].render(this);
  }

  html += "<div class=\"show-modal-holder\"><a id=\"show-modal\" class=\"btn primary\">Generate Report</a></div>";
  container.html(html);
};


Report.prototype.create_clone_report = function(json) {
  var key,
      value,
      field;

  for (key in json) {
    if (json.hasOwnProperty(key)) {
      value = json[key];

      if (key === "partner") {
        this.find_field("Select Partners").value = value;
        this.data[key] = value;
      } else if (key === "contact_name") {
        this.find_field("Select Contacts").value = value;
        this.data.contact = value;
      } else if (key.indexOf("date") > 0) {
        field = this.find_field("Select Date");
        if (field.value === "") {
          field.value = {"start_date": '', "end_date": ''};
        }
        field.value[key] = value;
        this.data[key] = value;
      } else {
        this.find_field(key.capitalize()).value = value;
        this.data[key] = value;
      }
    }
  }
};


var Field = function(label, type, required, value) {
  this.label = label;
  this.type = type;
  this.required = typeof required !== 'undefined';
  this.value = value || '';
};


// Outputs html based on type using jQuery.
Field.prototype.render = function() {
  var l = $("<label>" + this.label + "</label>"), // label for <input>
      wrapper = $("<div></div>"), // wrapping div
      field = this,
      html = '',
      input,
      date_widget,
      date_picker,
      start_date,
      to,
      end_date;

  // Indication that the field is required.
  if (this.required) {
    l.append("<span style='color: red;'>*</span>");
  }

  if (this.type === "text") {
    input = $("<input id='" + this.label.toLowerCase().replace(/ /g, "_") + "' type='text' placeholder='"+ this.label +"' value='" + this.value + "' />");
    wrapper.append(l).append(input);
    html = wrapper.prop("outerHTML");
  } else if (this.type === "date") {
    date_widget = $("<div id='date-filter' class='filter-option'></div>").append("<div class='date-picker'></div>");
    date_picker = $(date_widget).children("div");

    if (field.value) {
      start_date = $("<input id='start_date' class='datepicker picker-left' type='text' value='"+ field.value.start_date +"' placeholder='Start Date' />");
      end_date = $("<input id='end_date' class='datepicker picker-right' type='text' value='"+ field.value.end_date +"' placeholder='End Date' />");
    } else {
      start_date = $("<input id='start_date' class='datepicker picker-left' type='text' placeholder='Start Date' />");
      end_date = $("<input id='end_date' class='datepicker picker-right' type='text' placeholder='End Date' />");
    }
    to = $("<span id='activity-to-' class='datepicker'>to</span>");

    date_picker.append(start_date).append(to).append(end_date);
    date_widget.append(date_picker);
    html += l.prop("outerHTML");
    html += date_widget.prop("outerHTML");
  } else if (this.type === "state") {
    html += l.prop("outerHTML") + "<div class='state'></div>";
    (function() {
      $.ajax({
        type: "POST",
        url: location.protocol + "//" + location.host + "/reports/ajax/get-states",
        data: {"csrfmiddlewaretoken": read_cookie("csrftoken")},
        success: function(data) {
          $(".state").html(data);
          if (field.value) {
            $(".state").find("select").val(field.value);
          }
        }
      });
    })();
  }
  return html;
};


var List = function(label, type, required) {
  Field.call(this, label, type, required);
};


List.prototype = Object.create(Field.prototype);


// Outputs html based on type using jQuery.
// Runs ajax asynchronously to render associated lists.
List.prototype.render = function(report) {
  var container = $("<div id='"+ this.type +"-header' class='list-header'></div>"),
      icon = $("<i class='fa fa-plus-square-o'></i>"),
      all_checkbox = $("<input id='"+ this.type +"-all-checkbox' type='checkbox' checked />"),
      record_count = $("<span style='display: none;'>(<span>0</span> "+ this.type.capitalize() +"s Selected)</span>"),
      body = $("<div id='"+ this.type +"' class='list-body' style='display: none;'></div>"),
      wrapper = $("<div id='"+ this.type +"-wrapper'></div>"),
      prm_fields = ["start_date", "end_date", "state", "city", "partner"],
      copied_filter,
      list = this,
      key,
      html;

  if (report.data !== "") {
    copied_filter = $.extend({}, report.data);
  }

  if (this.value) {
    all_checkbox = $("<input id='"+ this.type +"-all-checkbox' type='checkbox' />");
  } else {
    all_checkbox = $("<input id='"+ this.type +"-all-checkbox' type='checkbox' checked />");
  }

  container.append(icon).append(all_checkbox).append(" All " + list.type.capitalize() + "s ").append(record_count);

  wrapper.append(container).append(body);
  html = wrapper.prop("outerHTML");

  if (this.type === "partner" || this.type === "contact") {
    for (key in copied_filter) {
      if (copied_filter.hasOwnProperty(key)) {
        if (prm_fields.indexOf(key) === -1) {
          delete copied_filter[key];
        }
      }
    }
  }

  // Asynchronously renders a list of records based on list type.
  (function() {
    list.filter(copied_filter);
  })();

  return html;
};

// Renders a list of records based on type.
List.prototype.filter = function(filter) {
  "use strict";
  var url = location.protocol + "//" + location.host, // https://secure.my.jobs
      data = {},
      list = this;

  // if filter, add to data.
  if (typeof filter !== "undefined") {
    $.extend(data, filter);
  }

  // specific duties based on type.
  if (list.type === "partner") {
    // annotate how many records a partner has.
    $.extend(data, {"count": "contactrecord"});
    url += "/reports/ajax/mypartners/partner";
    if (typeof data["partner"] !== "undefined") {
      delete data["partner"];
    }
  } else if (list.type === "contact") {
    url += "/reports/ajax/mypartners/contact";
  }

  $.ajaxSettings.traditional = true;
  $.ajax({
    type: 'GET',
    url: url,
    data: $.param(data, true),
    dataType: "json",
    global: false,
    success: function(data) {
      var ul = $("<ul></ul>"),
          selected = $("[id^='" + list.type + "-header'] span span"),
          record,
          li;

      // fill ul with li's
      for (var i = 0; i < data.length; i++) {
        record = data[i];

        li = $("<li><input type='checkbox' value='"+ record.pk +"' /> <span>"+ record.name +"</span></li>");
        li.find("input").prop("checked", Boolean(!list.value));

        // add record count to right of partners
        if (list.type === "partner") {
          li.append("<span class='pull-right'>"+ record.count +"</span>");
        }

        ul.append(li);
      }

      // render
      $("#"+ list.type + ".list-body").html('').append(ul);

      if (typeof list.value === "string" && list.value !== "") {
        list.value = [list.value];
      }

      if (list.value) {
        if (list.type === "partner") {
          for (var j = 0; j < list.value.length; j++) {
            $("input[value~=" + list.value[j] + "]").prop("checked", true);
          }
        } else if (list.type === "contact") {
          for (var k = 0; k < list.value.length; k++) {
            $("li span:contains(" + list.value[k] + ")").siblings("input").prop("checked", true);
          }
        }
      }

      $(selected).html(data.length).parent().show("fast");
    },
    error: function(e) {
      // TODO: change when testing is done to something more useful.
      console.error("Something horrible happened.");
    }
  });
};


// Capitalize first letter of a string.
String.prototype.capitalize = function() {
  return this.charAt(0).toUpperCase() + this.slice(1);
};


$(document).ready(function() {
  var sidebar = $(".sidebar");

  $(document.body).on("click", "#start-report:not(.disabled)", function(e) {
    e.preventDefault();
    var choices = $("#choices input[type='checkbox']:checked"),
        types = [],
        i = 0,
        report;

    // fill types with choices that are checked, see selector.
    for (i; i < choices.length; i++) {
      types.push(choices[i].value.toLowerCase());
    }

    // Create js Report object and set up next step.
    report = new Report(types);
    report.bind_events();
    $("#container").addClass("rpt-container");
    report.render_fields(report.fields);
  });


  // On initial page, when a type gets checked remove disabled from "Next" button.
  $(document.body).on("click", "#choices input[type='checkbox']:checked", function() {
    $("#start-report").removeClass("disabled");
  });


  // On initial page, when a checkbox is unchecked look to see if any others are checked.
  // If not then disable "Next" button.
  $(document.body).on("click", "#choices input[type='checkbox']:not(:checked)", function() {
    var checkboxes = $("#choices input[type='checkbox']");
    if (!checkboxes.is(":checked")) {
      $("#start-report").addClass("disabled");
    }
  });

  // View Report
  sidebar.on("click", ".report > a, .fa-eye", function() {
    var report_id = $(this).attr("id").split("-")[1],
        data = {"id": report_id},
        url = location.protocol + "//" + location.host; // https://secure.my.jobs

    $.ajax({
      type: "GET",
      url: url + "/reports/view/mypartners/contactrecord",
      data: data,
      success: function(data) {
        var contacts = data.contacts,
            communications = data.communications || 0,
            emails = data.emails || 0,
            pss = data.searches || 0,
            calls = data.calls || 0,
            meetings = data.meetings || 0,
            referrals = data.referrals || 0,
            applications = data.applications || 0,
            interviews = data.interviews || 0,
            hires = data.hires || 0,
            pChartInfo = {0: {'name': "Emails",            'count': emails,   'color': "#5EB95E"},
                          1: {'name': "PSS Emails",        'count': pss,      'color': "#4BB1CF"},
                          2: {'name': "Phone Calls",       'count': calls,    'color': "#FAA732"},
                          3: {'name': "Meetings & Events", 'count': meetings, 'color': "#5F6C82"}},
            bChartInfo = {0: {'name': "Applications", 'count': applications, 'style': "color: #5EB95E"},
                          1: {'name': "Interviews",   'count': interviews,   'style': "color: #4BB1CF"},
                          2: {'name': "Hires",        'count': hires,        'style': "color: #FAA732"},
                          3: {'name': "Records",      'count': referrals,    'style': "color: #5F6C82"}};

        // Grab google's jsapi to load chart files.
        $.getScript("https://www.google.com/jsapi", function() {
          // Had to use 'callback' with google.load otherwise after load google makes a new document
          // with just <html> tags.
          google.load("visualization", "1.0", {'packages':["corechart"], 'callback': function() {
            var pDataTable = [['Records', 'All Records']], // p for pieChart
                bDataTable = [['Activity', 'Amount', {'role': 'style'}]], // b for barChart
                $mainContainer = $("#main-container"),// the container everything goes in
                pSliceOptions = {}, // slice options for pieChart
                pLegend = [], // array that will hold the report-boxes for pieChart
                bLegend = [], // array that will hold the report-boxes for barChart
                pChartData,
                pKey,
                pValue,
                pBox,
                pOptions,
                pChart,
                $pLegend,
                $pChart,
                bChartData,
                bValue,
                bKey,
                bBox,
                bOptions,
                bChart,
                $bLegend,
                topThreeRow,
                restRow,
                contactContainer,
                i;

            $mainContainer.html('')
              .append("<div class='span6'><h4>Communication Activity</h4><div id='d-chart'></div>" +
                      "</div><div class='span6'><h4>Referral Activity</h4><div id='b-chart'></div></div>");

            for (pKey in pChartInfo) {
              if (pChartInfo.hasOwnProperty(pKey)) {
                pValue = pChartInfo[pKey];
                pDataTable.push([pValue.name, pValue.count]);

                // Used for PieChart to give data 'slices' color.
                pSliceOptions[pKey] = {'color': pValue.color};

                // Create legend boxes
                pBox = $('<div class="report-box" style="background-color: ' +
                         pValue.color + '"><div class="big-num">' + pValue.count +
                         '</div><div class="reports-record-type">' + pValue.name + '</div></div>');
                pLegend.push(pBox);
              }
            }

            pChartData = google.visualization.arrayToDataTable(pDataTable);
            pOptions = pieOptions(330, 350, 12, 12, 300, 330, 0.6, pSliceOptions, true);
            pChart = new google.visualization.PieChart(document.getElementById('d-chart'));
            pChart.draw(pChartData, pOptions);

            $pChart = $("#d-chart > div");
            $pChart.append("<div class='chart-box-holder legend'></div>");
            $pLegend = $("#d-chart .legend");
            pLegend.forEach(function(element) {
              $pLegend.append(element);
            });

            $pChart.append('<div class="piehole report"><div class="piehole-big">' + communications +
                           '</div><div class="piehole-topic">Contact Records</div></div>');

            for (bKey in bChartInfo) {
              if (bChartInfo.hasOwnProperty(bKey)) {
                bValue = bChartInfo[bKey];
                bDataTable.push([bValue.name, bValue.count, bValue.style]);

                bBox = $('<div class="report-box" style="background-' + bValue.style +
                         '"><div class="big-num">' + bValue.count +
                         '</div><div class="reports-record-type">' + bValue.name + '</div></div>');
                bLegend.push(bBox);
              }
            }

            bChartData = google.visualization.arrayToDataTable(bDataTable);
            bOptions = {title: 'Referral Records', width: 356, height: 360, legend: { position: "none" },
                        chartArea: {top: 22, left: 37, height: 270, width: 290},
                        animation: {startup: true, duration: 400}};
            bChart = new google.visualization.ColumnChart(document.getElementById('b-chart'));
            bChart.draw(bChartData, bOptions);

            $bLegend = $('<div class="chart-box-holder legend"></div>').append(function() {
              return bLegend.map(function(element) {
                return element.prop("outerHTML");
              }).join('');
            });

            $("#b-chart > div").append($bLegend);

            // Show the top three contacts in a different format than the rest.
            topThreeRow = $('<div class="row"></div>').append(function() {
              var html = '',
                  cLength = contacts.length,
                  contact,
                  name,
                  email,
                  cReferrals,
                  commRecords,
                  div,
                  topLength;

              // Determine how long topLength should be.
              topLength = (cLength > 3) ? 3 : cLength;

              // Just run for the first 3 contacts.
              for (i = 0; i < topLength; i++) {
                // remove first contact in array, returns the removed contact.
                contact = contacts.shift();
                name = contact.contact_name;
                email = contact.contact_email;
                cReferrals = contact.referrals;
                commRecords = contact.records;

                // create container
                div = $('<div class="span4 panel top-contacts"></div>');
                div.append('<div class="name">' + name + '</div><div>' + email + '</div><div class="top-three-box-container">' +
                           '<div class="report-box small"><div class="big-num">' + commRecords +
                           '</div><div class="reports-record-type">Contact Records</div></div>' +
                           '<div class="report-box small"><div class="big-num">' + cReferrals +
                           '</div><div class="reports-record-type">Referral Records</div></div></div>');

                // add the rendered html as a string.
                html += div.prop("outerHTML");
              }
              return html;
            });

            // Don't generate a table if cLength = 0
            if (contacts.length) {
              restRow = $('<div class="row"></div>').append(function() {
                var div = $('<div class="span12"></div>'),
                    table = $('<table class="table table-striped report-table"><thead><tr><th>Name</th>' +
                              '<th>Email</th><th>Contact Records</th><th>Referral Reocrds</th>' +
                              '</tr></thead></table>'),
                    tbody = $('<tbody></tbody>');
                tbody.append(function() {
                  // turn each element into cells of a table then join each group of cells with rows.
                  return "<tr>" + contacts.map(function(contact) {
                    return "<td>" + contact.contact_name + "</td><td>" + contact.contact_email +
                           "</td><td>" + contact.records + "</td><td>" + contact.referrals + "</td>";
                  }).join('</tr><tr>') + "</tr>";
                });
                return div.append(table.append(tbody));
              });
            } else {
              // Make sure topThreeRow didn't run before saying there are no records.
              if (topThreeRow.find("div.top-contacts").length === 0) {
                restRow = $('<div class="row"><div class="span12">This report has no contacts with records.</div></div>');
              }
            }

            contactContainer = $('<div id="report-contacts" class="span12"></div>').append(topThreeRow).append(restRow);
            $("#main-container").append(contactContainer);
          }});
        });
      }
    });
  });


  // Clone Report
  sidebar.on("click", ".fa-copy", function() {
    var report_id = $(this).attr("id").split("-")[1],
        data = {"csrfmiddlewaretoken": read_cookie("csrftoken"),
                "id": report_id},
        url = location.protocol + "//" + location.host; // https://secure.my.jobs

    $.ajax({
      type: "GET",
      url: url + "/reports/ajax/get-inputs",
      data: data,
      dataType: "json",
      success: function(data) {
        var report = new Report(["prm"]);
        report.create_clone_report(data);
        report.unbind_events();
        report.bind_events();
        $("#container").addClass("rpt-container");
        report.render_fields(report.fields);
      }
    });
  });

  // View Archive
  sidebar.on("click", "#report-archive", function() {
    var data = {"csrfmiddlewaretoken": read_cookie("csrftoken")};
    $.ajax({
      type: "POST",
      url: "archive",
      data: data,
      success: function(data) {
        $("#main-container").html(data);
      }
    });
  });
});


function format_date(date) {
  var year = date.getFullYear(),
      month = date.getMonth(),
      day = date.getDate(),
      hours = date.getHours(),
      minutes = date.getMinutes(),
      seconds = date.getSeconds(),
      milliseconds = date.getMilliseconds();

  function turn_two_digit(value) {
    return value < 10 ? "0" + value : value;
  }

  month = turn_two_digit(parseInt(month) + 1);
  day = turn_two_digit(day);
  hours = turn_two_digit(hours);
  minutes = turn_two_digit(minutes);
  seconds = turn_two_digit(seconds);

  return year + "-" + month + "-" + day + " " + hours + ":" + minutes + ":" + seconds + "." + milliseconds;
}


function update_all_checkbox(element) {
  var all_checkbox = $(element).parents("div.list-body").prev().children("input"),
      checkboxes = $(element).parents(".list-body").find("input"),
      checked = $(element).parents(".list-body").find(":checked");

  all_checkbox.prop("checked", checked.length === checkboxes.length);
}


function update_items_selected(element) {
  var checked = $(element).parents(".list-body").find(":checked"),
      num_selected = $(element).parents(".list-body").prev().children("span").children("span");

  num_selected.html(checked.length);
}


function pieOptions(height, width, chartArea_top, chartArea_left, chartArea_height, chartArea_width,
                    piehole_radius, slice_colors, show_tooltips) {
  var options = {legend: 'none', pieHole: piehole_radius, pieSliceText: 'none',
                 height: height, width: width,
                 chartArea: {top:chartArea_top, left:chartArea_left,
                             height: chartArea_height, width: chartArea_width},
                 slices: slice_colors
                };
  if(!show_tooltips) {
    options.tooltip = { trigger: 'none' };
  }
  return options;
}
