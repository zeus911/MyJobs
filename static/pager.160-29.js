function Pager() {
    this._PAGE_SIZE = 20;
    this._HIDDEN_CLASS_NAME = "direct_hiddenOption";
}


Pager.prototype = {

    showLessHandler: function(e, num_items) {
        // get the list to act on
        var clickedLink = e.target;
        var parentEl = $(clickedLink).parent();
        var itemListId = this._getListElementFromContainerId(parentEl.attr('id'));

        // hide the items
        this._showLessItems(itemListId, num_items, num_items);

        // toggle more/less link, if needed
        this._toggleLessLink(itemListId, num_items);
        this._toggleMoreLink(itemListId);

        // stop default behavior of the link, since we're
        // not really using it as a link.  yeah, its not ideal.
        return false;
    },

    showMoreHandler: function(e, num_items, parent) {
        var clickedLink = e.target;
        var parentEl = $(clickedLink).parent();
        var type = parentEl.attr('data-type');
        var itemListId = this._getListElementFromContainerId(parentEl.attr('id'));

        this._showMoreItems(itemListId, num_items, type, parent);

        // toggle more/less links, if needed
        this._toggleLessLink(itemListId, num_items);

        // stop default behavior of the link, since we're
        // not really using it as a link.  yeah, its not ideal.
        return false;
    },

    _toggleLessLink: function(itemListId, minVisible) {
        // we want to turn the 'Less' link off when
        // we're at the minVisible limit.

        // if minVisible = 10 and there's 11, we want
        // to just hide 1 element, if there's 16 showing
        // we'd want to hide 6
        var jqItemList = $("#"+itemListId);
        var currNumVisible = jqItemList.children(':visible').length;

        var jqLessLink = this._getLinkForItemList(jqItemList, "less");
        var jqMoreLink = this._getLinkForItemList(jqItemList, "more");

        if(currNumVisible > minVisible){
            jqLessLink.show()
        }else{
            jqLessLink.hide();
            jqMoreLink.focus();
        }
    },

    _toggleMoreLink: function(itemListId) {
        var jqItemList = $("#"+itemListId);
        var numHiddenItems = jqItemList.children("."+this._HIDDEN_CLASS_NAME).length;

        var jqMoreLink = this._getLinkForItemList(jqItemList, "more");
        (numHiddenItems > 0) ? jqMoreLink.show() : jqMoreLink.hide();
    },

    _getLinkForItemList: function(jqItemList, moreOrLess) {
        var itemListId = jqItemList.attr('id');
        var linkClassNames = {
            'more': ".direct_optionsMore",
            'less': ".direct_optionsLess"
        };
        var selector = "#direct_moreLessLinks_" + itemListId.split('_')[1] + " " + linkClassNames[moreOrLess];
        return $(selector);
    },

    _getListElementFromContainerId: function(linkContainerId) {
        // Current List IDs that we'll be looking for:
        // - direct_titleDisambig
        // - direct_countryDisambig
        // - direct_stateDisambig
        // - direct_cityDisambig
        // - direct_jobListing
        // - direct_facetDisambig
        // - direct_mocDisambig

        // We've attached the second part onto the ID of
        // the <span> tag that wraps the more/less links,
        // so we can pull it off of there to know which
        // list we should take action on.

        // i.e. <span id="direct_moreLessLinks_countryDisambig">
        var baseElementId = "direct_%s";
        var idPieces = linkContainerId.split('_');
        var listId = idPieces[2];

        return baseElementId.replace('%s', listId);
    },

    _showMoreItems: function(listId, numToShow, type, parent){
        var itemList = $("#" + listId);

        var hiddenItems = itemList.children("." + this._HIDDEN_CLASS_NAME);
        var currNumHidden = hiddenItems.length;
        var offset = parent.attr('data-offset');
        focus_item = $("#" + listId + " .direct_hiddenOption:first a");

        // if we have current hidden ones, lets show those
        if(currNumHidden > 0) {
            // if there's less hidden items than what we want to show
            // then we'll only show those and if there's zero hidden,
            // then we'll go get some more and still show the number
            // we want to
            numToShow = (numToShow > currNumHidden) ? currNumHidden : numToShow;

            hiddenItems.slice(0, numToShow).removeClass(this._HIDDEN_CLASS_NAME);
            currNumHidden -= numToShow;
        }

        if(currNumHidden == 0) {
            // lets see if we have any to get from the server
            var data = {
                'offset': offset,
                'num_items': this._PAGE_SIZE
            };
            var qsParams = this._getQueryParams();
            data['q'] = qsParams['q'];
            data['location'] = qsParams['location'];
            data['moc'] = qsParams['moc'];
            data['company'] = qsParams['company'];
            data['filter_path'] = window.location.pathname;

            this._ajax_getItems(type, data, listId, parent);
        }
        focus_item.focus();
    },

    _showLessItems: function(listId, numToHide, minVisible){
        var itemList = $("#" + listId);
        var visibleItems = itemList.children(':visible');
        var numVisible = visibleItems.length;
        var numAvailableToHide = numVisible - minVisible;

        if (numAvailableToHide < numToHide) {
            numToHide = numAvailableToHide;
        }

        if (numToHide > 0) {
            visibleItems.slice(-numToHide).addClass(this._HIDDEN_CLASS_NAME);
        }

    },

    _ajax_getItems: function(type, data, elem, parent){
        var that = this;
        var url = this._build_url(type);
        $.get(
            url,
            data,
            function(html) {
                that._getItemsSuccessHandler(html, elem, parent);
            }
        );
    },

    _build_url: function(type){
        // Build the URL with the current path as our
        // 'filter' that is sent into to filter objects
        var urls = {
            "title": "/ajax/titles/",
            "city": "/ajax/cities/",
            "state": "/ajax/states/",
            "country": "/ajax/countries/",
            "facet": "/ajax/facets/",
            "facet-2": "/ajax/facets/",
            "facet-3": "/ajax/facets/",
            "moc": "/ajax/mocs/",
            "mappedmoc": "/ajax/mapped/",
            "company": "/ajax/company-ajax/",
            "listing": "/ajax/joblisting/",
            "search": "/ajax/joblisting/"
        };

        return urls[type];
    },

    _getItemsSuccessHandler: function(html, insertIntoElem, parent){
        // Since the update was successful, the offset can be updated to
        // reflect the requested amount.
        parent.attr('data-offset', parseInt(parent.attr('data-offset')) + this._PAGE_SIZE);

        // From the Django templates we get a lot of line breaks,
        // so we'll remove them right here, just to be safe
        html = html.replace(/\n/g, "");
        $("#" + insertIntoElem).children(":last").after(html);
        this._toggleMoreLink(insertIntoElem);
    },

    _getQueryParams: function() {
        var result = {}, queryString = location.search.substring(1),
            re = /([^&=]+)=([^&+]*)/g, m;
        while (m = re.exec(queryString)) {
            result[decodeURIComponent(m[1])] = decodeURIComponent(m[2]);
        }

        return result;
    }
};

