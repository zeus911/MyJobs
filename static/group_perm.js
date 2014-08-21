var GroupPermission = (function($) {    

    var groupId;
    var dataCache = {};
    var originalData = {};
    var sites_container;
    var sites_to_selector;
    var sites_from_selector;
    var sites_to_from_selector;
    var addCacheToKeys;
    var addCacheFromKeys;
    var siteTypes;
    var node = {'id': "", "domain": ""};
    var resetCacheKeys;
    var optionString = "";
    var optionJson = {};
    
    function initializeData(obj){
    	// set up variables for GroupPermission to use an type of admin page (default or microsite carousel)
	    sites_container = obj.sites_container;
	    sites_to_selector = obj.sites_to_selector;
	    sites_from_selector = obj.sites_from_selector;
	    sites_to_from_selector = sites_to_selector + ", " + sites_from_selector;
	    addCacheToKeys = obj.addCacheToKeys;
	    addCacheFromKeys = obj.addCacheFromKeys;
	    siteTypes = obj.siteTypes;
	    resetCacheKeys = addCacheToKeys.concat(addCacheFromKeys);
	    
	    // store the selected sites of the selected group on page load
	    // if this is an existing object being editted
	    originalData.group = obj.originalData.group;
        $.each(obj.siteTypes, function(index, siteType) {
            if (!obj.originalData[siteType]) {
                obj.originalData[siteType] = {};
            }
        	originalData[siteType] = obj.originalData[siteType];
        });
    }
    
    function setGroupId(val){
		groupId = val;
		return groupId;
    }
    
    function addToCache(items, data){
    	// patch into the django's javascript for multiselect boxes and
    	// add ajax'd site values into the cache entry for that/those select(s)
    	for(var i=0, itemLength = items.length; i < itemLength; i++){
    		SelectBox.add_to_cache(items[i], data);
    	}
    }
    
    function resetCache(items){
    	// patch into the django's javascript for multiselect boxes and
    	// clear values from the cache entry for that/those select(s)
    	for(var i=0, itemLength = items.length; i < itemLength; i++){
    		SelectBox.cache[items[i]] = new Array();
    	}
    }
    
    function buildOption(nodeId, nodeDomain) {
    	return '<option value="' + nodeId + '">' + nodeDomain + '</option>';
    }
    
    function setSelectsByGroup(data){
    	// if we don't have the return value from ajax call cached in dataCache, add it
        if(!(dataCache[groupId])){
            dataCache[groupId] = data;
        }
        // empty the selected "chosen sites" box of multiselect
        $(sites_to_from_selector).html('');
        resetCache(resetCacheKeys);
        // check if this data call is for the default selected group from page load
        // because it possible already has "chosen" sites to redisplay
        if(groupId == originalData.group){
            $.each(siteTypes, function(index, siteType) {
	            var options_to = ""
	            var options_from = ""
	            for(var i=0, dataLength = data.length; i < dataLength; i++){
	            	node = data[i];
	        	    optionJson = {value: node.id, text: node.domain, displayed: 1};
	                if($.inArray(node.id.toString(), originalData[siteType]) > -1){
	                    options_to += buildOption(node.id, node.domain);
	                    addToCache(["id_"+siteType+"_to"], optionJson);
	                }
	                else{
	                    options_from += buildOption(node.id, node.domain);
	                    addToCache(["id_"+siteType+"_from"], optionJson);
	                }
	            }
	            $("#id_"+siteType+"_from").html(options_from);
	            $("#id_"+siteType+"_to").html(options_to);
            });
        }
        // data call is not for the default selected group from page load, so it could not
        // have previously selected "chosen sites", so display all options in "available sites"
        else{
            var options = ""
            for(var i=0, dataLength = data.length; i < dataLength; i++){
            	node = data[i];
            	optionJson = {value: node.id, text: node.domain, displayed: 1};
                options += buildOption(node.id, node.domain);
                addToCache(addCacheFromKeys, optionJson);
            }
            $(sites_from_selector).html(options);
        }
        $(sites_container).show();
    }
    
    return {
		init: function(obj) {
			// initialize data from passed object
			initializeData(obj);
		},
		setSelectsByGroup: function(data) {
			setSelectsByGroup(data);
		},
		setGroupId: function(val) {
			return setGroupId(val);
		},
		getGroupId: function() {
			return groupId;
		},
		getDataCacheEntry: function(val) {
			return dataCache[val];
		},
		getSitesContainer: function() {
			return sites_container;
		}
	};
})(django.jQuery);
