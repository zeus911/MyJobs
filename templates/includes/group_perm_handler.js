    //$().on doesn't work with older versions of jQuery, which django uses
    $('#id_group').change(function(){
	    var val = $(this).val();
	    if(val){
            // set the value from group ddl to GroupPermission.groupId
            GroupPermission.setGroupId(val);
	    	// check if we already have this ajax call's output cached and use it
	        if(GroupPermission.getDataCacheEntry(val)){
	            GroupPermission.setSelectsByGroup(GroupPermission.getDataCacheEntry(val));
	        }
	        // otherwise send ajax call and return output to GroupPermission.setSelectsByGroup
	        else{
	            $.getJSON("/admin/groupsites/", {"groupId" : GroupPermission.getGroupId()}, GroupPermission.setSelectsByGroup);
	        }            
	    } else{
	    	// if the group ddl selected the "none" option, hide the site(s) select box(s)
	        $(GroupPermission.getSitesContainer()).hide();
	    }
	});
