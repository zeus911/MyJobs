(function($) {
    var dataCache = {};
    /**
    ID of the SeoSite object being edited, fetched from the last portion of
    the url. This var is passed to various functions in this module as the
    'group' argument. It's used to filter the various inlines on the SeoSite
    admin page.

    **/
    var objId = window.location.pathname.split("/");
    objId = objId[objId.length-2];
    var show_msg = false;

    $(document).ready(function() {
        getSelectsByGroup($('#id_group').val());
    });
    
    $('#id_group').change(function(){
        if($(this).val() > 0) {
            getSelectsByGroup($('#id_group').val());
        } else {
            $('select.filtered').not('div.business_units select.filtered').html('');
        }
        if (show_msg===false) {
            $('#id_business_units_to option').attr('selected', 'selected');
            SelectBox.move('id_business_units_to', 'id_business_units_from');
        }
        show_msg=true;
    });

    function getSelectsByGroup(group) {
        /**
        Call to seo.views.search_views.get_group-relationships.
        The return value is a JSON-serialized string containing querysets
        filtered by group 'group'.

        Is the callback really necessary here? Can't this just be a simple
        'if not (dataCache[group]) { $.getJSON <...> }
         setSelectsByGroup(data, group)' ?

        **/
        if(dataCache[group]) {
            setSelectsByGroup(dataCache[group]);
        } else {
            $.getJSON("/admin/grouprelationships/", {groupId : group, objId : objId}, callbackFunction(group));
        }
    }

    function callbackFunction(group) {
        /**
        It's not entirely clear this fn is actually necessary since it
        seems like getSelectsByGroup could be refactored to perform in the
        same way.

        **/
        return function(data, group) {
            setSelectsByGroup(data, group);
        };
    }
    
    function setSelectsByGroup(data, group) {
        if(!(dataCache[group])){
            dataCache[group] = data;
        }
        SelectBox.cache.id_configurations_from = [];
        SelectBox.cache.id_configurations_to = [];
        SelectBox.cache.id_google_analytics_from = [];
        SelectBox.cache.id_google_analytics_to = [];
        // facets = data.facets;
        configurations = data.configurations;
        google_analytics = data.google_analytics;
        configOptions = buildOptions('configurations', 'title', configurations, data.selected.configurations);
        $('#id_configurations_from').html(configOptions.from);
        $('#id_configurations_to').html(configOptions.to);
        googleAnalyticsOptions = buildOptions('google_analytics', 'web_property_id', google_analytics, data.selected.google_analytics);
        $('#id_google_analytics_from').html(googleAnalyticsOptions.from);
        $('#id_google_analytics_to').html(googleAnalyticsOptions.to);     
    }

    function buildOptions(type, title_value, items, selected) {
        /**
        This method builds out the HTML <option> tags for the inline models.
        It controls the behavior of the multiple select boxes in the admin
        interface.
        
        It's not clear what the SelectBox caching is used for, or why/whether
        it's even necessary. Could stand a look toward refactoring.

        **/
        var options_to = [];
        var options_from = [];
        var item_id;
        var item_title;
        for(var i=0, itemLength = items.length; i < itemLength; i++) {
            item_id = items[i].id;
            item_title = items[i].title;
            if ($.inArray(item_id, selected) > -1){
                options_to[options_to.length] = buildOptionHTML(item_id, item_title);
                SelectBox.add_to_cache("id_" + type + "_to", {value: item_id, text: item_title, displayed: 1});
            } else {
                options_from[options_from.length] = buildOptionHTML(item_id, item_title);
                SelectBox.add_to_cache("id_" + type + "_from", {value: item_id, text: item_title, displayed: 1});
            }
        }
        return {"from": options_from.join(), "to" : options_to.join()};
    }
    
    function buildOptionHTML(item_id, item_title) {
        return '<option value="' + item_id + '">' + item_title + '</option>';
    }

})(django.jQuery);

