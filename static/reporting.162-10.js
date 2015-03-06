/*
Send the user a message when they try to unload the page saying their
progress will not be saved and will be lost.
TODO: uncomment this and give a more meaningful message. Commented out for development purposes.
window.addEventListener("beforeunload", function(e) {
    e.returnValue = "\\o/";
});
*/


// Handles storing data, rendering fields, and submitting report. See prototype functions
var Report = function(types) {
  this.types = types;
  this.data = {};
  this.fields = this.create_fields(types);
};


// Pulls the fields required for report type(s)
Report.prototype.create_fields = function(types) {
   var reports = {"prm":        [new Field("Select Date", "date"),
                                 new Field("State", "text"),
                                 new Field("City", "text"),
                                 new List("Select Partners", "partner"),
                                 new List("Select Contacts", "contact")],
                  "compliance": [new Field("test", "text"),
                                 new Field("test2", "text")]},
        fields = [],
        key;

  for (key in types) {
    if (reports.hasOwnProperty(types[key])) {
      fields.push.apply(fields, reports[types[key]]);
    }
  }
  return fields;
};


// Bind events for report, events that use the report object need to be here.
Report.prototype.bind_events = function() {
  var report = this;


  // Updates data field of Report. Also, if needed, updates Partner and Contact Lists
  $(document.body).on("change", "input:not([id$=-all-checkbox])", function(e) {
    var in_list = $(this).parents(".list-body").attr("id"),
        contact_wrapper = $("#contact-wrapper"),
        c_field = report.find_field("Select Contacts");

    // Check to see if the triggering even was in a list.
    if (typeof in_list !== "undefined") {
      var all_records = $(this).parents(".list-body").prev().children("input"),
          records = $($(this).parents(".list-body").find("input")),
          values = [];

      if (all_records.is(":checked")) {
        report.data[in_list] = "";
      } else {
        // iterate through all checkboxes and find all the ones that are checked
        // and add to data.
        $(records).each(function(element) {
          if ($(records[element]).is(":checked")) {
            values.push(records[element].value);
          }
        });
        // if there were no partners selected ignore saving data.
        if (values.length > 0) {
          report.data[in_list] = values;
        } else {
          // Suppose to return 0 contacts
          // List filter uses IDs which no object will ever have id=0
          report.data[in_list] = "0";
        }
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

    if(icon.hasClass("fa-plus-square-o")) {
      icon.removeClass("fa-plus-square-o").addClass("fa-minus-square-o");
      $(this).next(".list-body").slideDown();
    } else {
      icon.removeClass("fa-minus-square-o").addClass("fa-plus-square-o");
      $(this).next(".list-body").slideUp();
    }
  });


  $(document.body).on("click", ".list-body :checkbox", function(e) {
    e.stopPropagation();

    update_all_checkbox(this);
  });


  // Clicking on an li in the lists will click the checkbox.
  $(document.body).on("click", ".list-body li", function() {
    var checkbox = $(this).children("input");

    checkbox.prop("checked", !checkbox.prop("checked")).change();

    update_all_checkbox(this);
  });

  // Clicking on all "type" checkbox will check/uncheck all checkboxes in associated list.
  $(document.body).on("click", "input[id$=-all-checkbox]", function(e) {
    e.stopPropagation();
    var checkboxes = $(this).parent().next().find("input");

    checkboxes.prop("checked", $(this).prop("checked")).change();
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
    var data = {"csrfmiddlewaretoken": read_cookie("csrftoken"), "ignore_cache": true},
        url = location.protocol + "//" + location.host + "/reports/ajax/mypartners/contactrecord";
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
        $(".modal-body").html(JSON.stringify(data));
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

      // Replace _ with spaces
      key = key.replace(/_/g, " ");

      html += "<label>" + key + ":</label>";

      // If value is an object (aka a list).
      if (typeof value === "object") {
        var ul = $("<ul></ul>");

        // fill ul with li's.
        for (var i = 0; i < value.length; i++) {
          var name = $("#" + key + " input[value='" + value[i] + "']").next("span").html(),
              li = $("<li>" + name + "</li>");
          ul.append(li);
        }

        html += ul.prop("outerHTML");
      } else {
        html += value;
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
      i = 0;

  // for field in fields render.
  for (i; i < fields.length; i++) {
    html += fields[i].render();
  }

  html += "<br /><a id=\"show-modal\" class=\"btn\">Generate Report</a>";
  container.html(html);
};


var Field = function(label, type) {
  this.label = label;
  this.type = type;
};


// Outputs html based on type using jQuery.
Field.prototype.render = function() {
  var l = $("<label>" + this.label + "</label>"), // label for <input>
      wrapper = $("<div></div>"), // wrapping div
      html = '',
      input,
      date_widget,
      date_picker;

  if (this.type === "text") {
    input = $("<input id='" + this.label.toLowerCase().replace(/ /g, "_") + "' type='text' placeholder='"+ this.label +"' />");
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
    // TODO: ajax state dropdown
  }
  return html;
};


var List = function(label, type) {
  Field.call(this, label, type);
};


List.prototype = Object.create(Field.prototype);


// Outputs html based on type using jQuery.
// Runs ajax asynchronously to render associated lists.
List.prototype.render = function(filter) {
  var container = $("<div id='"+ this.type +"-header' class='list-header'></div>"),
      icon = $("<i class='fa fa-plus-square-o'></i>"),
      all_checkbox = $("<input id='"+ this.type +"-all-checkbox' type='checkbox' checked />"),
      record_count,
      html,
      body = $("<div id='"+ this.type +"' class='list-body' style='display: none;'></div>"),
      wrapper = $("<div id='"+ this.type +"-wrapper'></div>"),
      list = this;

  if (this.type === "contact") {
    record_count = $("<span style='display: none;'>(<span>0</span> Contacts Selected)</span>");
    container.append(icon).append(all_checkbox).append(" All Contacts ").append(record_count);
  } else if (this.type === "partner") {
    record_count = $("<span style='display: none;'>(<span>0</span> Partners Selected)</span>");
    container.append(icon).append(all_checkbox).append(" All Partners ").append(record_count);
  } else {
    record_count = $("<span style='display: none;'>(<span>0</span> "+ this.type +" Selected)</span>");
    container.append(icon).append(all_checkbox).append(" All " + this.type + " ").append(record_count);
  }

  wrapper.append(container).append(body);
  html = wrapper.prop("outerHTML");

  // Asynchronously renders a list of records based on list type.
  (function() {
    list.filter(list.type, filter);
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
    url += "/reports/ajax/mypartners/partner";
  } else if (type === "contact") {
    url += "/reports/ajax/mypartners/contact";
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
      for (var i = 0; i < data.records.length; i++) {
        record = data.records[i];
        li = $("<li><input type='checkbox' value='"+ record.pk +"' checked /> <span>"+ record.name +"</span></li>");

        // add record count to right of partners
        if (type === "partner") {
          li.append("<span class='pull-right'>"+ record.count +"</span>");
        }

        ul.append(li);
      }

      // render
      $("#"+ type + ".list-body").append(ul);
      $(selected).html(data.length).parent().show("fast");
    },
    error: function(e) {
      // TODO: change when testing is done to something more useful.
      console.error("Something horrible happened.");
    }
  });
};


$(document).ready(function() {
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
    $("#back").hide();
    $(".rpt-buttons").removeClass("no-show");
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
});


function update_all_checkbox(element) {
  var all_checkbox = $(element).parents("div.list-body").prev().children("input"),
      checkboxes = $(element).parents(".list-body").find("input"),
      checked = $(element).parents(".list-body").find(":checked");

  all_checkbox.prop("checked", checked.length === checkboxes.length);
}
