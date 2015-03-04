var TextInput = React.createClass({
  getInitialState: function(eid, verbose_name) {
    return {
      "id": eid,
      "verbose_name": verbose_name
    }
  },
  render: function() {
    var verbose_name = this.props.verbose_name;
    return (
      <div>
        <label for={this.props.id}>{verbose_name}</label>
        <input id={this.props.id} type="text" placeholder={"" + verbose_name + ""} />
      </div>
    );
  }
});

var DateInput = React.createClass({
  render: function() {
    return (
      <div id="date-filter" class="filter-option">
        <div class="date-picker">
          <input class="datepicker picker-left" id="start_date" type="text" placeholder="Start Date" />
          <span class="datepicker" id="activity-to-">to</span>
          <input class="datepicker picker-right" id="end_date" type="text" placeholder="End Date" />
        </div>
      </div>
    );
  }
});

var Report = React.createClass({
  getInitialState: function(types) {
    return {
      data: null,
      t: types
    };
  },
  render: function() {
    return (

    );
  }
});
