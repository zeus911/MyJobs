$(document).ready(function() {
    $("#addTags").on("click", function() {
        var values = $("#p-tags").val();
        $.ajax({
            type: "GET",
            url: "/prm/view/tagging/add",
            data: {'data': values},
            success: function(data) {
                location.reload();
            }
        });
    });
    
    $("#p-tags").hide();
    $("#p-tags").tagit({
        allowSpaces: true,
        tagSource: function(search, showChoices) {
            var value = $(".tagit-new > input").val(),
                search = {value: value},
                that = this;
            $.ajax({
                type: "GET",
                url: "/prm/view/records/get-tags",
                data: search,
                success: function(data) {
                    var jdata = jQuery.parseJSON(data);
                    showChoices(that._subtractArray(jdata, that.assignedTags()))
                }
            });
        },
        beforeTagAdded: function(event, ui) {
            ui.tag.hide();
            var name = ui.tag.children("span").html();
            $.ajax({
                type: "GET",
                url: "/prm/view/records/get-tag-color",
                data: {"name": name},
                success: function(data) {
                    var jdata = jQuery.parseJSON(data);
                    if(jdata.length > 0)
                        ui.tag.css("background-color", "#"+jdata[0]);
                    ui.tag.show();
                }
            })
        },
        autocomplete: {delay: 0, minLength: 1},
        afterTagAdded: function() {
            if($("ul.tagit").children("li.tagit-choice").length > 0)
                $("#addTags").removeAttr("disabled");
        },
        afterTagRemoved: function() {
            if($("ul.tagit").children("li.tagit-choice").length === 0)
                $("#addTags").attr("disabled", "disabled");
        },
        placeholderText: "Create New Tags"
    });
});