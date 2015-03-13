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
  var report = this;

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
  $(document.body).on("focus", "#report_name", function() {
    $(this).select();
  });


  // Updates data field of Report. Also, if needed, updates Partner and Contact Lists
  $(document.body).on("change", "input:not([id$=-all-checkbox]), select:not([class^=picker])", function(e) {
    var in_list = $(this).parents(".list-body").attr("id"),
        contact_wrapper = $("#contact-wrapper"),
        c_field = report.find_field("Select Contacts");

    // Check to see if the triggering even was in a list.
    if (typeof in_list !== "undefined") {
      var all_records = $(this).parents(".list-body").prev().children("input"),
          records = $($(this).parents(".list-body").find("input")),
          values = [];

      if (all_records.is(":checked") && $(this).is(":checked")) {
        report.data[in_list] = "";
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
        contact_wrapper.html(c_field.render(report.data)).children().unwrap();
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
        partner_wrapper.html(p_field.render(report.data)).children().unwrap();
        contact_wrapper.html(c_field.render(report.data)).children().unwrap();
      }
    }
  });


  // Slides the associated list up or down.
  $(document.body).on("click", ".list-header", function() {
    var icon = $(this).children("i");

    if (icon.hasClass("fa-plus-square-o")) {
      icon.removeClass("fa-plus-square-o").addClass("fa-minus-square-o");
    } else {
      icon.removeClass("fa-minus-square-o").addClass("fa-plus-square-o");
    }
    $(this).next(".list-body").stop(true, true).slideToggle();
  });


  $(document.body).on("click", ".list-body :checkbox", function(e) {
    e.stopPropagation();

    update_items_selected(this);
    update_all_checkbox(this);
  });


  // Clicking on an li in the lists will click the checkbox.
  $(document.body).on("click", ".list-body li", function() {
    var checkbox = $(this).children("input");

    checkbox.prop("checked", !checkbox.prop("checked")).change();

    update_items_selected(this);
    update_all_checkbox(this);
  });


  // Clicking on all "type" checkbox will check/uncheck all checkboxes in associated list.
  $(document.body).on("click", "input[id$=-all-checkbox]", function(e) {
    e.stopPropagation();
    var checkboxes = $(this).parent().next().find("input"),
        num_selected = $(this).siblings("span").children("span");

    // Update all checkboxes with this' current state.
    checkboxes.prop("checked", $(this).prop("checked")).change();

    // Update how many items in the list is selected based on this' current state. All or nothing.
    num_selected.html($(this).prop("checked") ? checkboxes.length : "0");
  });


  // Clicking this button will show the modal with human readable data to review.
  $(document.body).on("click", "#show-modal", function(e) {
    var modal = $("#report-modal"),
        body = modal.children(".modal-body"),
        footer = modal.children(".modal-footer");
    body.html(report.readable_data());
    modal.modal("show");
  });


  // Actually submits the report's data to create a Report object in db.
  $(document.body).on("click", "#gen-report", function(e) {
    var csrf = read_cookie("csrftoken"),
        data = {"csrfmiddlewaretoken": csrf, "ignore_cache": true},
        url = location.protocol + "//" + location.host + "/reports/ajax/render/mypartners/contactrecord";
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
      global: false,
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


// Changes report.data from having PKs in lists to show more human friendly data such as names.
Report.prototype.readable_data = function() {
  var data = this.data,
      html = '',
      key,
      value;

  for (key in data) {
    if (data.hasOwnProperty(key)) {
      value = data[key];

      // Replace all '_' instances with spaces
      key = key.replace(/_/g, " ");

      if (value) {
        html += "<label>" + key + ":</label>";
      }

      // If value is an object (aka a list).
      if (typeof value === "object") {
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
    html += fields[i].render();
  }

  html += "<br /><a id=\"show-modal\" class=\"btn\">Generate Report</a>";
  container.html(html);
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
      html = '',
      input,
      date_widget,
      date_picker;

  // Indication that the field is required.
  if (this.required) {
    l.append("<span style='color: red;'>*</span>");
  }

  if (this.type === "text") {
    input = $("<input id='" + this.label.toLowerCase().replace(/ /g, "_") + "' type='text' placeholder='"+ this.label +"' value='" + this.value + "' />");
    wrapper.append(l).append(input);
    html = wrapper.prop("outerHTML");
  } else if (this.type === "date") {
    date_widget = $("<div id='date-filter' class='filter-option'></div>").append("<div class='date-picker'></div>"),
    date_picker = $(date_widget).children("div")
                    .append("<input id='start_date' class='datepicker picker-left' type='text' placeholder='Start Date' />")
                    .append("<span id='activity-to-' class='datepicker'>to</span>")
                    .append("<input id='end_date' class='datepicker picker-right' type='text' placeholder='End Date' />");
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
List.prototype.render = function(filter) {
  var container = $("<div id='"+ this.type +"-header' class='list-header'></div>"),
      icon = $("<i class='fa fa-plus-square-o'></i>"),
      all_checkbox = $("<input id='"+ this.type +"-all-checkbox' type='checkbox' checked />"),
      record_count = $("<span style='display: none;'>(<span>0</span> "+ this.type.capitalize() +"s Selected)</span>"),
      body = $("<div id='"+ this.type +"' class='list-body' style='display: none;'></div>"),
      wrapper = $("<div id='"+ this.type +"-wrapper'></div>"),
      prm_fields = ["start_date", "end_date", "state", "city"],
      copied_filter = $.extend({}, filter),
      list = this,
      key,
      html;

  container.append(icon).append(all_checkbox).append(" All " + this.type.capitalize() + "s ").append(record_count);

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
    list.filter(list.type, copied_filter);
  })();

  return html;
};

// Renders a list of records based on type.
List.prototype.filter = function(type, filter) {
  "use strict";
  var url = location.protocol + "//" + location.host, // https://secure.my.jobs
      data = {"csrfmiddlewaretoken": read_cookie("csrftoken")};

  // if filter, add to data.
  if (typeof filter !== "undefined") {
    $.extend(data, filter);
  }

  // specific duties based on type.
  if (type === "partner") {
    // annotate how many records a partner has.
    $.extend(data, {"count": "contactrecord"});
    url += "/reports/ajax/get/mypartners/partner";
  } else if (type === "contact") {
    url += "/reports/ajax/get/mypartners/contact";
  }

  $.ajaxSettings.traditional = true;
  $.ajax({
    type: 'POST',
    url: url,
    data: $.param(data, true),
    dataType: "json",
    global: false,
    success: function(data) {
      var ul = $("<ul></ul>"),
          selected = $("[id^='" + type + "-header'] span span"),
          record,
          li;

      // fill ul with li's
      for (var i = 0; i < data.length; i++) {
        record = data[i];
        li = $("<li><input type='checkbox' value='"+ record.pk +"' checked /> <span>"+ record.name +"</span></li>");

        // add record count to right of partners
        if (type === "partner") {
          li.append("<span class='pull-right'>"+ record.count +"</span>");
        }

        ul.append(li);
      }

      // render
      $("#"+ type + ".list-body").html('').append(ul);
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


  // For date widget.
  $(document.body).on("click", ".datepicker",function(e) {
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
  sidebar.on("click", ".fa-eye", function() {
    var report_id = $(this).attr("id").split("-")[1];
    console.log("View Report ID: ", report_id);
  });


  // Clone Report
  sidebar.on("click", ".fa-copy", function() {
    var report_id = $(this).attr("id").split("-")[1];
    console.log("Clone Report ID: ", report_id);
  });


  // Export Report
  sidebar.on("click", ".fa-download", function() {
    var report_id = $(this).attr("id").split("-")[1];
    console.log("Export Report ID: ", report_id);
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
