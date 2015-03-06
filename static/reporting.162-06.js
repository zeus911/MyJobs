/*
Send the user a message when they try to unload the page saying their
progress will not be saved and will be lost.
TODO: uncomment this and give a more meaningful message. Commented out for development purposes.
window.addEventListener("beforeunload", function(e) {
    e.returnValue = "\\o/";
});
*/


var Report = function(types) {
  this.types = types;
  this.data = {};
  this.fields = this.create_fields(types);
};


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


Report.prototype.bind_events = function() {
  var report = this;


  // Update Partner and Contact Lists
  $(document.body).on("change", "input:not([id$=-all-checkbox])", function(e) {
    console.log("CHANGE!");

    var in_list = $(this).parents(".list-body").attr("id"),
        contact_wrapper = $("#contact-wrapper"),
        c_field = report.find_field("Select Contacts");

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


  $(document.body).on("click", ".list-body li", function() {
    $(this).children("input").click();
  });


  // The event that a checked checkbox is clicked (will uncheck the checkbox)
  $(document.body).on("click", ".list-body input[type='checkbox']:checked", function(e) {
    e.stopPropagation();
    var all_checkbox = $(this).parents("div.list-body").prev().children("input");
    if (all_checkbox.is(":checked")) {
      all_checkbox.prop("checked", false);
    }
  });


  $(document.body).on("click", ".list-body input[type='checkbox']:not(:checked)", function(e) {
    e.stopPropagation();
    var all_checkbox = $(this).parents("div.list-body").prev().children("input"),
        checkboxes = $(this).parents(".list-body").find("input"),
        all_are_checked = true,
        that = this;

    $(checkboxes).each(function(element) {
      // Check to see if all checkboxes are checked
      if (!$(checkboxes[element]).is(":checked") && checkboxes[element] !== that) {
        all_are_checked = false;
        // exit .each function. Mimics break
        return false;
      }
    });

    if (!all_are_checked) {
      all_checkbox.prop("checked", false);
    } else {
      all_checkbox.prop("checked", true);
    }
  });


  $(document.body).on("click", "input[id$=-all-checkbox]:checked", function(e) {
    e.stopPropagation();
    var checkboxes = $(this).parent().next().find("input");

    $(checkboxes).each(function(element) {
      $(checkboxes[element]).prop("checked", true);
    });
  });


  $(document.body).on("click", "input[id$=-all-checkbox]:not(:checked)", function(e) {
    e.stopPropagation();
    var checkboxes = $(this).parent().next().find("input");

    $(checkboxes).each(function(element) {
      $(checkboxes[element]).prop("checked", false);
    });
  });


  $(document.body).on("click", "#show-modal", function(e) {
    var modal = $("#report-modal"),
        body = modal.children(".modal-body"),
        footer = modal.children(".modal-footer");
    body.html(report.readable_data());
    modal.modal("show");
  });


  $(document.body).on("click", "#gen-report", function(e) {
    var data = {"csrfmiddlewaretoken": read_cookie("csrftoken")},
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
        $(".modal-body").html(JSON.stringify(data.records));
      }
    });
  });
};


Report.prototype.readable_data = function() {
  var data = this.data,
      html = '',
      key;

  for (key in data) {
    if (data.hasOwnProperty(key)) {
      var value = data[key];

      key = key.replace(/_/g, " ");
      html += "<label>" + key + ":</label>";

      if (typeof value === "object") {
        var ul = $("<ul></ul>");

        for (var i = 0; i < value.length; i++) {
          var name = $("#" + key + " input[value='" + value[i] + "'").next("span").html(),
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


Report.prototype.find_field = function(field_label) {
  return ($.grep(this.fields, function(field) {
    return field.label === field_label;
  })[0]);
};


Report.prototype.render_fields = function(fields) {
  var container = $("#container"),
      html = '',
      i = 0;
  for (i; i < fields.length; i++) {
    var field = fields[i];
    html += field.render();
  }
  html += "<br /><a id=\"show-modal\" class=\"btn\">Generate Report</a>";
  container.html(html);
};


var Field = function(label, type) {
  this.label = label;
  this.type = type;
};


Field.prototype.render = function() {
  var html = '',
      wrapper = $("<div></div>"), // wrapping div
      l = $("<label>" + this.label + "</label>"), // label for <input>
      input;

  if (this.type === "text") {
    input = $("<input id='" + this.label.toLowerCase().replace(/ /g, "_") + "' type='text' placeholder='"+ this.label +"' />");
    wrapper.append(l).append(input);
    html = wrapper.prop("outerHTML");
  } else if (this.type === "date") {
    var date_widget = $("<div id='date-filter' class='filter-option'></div>").append("<div class='date-picker'></div>"),
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

  (function() {
    list.filter(list.type, filter);
  })();

  return html;
};


List.prototype.filter = function(type, filter) {
  "use strict";
  var url = location.protocol + "//" + location.host, // https://secure.my.jobs
      data = {"csrfmiddlewaretoken": read_cookie("csrftoken")};

  if (typeof filter !== "undefined") {
    $.extend(data, filter);
  }

  if (type === "partner") {
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
          selected = $("[id^='" + type + "-header'] span span");
      for (var i = 0; i < data.records.length; i++) {
        var record = data.records[i],
            li = $("<li><input type='checkbox' value='"+ record.pk +"' checked /> <span>"+ record.name +"</span></li>"),
            invis_box = $("<div class=\"invis-box\"></div>");
        if (type === "partner") {
          li.append("<span class='pull-right'>"+ record.count +"</span>");
        }
        li.append(invis_box);
        ul.append(li);
      }
      $("#"+ type + ".list-body").append(ul);
      $(selected).html(data.records.length).parent().show("fast");
    },
    error: function(e) {
      // TODO: change when testing is done to something more useful.
      throw "Something horrible happened.";
    }
  });
};


$(document).ready(function() {
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
      i = 0;
    for (i; i < choices.length; i++) {
      types.push(choices[i].value.toLowerCase());
    }
    var report = new Report(types);
    report.bind_events();
    $("#container").addClass("rpt-container");
    $("#back").hide();
    $(".rpt-buttons").removeClass("no-show");
    report.render_fields(report.fields);
  });


  $(document.body).on("click", "#choices input[type='checkbox']:checked", function() {
    var btn = $("#start-report");
    btn.removeClass("disabled");
  });


  $(document.body).on("click", "#choices input[type='checkbox']:not(:checked)", function() {
    var btn = $("#start-report"),
        checkboxes = $("#choices input[type='checkbox']");
    if (!checkboxes.is(":checked")) {
      btn.addClass("disabled");
    }
  });
});