$(document).ready(function(){
	var pager = new Pager();
    $(document).on("click", "a.direct_optionsMore", function(e) {
        return pager.showMoreHandler(e, $(this).parent().attr('data-num-items'), $(this).parent());
    });
	$('#button_moreJobs').click(function(e) {
		e.preventDefault();
		var parent = $(this).parent();
		var num_items = parseInt(parent.attr('data-num-items'));
		var offset = parseInt(parent.attr('offset'));
		var type = parent.attr('data-type');
		var path = window.location.pathname;
		var query = window.location.search;
		var ajax_url = path + "ajax/joblisting/" + query;
		focus_item = $('#direct_listingDiv .direct_hiddenOption .direct_joblisting:first-child h4 a');
		$('#direct_listingDiv .direct_hiddenOption').removeClass('direct_hiddenOption');
		focus_item.focus();
		$.ajax({
			url: ajax_url,
			data: {'num_items': num_items, 'offset': offset},
			success: function (data) {
						$('#direct_listingDiv ul:last').after(data);
						parent.attr('offset', (offset + num_items).toString());						
					}
			});
	});
	$('a.direct_optionsLess').click(function(e) {
		return pager.showLessHandler(e, $(this).parent().attr('data-num-items'));
	});
	$(".direct_offsiteContainer").hover(function() {
		$(this).children('.direct_offsiteHoverDiv').show();
			}, function() {
		$(this).children('.direct_offsiteHoverDiv').hide();
	});

	$('div.direct_offsiteHoverDiv').each(function(){
		$(this).attr('style', 'margin-top: -'+($(this).height()+2)+'px;');
	});
	
	$('.direct_deBadgeLink').click(function(){
		goalClick('/G/de-click', this.href); 
		return false;
	});
	
	$('.direct_companyLink').click(function(){
		goalClick('/G/career-site-click', this.href);
		return false;
	});

	$('.direct_socialLink').click(function(){
		goalClick('/G/social-media-click', this.href);
		return false;
	});
});
