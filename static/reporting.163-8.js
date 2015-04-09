window.onpopstate = function(event) {
  var state = event.state,
      $sidebar = $(".sidebar"),
      historyNew,
      historyClone,
      inputs,
      report;

  if (state.page && state.page === 'overview') {
    navigation = false;
    renderOverview();
  } else if (state.page && state.page === 'new') {
    historyNew = function() {
      report = new Report(state.report.types);
      report.unbindEvents().bindEvents();
      $("#container").addClass("rpt-container");
      report.renderFields(report.fields);
      renderNavigation();
    };

    navigation = true;
    $sidebar.length > 0 ? historyNew() : renderOverview(historyNew);
  } else if (state.page && state.page === 'view-report') {
    var callback = function() {
      renderNavigation(true);
    };
    navigation = true;
    renderGraphs(state.reportId, callback);
  } else if (state.page && state.page === 'report-archive') {
    navigation = true;
    renderArchive(renderNavigation);
  } else if (state.page && state.page === 'report-download') {
    renderDownload(state.report);
  } else if (state.page && state.page === 'clone') {
    historyClone = function() {
      inputs = state.inputs;
      report = new Report(["prm"]);
      report.createCloneReport(inputs);
      report.unbindEvents().bindEvents();
      $("#container").addClass("rpt-container");
      report.renderFields(report.fields);
      renderNavigation();
    };

    navigation = true;
    $sidebar.length > 0 ? historyClone() : renderOverview(historyClone);
  }
};

// Determines if IE is being used. If it is IE returns IE version #. If not will return false.
var modernBrowser = !(isIE() && isIE() < 10);

// Used to get through beforeunload listener without displaying message.
var reload = false;

// Determines if a navigation bar is needed.
var navigation = false;

// Handles storing data, rendering fields, and submitting report. See prototype functions
var Report = function(types) {
  this.types = types;
  this.data = {};
  this.fields = this.createFields(types);
};

// checklist  values
var checklists = {
  'contact_type': [
    {'value': 'email', 'label': 'Email', 'checked': true},
    {'value': 'phone', 'label': 'Phone Call', 'checked': true},
    {'value': 'meetingorevent', 'label': 'Meeting or Event', 'checked': true},
    {'value': 'job', 'label': 'Job Followup', 'checked': true},
    {'value': 'pssemail', 'label': 'Saved Search Email', 'checked': true}
  ]
};


// Pulls the fields required for report type(s)
// Field Params: label, type, required, value
Report.prototype.createFields = function(types) {
  var reports = {"prm": [new Field(this, "Select Date", "date"),
                         new Field(this, "State", "state"),
                         new Field(this, "City", "text"),
                         new Field(this, "Contact Type", "checklist", false, checklists.contact_type),
                         new List(this, "Select Partners", "partner", true),
                         new List(this, "Select Contacts", "contact", true)]},
        fields = [],
        key;

  for (key in types) {
    if (reports.hasOwnProperty(types[key])) {
      fields.push.apply(fields, reports[types[key]]);
    }
  }
  fields.unshift(new Field(this, "Report Name", "text", true, formatDate(new Date())));
  return fields;
};


