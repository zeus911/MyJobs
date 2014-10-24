$(document).ready(function() {
    if(window.location.pathname == "/postajob/admin/product/group/") {
        var container = $(".card-wrapper");
    }
    edit_order_setup(container);
});

function edit_order_setup(container) {
    // Run functions that are needed to set up editing order

    disable_first_up_last_down(container);
    add_event_listeners(container);
}

function disable_first_up_last_down(container) {
    /* Variables */
    var rows = $(container).children(".product-card"),
        first_row = $(rows[0]),
        last_row = $(rows[rows.length - 1]);

    // Disable first up arrow and last down arrow in container
    first_row.children("div.product-group-order").children("a:first-child").addClass("disabled");
    last_row.children("div.product-group-order").children("a:last-child").addClass("disabled");
}

function add_event_listeners(container) {
    /* Variables */
    var up_arrows = $("[class*='icon-arrow-up']"),
        down_arrows = $("[class*='icon-arrow-down']");

    // For each up arrow the same process happens
    up_arrows.each(function() {
        $(this).parent('a').on("click", function() {
            // now $(this) == parent of up_arrows
            if(!$(this).hasClass("disabled")) {
                // Prohibits multiple actions to take place during order change
                // to avoid multiple clicks, clicks during process on different
                // objects that could cause confusion.
                disable_buttons();
                var this_row = $(this).parents('div.product-card'),
                    previous_row = $(this_row).prev(),
                    this_group_pk = this_row.attr('id').split('-').slice(-1)[0],
                    previous_group_pk = previous_row.attr('id').split('-').slice(-1)[0],
                    data = {'a': this_group_pk, 'b': previous_group_pk};

                // AJAX call
                send_info(data, container);
            }
        });
    });

    down_arrows.each(function() {
        $(this).parent('a').on("click", function() {
            // now $(this) == parent of down_arrows
            if(!$(this).hasClass("disabled")) {
                // Prohibits multiple actions to take place during order change
                // to avoid multiple clicks, clicks during process on different
                // objects that could cause confusion.
                disable_buttons();
                var this_row = $(this).parents('div.product-card'),
                    next_row = $(this_row).next(),
                    this_group_pk = this_row.attr('id').split('-').slice(-1)[0],
                    next_group_pk = next_row.attr('id').split('-').slice(-1)[0],
                    data = {'a': this_group_pk, 'b': next_group_pk};

                // AJAX call
                send_info(data, container);
            }
        });
    });
}

function disable_buttons() {
    // Disables arrows to prohibit multiple actions.
    var up_arrows = $("[class*='icon-arrow-up']"),
        down_arrows = $("[class*='icon-arrow-down']");
    down_arrows.each(function() {
        $(this).parent("a").addClass("disabled");
    });
    up_arrows.each(function() {
        $(this).parent("a").addClass("disabled");
    });
}

function send_info(data, table) {
    // AJAX that sends info for order switch
    data['company'] = read_cookie();
    data['obj_type'] = "groupings";
    $.ajax({
        type: "GET",
        url: "/postajob/order/",
        data: data,
        global: false,
        success: function(html) {
            $(".product-card").each(function() { $(this).remove() });
            $(".card-wrapper").append(html);
            edit_order_setup(table);
        }
    });
}

function read_cookie() {
    var nameEQ = "myjobs_company=";
    var ca = document.cookie.split(';');
    for (var i=0; i< ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === ' ')
            c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0)
            return c.substring(nameEQ.length, c.length);
    }
    return null;
}