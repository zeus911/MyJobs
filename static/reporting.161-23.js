var Report = function(types) {
  this.types = types;
  this.data = null;
  this.fields = this.create_fields(types);
};

Report.prototype.create_fields = function(types) {
   var reports = {"prm": [new Field("Select Date", "date"),
                          new Field("City", "text"),
                          new Field("State", "text"),
                          new List("Select Partners", "partner"),
                          new List("Select Contacts", "contact")],
              "compliance": []},
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

};

Report.prototype.render_fields = function(fields) {
  var container = $("#container"),
    html = '',
    i = 0;
  for (i; i < fields.length; i++) {
    var field = fields[i];
    console.log("Field: ", field,"Label: ", field.label, "Field: ", field.type);
    html += field.render(field.label, field.type);
  }
  container.html(html);
};

var Field = function(label, type) {
  this.label = label;
  this.type = type;
};

Field.prototype.render = function(label, type) {
  var html = '',
    wrapper = $("<div></div>"), // wrapping div
    l = $("<label>" + label + "</label>"), // label for <input>
    input;
  if (type === "text") {
    input = $("<input type='text' placeholder='"+ label +"' />");
    wrapper.append(l).append(input);
    html = $("<div>").append(wrapper).remove().html();
  } else if (type === "date") {
    var date_widget = $("<div id='date-filter' class='filter-option'></div>")
                        .append("<div class='date-picker'></div>"),
      date_picker = $(date_widget).children("div")
                      .append("<input id='start_date' class='datepicker picker-left' type='text' placeholder='Start Date' />")
                      .append("<span id='activity-to-' class='datepicker'>to</span>")
                      .append("<input id='end_date' class='datepicker picker-right' type='text' placeholder='End Date' />");
    date_widget.append(date_picker);
    html = $("<div>").prepend(l).append(date_widget).remove().html();
  }
  return html;
};

var List = function(label, type) {
  Field.call(this, label, type);
};

List.prototype = Object.create(Field.prototype);

List.prototype.render = function(label, type) {
  console.log("render() Type: ", type);
  var container = $("<div></div>"),
    icon = $("<i class='fa fa-plus-square-o'></i>"),
    all_checkbox = $("<input type='checkbox' checked />"),
    record_count,
    html = '';
  if (type === "contact") {
    record_count = $("<span>(0 Contacts)</span>");
    container.append(icon).append(all_checkbox).append(" All Contacts ").append(record_count);
  } else {
    record_count = $("<span>(0 Partners)</span>");
    container.append(icon).append(all_checkbox).append(" All Partners ").append(record_count);
  }
  html = $("<div>").append(container).remove().html();
  (function() {

  })();
  return html;
};


$(document).ready(function() {
  $(document.body).on("click", ".datepicker",function (e) {
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

  $(document.body).on("click", "#start-report:not(.disabled)", function (e) {
    e.preventDefault();
    var choices = $("#choices input[type='checkbox']:checked"),
      types = [],
      i = 0;
    for (i; i < choices.length; i++) {
      types.push(choices[i].value.toLowerCase());
    }
    report = new Report(types);
    report.bind_events();
    $("#container").addClass("rpt-container");
    $("#back").hide();
    $(".rpt-buttons").removeClass("no-show");
    report.render_fields(report.fields);
  });

  $(document.body).on("click", "#choices input[type='checkbox']:checked", function () {
    var btn = $("#start-report");
    btn.removeClass("disabled");
  });

  $(document.body).on("click", "#choices input[type='checkbox']:not(:checked)", function () {
    var btn = $("#start-report"),
      checkboxes = $("#choices input[type='checkbox']");
    if (!checkboxes.is(":checked")) {
      btn.addClass("disabled");
    }
  });
});