// Bind events for report, events that use the report object need to be here.
Report.prototype.bindEvents = function() {
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


  // Populate contact types from selected check boxes
  container.on("change", "input#contact_type", function(e) {
    var $checkboxes = $("input#contact_type"),
        $checked = $("input#contact_type:checked"),
        $allCheckbox = $("input#all_contact_type");

    var values = $.map($("input#contact_type:checked"), function(item, index) {
      return $(item).val();
    });

    $allCheckbox.prop("checked", $checkboxes.length === $checked.length);
    report.data.contact_type = values.length ? values : "0";
  });

  container.on("change", "input#all_contact_type", function(e) {
    var $checkboxes = $("input#contact_type");

    $checkboxes.prop("checked", $(this).is(":checked"));
    $.each($checkboxes, function(index, value) {
      if (index === $checkboxes.length - 1) {
        $(this).change();
      }
    });
  });


  // Updates data field of Report. Also, if needed, updates Partner and Contact Lists
  container.on("change", "input:not([id$=-all-checkbox]), select:not([class^=picker])", function(e) {
    var in_list = $(this).parents(".list-body").attr("id"),
        contact_wrapper = $("#contact-wrapper"),
        c_field = report.findField("Select Contacts"),
        ignore_data = ['contact_type', 'all_contact_type'];

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
          p_field = report.findField("Select Partners"),
          is_prm_field = function(e) {
            // This list will need to be updated if more is added to the PRM report
            // if they filter down partners/contacts
            var prm_field = ["start_date", "end_date", "contact_type", "state", "city"],
                e_id = $(e.currentTarget).attr("id");

            // returns true or false
            return (prm_field.indexOf(e_id) >= 0);
          };

      // Default update/save data
      if (ignore_data.indexOf($(e.currentTarget).attr("id")) === -1) {
        report.data[$(e.currentTarget).attr("id")] = $(e.currentTarget).val();
      }

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

    updateItemsSelected(this);
    updateAllCheckbox(this);
  });


  // Clicking on an li in the lists will click the checkbox.
  container.on("click", ".list-body li", function() {
    var checkbox = $(this).children("input");

    checkbox.prop("checked", !checkbox.prop("checked")).change();

    updateItemsSelected(this);
    updateAllCheckbox(this);
  });


  // Clicking on all "type" checkbox will check/uncheck all checkboxes in associated list.
  container.on("click", "input[id$=-all-checkbox]", function(e) {
    e.stopPropagation();
    var checkboxes = $(this).parent().next().find("input"),
        $recordCount = $(".record-count"),
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
    $recordCount.html($(this).prop("checked") ? checkboxes.length : "0");
    updateShowModal();
  });


  // Clicking this button will show the modal with human readable data to review.
  container.on("click", "#show-modal:not(.disabled)", function(e) {
    var modal = $("#report-modal"),
        body = modal.children(".modal-body"),
        footer = modal.children(".modal-footer");

    if (typeof report.data.report_name === "undefined") {
      report.data.report_name = $("#report_name").val();
    }

    body.html(report.readable_data());
    modal.modal("show");
  });

  container.on("click", "#cancel-modal", function() {
    if (modernBrowser) {
      history.back();
    } else {
      renderOverview();
    }
  });


  // Actually submits the report's data to create a Report object in db.
  $("body").on("click", "#gen-report", function(e) {
    var csrf = read_cookie("csrftoken"),
        data = {"csrfmiddlewaretoken": csrf},
        url = location.protocol + "//" + location.host + "/reports/view/mypartners/contactrecord",
        newList = [];
    if (report.data) {
      $.extend(data, report.data);
    }
    if (data.contact) {
      for (var i = 0; i < data.contact.length; i++) {
        var value = data.contact[i],
            name = $("#contact input[value='" + value + "']").next("span").html();
        newList.push(name);
      }
      delete data.contact;
      data.contact_name = newList;
    }
    $.ajaxSettings.traditional = true;
    $.ajax({
      type: 'POST',
      url: url,
      data: $.param(data, true),
      success: function (data) {
        reload = true;
        window.location = location.protocol + '//' + location.host + location.pathname;
      }
    });
  });

  return this;
};


Report.prototype.unbindEvents = function() {
  $("#main-container").off("click change");
  $("body").off("click", "#gen-report");

  return this;
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

        if (key === "contact type") {
          value = $.map(checklists.contact_type, function(item, index) {
            if (value.indexOf(item.value) > 0) {
              return item.label;
            }
          });

          var $all = $("input[name='checklist[]']"),
              $checked = $("input[name='checklist[]']:checked");

          if ($all.length === $checked.length) {
            html += ": All Contact Types";
          } else {
            html += "<ul class='short-list'><li>" + value.join("</li><li>") + "</li></ul>";
          }
        } else {
          for (i = 0; i < value.length; i++) {
            items.push($("#" + key + " input[value='" + value[i] + "']").next("span").html());
          }

          html += "<ul class='short-list'><li>" + items.join('</li><li>') + '</li></ul>';
        }
      } else {
        html += key === "state" ? $("#state option[value=" + value + "]").html() : value;
      }
      html += "</div>";
    }
  }

  if (typeof data.contact_type === "undefined") {
    html += "<div><label>Contact type:</label>All Contact Types</div>";
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
Report.prototype.findField = function(field_label) {
  return ($.grep(this.fields, function(field) {
    return field.label === field_label;
  })[0]);
};


// Takes a list of Fields and renders them.
Report.prototype.renderFields = function(fields) {
  var container = $("#container"),
      html = '',
      i;

  // for field in fields render.
  for (i = 0; i < fields.length; i++) {
    html += fields[i].render(this);
  }

  html += "<div class='show-modal-holder'><a id='cancel-modal' class='btn secondary'>Cancel</a><a id='show-modal' class='btn primary'>Generate Report</a></div>";
  container.html(html);
};


Report.prototype.createCloneReport = function(json) {
  var key,
      value,
      field;

  for (key in json) {
    if (json.hasOwnProperty(key)) {
      value = json[key];

      if (key === "partner") {
        this.findField("Select Partners").value = value;
        this.data[key] = value;
      } else if (key === "contact_name") {
        this.findField("Select Contacts").value = value;
        this.data.contact = value;
      } else if (key.indexOf("date") > 0) {
        field = this.findField("Select Date");
        if (field.value === "") {
          field.value = {"start_date": '', "end_date": ''};
        }
        field.value[key] = value;
        this.data[key] = value;
      } else if (key === "contact_type") {
        var values = checklists.contact_type;

        $.map(values, function(item, index) {
          item.checked = value.indexOf(item.value) !== -1;
        });

        field = this.findField("Contact Type").value = values;
        this.data[key] = value;
      } else {
        this.findField(key.capitalize()).value = value;
        this.data[key] = value;
      }
    }
  }

  return this;
};


var Field = function(report, label, type, required, value) {
  this.report = report
  this.label = label;
  this.type = type;
  this.required = !!required || false;
  this.value = value || '';
};


// Outputs html based on type using jQuery.
Field.prototype.render = function() {
  var l = $("<label>" + this.label + "</label>"), // label for <input>
      $wrapper = $("<div></div>"), // wrapping div
      field = this,
      html = '',
      input,
      dateWidget,
      datePicker,
      start_date,
      to,
      end_date;

  // Indication that the field is required.
  if (this.required) {
    l.append("<span style='color: red;'>*</span>");
  }

  if (this.type === "text") {
    input = "<input id='" + this.label.toLowerCase().replace(/ /g, "_") + "' type='text' placeholder='"+ this.label + "' value='" + this.value + "' />";
    $wrapper.append(l).append(input);
    html = $wrapper.prop("outerHTML");
  } else if (this.type === "date") {
    dateWidget = $("<div id='date-filter' class='filter-option'></div>").append("<div class='date-picker'></div>");
    datePicker = $(dateWidget).children("div");

    if (field.value) {
      start_date = "<input id='start_date' class='datepicker picker-left' type='text' value='" + field.value.start_date + "' placeholder='Start Date' />";
      end_date = "<input id='end_date' class='datepicker picker-right' type='text' value='" + field.value.end_date + "' placeholder='End Date' />";
    } else {
      start_date = "<input id='start_date' class='datepicker picker-left' type='text' placeholder='Start Date' />";
      end_date = "<input id='end_date' class='datepicker picker-right' type='text' placeholder='End Date' />";
    }
    to = "<span id='activity-to-' class='datepicker'>to</span>";

    datePicker.append(start_date).append(to).append(end_date);
    dateWidget.append(datePicker);
    html += l.prop("outerHTML");
    html += dateWidget.prop("outerHTML");
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
  } else if (field.type === "checklist") {
    var field_label = field.label.toLowerCase().replace(/ /g, "_"),
        all_checked = field.value.every(function(item, index, array) {
          return item.checked;
        });

    input = $.map(field.value, function(item, index) {
      return "<input id='" + field_label +
             "'type='checkbox' name='checklist[]' value='" + item.value +
             (item.checked ? "' checked />" : "' />") + item.label;
    }).join("");

    input = "<input id='all_" + field_label +
            "'type='checkbox' name='checklist[]' value='all' " +
            (all_checked ? "' checked />" : "' />") + "All" + input;

    $wrapper.attr("id", field_label);
    $wrapper.append(l).append(input);
    $wrapper.children("input").css("margin", "10px 5px");
    html = $wrapper.prop("outerHTML");

    field.report.data[field_label] = $.map(field.value, function(item, index) {
      return item.value;
    });
  }
  return html;
};


var List = function(report, label, type, required) {
  Field.call(this, report, label, type, required);
};


List.prototype = Object.create(Field.prototype);


// Outputs html based on type using jQuery.
// Runs ajax asynchronously to render associated lists.
List.prototype.render = function(report) {
  var container = $("<div id='"+ this.type +"-header' class='list-header'></div>"),
      icon = $("<i class='fa fa-plus-square-o'></i>"),
      allCheckbox = $("<input id='"+ this.type +"-all-checkbox' type='checkbox' checked />"),
      $recordCount = $("<span style='display: none;'>(<span class='record-count'>0</span> "+ this.type.capitalize() +"s Selected)</span>"),
      body = $("<div id='"+ this.type +"' class='list-body' style='display: none;'></div>"),
      wrapper = $("<div id='"+ this.type +"-wrapper'></div>"),
      prmFields = ["start_date", "end_date", "state", "city", "contact_type", "partner"],
      copiedFilter,
      list = this,
      key,
      html;

  if (report.data !== "") {
    copiedFilter = $.extend({}, report.data);
  }

  if (this.value) {
    allCheckbox = $("<input id='"+ this.type +"-all-checkbox' type='checkbox' />");
  } else {
    allCheckbox = $("<input id='"+ this.type +"-all-checkbox' type='checkbox' checked />");
  }

  container.append(icon).append(allCheckbox).append(" All " + list.type.capitalize() + "s ").append($recordCount);

  wrapper.append(container).append(body);
  html = wrapper.prop("outerHTML");

  if (this.type === "partner" || this.type === "contact") {
    for (key in copiedFilter) {
      if (copiedFilter.hasOwnProperty(key)) {
        if (prmFields.indexOf(key) === -1) {
          delete copiedFilter[key];
        }
      }
    }
  }

  // Asynchronously renders a list of records based on list type.
  (function() {
    list.filter(copiedFilter);
  })();

  return html;
};

// Renders a list of records based on type.
List.prototype.filter = function(filter) {
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
    $.extend(data, {"count": "contactrecord",
                    "values": ["pk", "name", "count"]}
    );
    url += "/reports/ajax/mypartners/partner";

    if (typeof data.partner !== "undefined") {
      delete data.partner;
    }
  } else if (list.type === "contact") {
    url += "/reports/ajax/mypartners/contact";
    $.extend(data, {"values": ["name", "email"]});
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
          recordCount = $("[id^='" + list.type + "-header'] .record-count"),
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

        if (list.type === "contact" && record.email) {
          li.append(" <span class='small'>("+ record.email + ")</span>");
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

      $(recordCount).html(data.length).parent().show("fast");
      updateShowModal();
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
  var subpage = $(".subpage");

  $("#choices input[type='checkbox']:checked").prop("checked", false);

  if (modernBrowser) {
    history.replaceState({'page': 'overview'}, "Report Overview");
  }

  subpage.on("click", "#start-report:not(.disabled)", function(e) {
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
    if (modernBrowser) {
      history.pushState({'page': 'new', 'report': report}, 'Create Report');
    }
    navigation = true;
    renderNavigation();
    report.unbindEvents().bindEvents();
    $("#container").addClass("rpt-container");
    report.renderFields(report.fields);
  });

  subpage.on("click", "#choices input[type='checkbox']", function() {
    var $checkboxes = $("#choices input[type='checkbox']"),
        $startReport = $("#start-report");

    if ($checkboxes.is(":checked")) {
      $startReport.removeClass("disabled");
    } else {
      $startReport.addClass("disabled");
    }
  });

  // View Report
  subpage.on("click", ".report > a, .fa-eye, .view-report", function() {
    var report_id,
        callback = function() {
          renderNavigation(true);
        };

    if ($(this).attr("id") !== undefined) {
      report_id = $(this).attr("id").split("-")[1];
    } else {
      report_id = $(this).parents("tr").data("report");
    }

    if (modernBrowser) {
      history.pushState({'page': 'view-report', 'reportId': report_id}, 'View Report');
    }

    navigation = true;
    renderGraphs(report_id, callback);
  });

  subpage.on("click", ".report > a, .fa-download", function() {
    var report_id = $(this).attr("id").split("-")[1];

    history.pushState({'page': 'report-download', 'report': report_id}, 'Download Report');

    renderDownload(report_id);
  });


  // Clone Report
  subpage.on("click", ".fa-copy, .clone-report", function() {
    var data = {},
        url = location.protocol + "//" + location.host, // https://secure.my.jobs
        cloneReport = function() {
          $.ajax({
            type: "GET",
            url: url + "/reports/ajax/get-inputs",
            data: data,
            dataType: "json",
            success: function(data) {
              if (modernBrowser) {
                history.pushState({'page': 'clone', 'inputs': data, 'reportId': report_id}, "Clone Report");
              }
              var report = new Report(["prm"]);
              report.createCloneReport(data);
              report.unbindEvents();
              report.bindEvents();
              $("#container").addClass("rpt-container");
              report.renderFields(report.fields);
            }
          });
        },
        report_id;

    if ($(this).attr("id") !== undefined) {
      data.id = $(this).attr("id").split("-")[1];
      cloneReport();
    } else {
      data.id = $(this).parents("tr").data("report");
      renderOverview(cloneReport);
    }

    navigation = true;
    renderNavigation();
  });

  // View Archive
  subpage.on("click", "#report-archive", function() {
    if (modernBrowser) {
      history.pushState({'page': 'report-archive'}, "Report Archive");
    }
    navigation = true;
    renderArchive(renderNavigation);
  });
});


function formatDate(date) {
  var year = date.getFullYear(),
      month = date.getMonth(),
      day = date.getDate(),
      hours = date.getHours(),
      minutes = date.getMinutes(),
      seconds = date.getSeconds(),
      milliseconds = date.getMilliseconds();

  function turnTwoDigit(value) {
    return value < 10 ? "0" + value : value;
  }

  month = turnTwoDigit(parseInt(month) + 1);
  day = turnTwoDigit(day);
  hours = turnTwoDigit(hours);
  minutes = turnTwoDigit(minutes);
  seconds = turnTwoDigit(seconds);

  return year + "-" + month + "-" + day + " " + hours + ":" + minutes + ":" + seconds + "." + milliseconds;
}


function updateAllCheckbox(element) {
  var allCheckbox = $(element).parents("div.list-body").prev().children("input"),
      checkboxes = $(element).parents(".list-body").find("input"),
      checked = $(element).parents(".list-body").find(":checked");

  allCheckbox.prop("checked", checked.length === checkboxes.length);
}


function updateItemsSelected(element) {
  var checked = $(element).parents(".list-body").find(":checked"),
      $recordCount = $(element).parents(".list-body").prev().find(".record-count");

  $recordCount.html(checked.length);
  updateShowModal();
}


function updateShowModal() {
  var counts = [];
  $(".record-count").map(function() {
    counts.push($(this).text());
  });

  if (counts.indexOf("0") === -1) {
    $("#show-modal").removeClass("disabled");
  } else {
    $("#show-modal").addClass("disabled");
  }
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


var $navigationBar = $("#navigation");

function renderNavigation(download) {
  var mainContainer = $('#main-container'),
      $navigationBar = $navigationBar || $("#navigation");

  if (navigation) {
    if (!$navigationBar.length) {
      $navigationBar = $('<div id="navigation" class="span12" style="display:none;"></div>').append(function() {
        var $row = $('<div class="row"></div>'),
            $column1 = $('<div class="span4"></div>'),
            $column2 = $column1.clone(),
            $column3 = $column1.clone(),
            $span = $('<span id="goBack"> Back</span>'),
            $i = $('<i class="fa fa-arrow-circle-o-left fa-2x"></i>'),
            $download;

        $span.prepend($i);
        $span.on("click", function() {
          if (modernBrowser) {
            history.back();
          } else {
            renderOverview();
          }
        });
        $row.append($column1.append($span));

        if (download) {
          $download = $('<i class="fa fa-download"></i>');
          $column3.append($download);
        }

        $row.append($column2).append($column3);

        return $row;
      });
      mainContainer.prepend($navigationBar);
    }
    // TODO: Uncomment once UI for navbar is done.
    //$navigationBar.show();
  } else {
    $navigationBar.remove();
  }
}


function renderOverview(callback) {
  $.ajax({
    type: 'GET',
    url: window.location,
    data: {},
    global: false,
    success: function(data) {
      $(".subpage > .wrapper").html(data);
    }
  }).complete(function() {
    if (typeof callback === "function") {
      callback();
    }
  });
}

function renderDownload(report_id) {
  var data = {'id': report_id};

  $.ajaxSettings.traditional = true;
  $.ajax({
    type: "GET",
    url: "downloads",
    data: data,
    success: function(data) {
      var ctx,
          values;

    function updateValues() {
      values = $.map($(".enable-column:checked"), function(item, index) {
        return $(item).val();
      });

      ctx = {'id': report_id, 'values': values};
      $("#download-csv").attr("href", "download?" + $.param(ctx));
    }

      $("#main-container").html(data);

      updateValues();

      // Event Handlers
      $(".column-holder").sortable({
        axis: "y",
        placeholder: "placeholder",
        start: function(e, ui) {
          ui.placeholder.height(ui.item.outerHeight());
          ui.placeholder.width(ui.item.outerWidth() - 2);
          ui.item.addClass("drag");
        },
        stop: function(e, ui) {
          ui.item.removeClass("drag");
        },
        update: updateValues
      });

      $("#all-columns").on("change", function() {
        $("input.enable-column").prop("checked", $(this).is(":checked"));
      });

      $("input.enable-column").on("change", function() {
        var $checkboxes = $("input.enable-column"),
            $checked = $("input.enable-column:checked"),
            $allCheckbox = $("input#all-columns");

        $allCheckbox.prop("checked", $checkboxes.length === $checked.length);
      });

      $("#download-cancel").on("click", function() {
        if (modernBrowser) {
          history.back();
        } else {
          renderOverview();
        }
      });

      $("input.enable-column").on("click", updateValues);
    }
  });
}


function renderGraphs(report_id, callback) {
  var data = {'id': report_id},
      url = location.protocol + "//" + location.host; // https://secure.my.jobs

  navigation = true;

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

          $mainContainer.html('').append("<div class='span6'><h4>Communication Activity</h4><div id='d-chart'></div>" +
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

          if (typeof callback === "function") {
            callback();
          }
        }});
      });
    }
  });
}


function renderArchive(callback) {
  $.ajax({
    type: "GET",
    url: "archive",
    data: {},
    success: function(data) {
      $("#main-container").html(data);
    }
  }).complete(function() {
    if (typeof callback === "function") {
      callback();
    }
  });
}


// Checks to see if browser is IE. If it is then get version.
function isIE() {
    var myNav = navigator.userAgent.toLowerCase();
    return (myNav.indexOf('msie') !== -1) ? parseInt(myNav.split('msie')[1]) : false;
}
