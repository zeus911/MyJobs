function Pager() {
    this._PAGE_SIZE = 20;
    this._HIDDEN_CLASS_NAME = "direct_hiddenOption";
}


Pager.prototype = {

    showLessHandler: function (e, num_items, parent) {
        // hide the items
        this._showLessItems(parent, num_items, num_items);

        // toggle more/less link, if needed
        this._toggleLessLink(parent, num_items);
        this._toggleMoreLink(parent);

        // stop default behavior of the link, since we're
        // not really using it as a link.  yeah, its not ideal.
        return false;
    },

    showMoreHandler: function(e, num_items, parent) {
        var type = parent.attr('data-type');

        this._showMoreItems(num_items, type, parent);

        // toggle more/less links, if needed
        this._toggleLessLink(parent, num_items);

        // stop default behavior of the link, since we're
        // not really using it as a link.  yeah, its not ideal.
        return false;
    },

    _toggleLessLink: function(moreLessSpan, minVisible) {
        /* Turn the 'Less' link off when we're at the minVisible limit. */
        var relatedList = this._getListFromMoreLessLinksSpan(moreLessSpan);

        var lessLink = moreLessSpan.children('.direct_optionsLess')[0];
        var moreLink = moreLessSpan.children('.direct_optionsMore')[0];

        var currNumVisible = relatedList.children(':visible').length;
        if(currNumVisible > minVisible) {
            $(lessLink).show();
        }
        else {
            $(lessLink).hide();
            $(moreLink).focus();
        }
    },

    _toggleMoreLink: function(moreLessSpan) {
        var relatedList =  this._getListFromMoreLessLinksSpan(moreLessSpan);

        var numHiddenItems = relatedList.children("."+this._HIDDEN_CLASS_NAME).length;

        var moreLink = moreLessSpan.children('.direct_optionsMore')[0];

        (numHiddenItems > 0) ? $(moreLink).show() : $(moreLink).hide();
    },

    _getListFromMoreLessLinksSpan: function(moreLessSpan) {
        // The container for all the facet blocks.
        var parentDiv = $(moreLessSpan).parent();

        // From the container for all the facet blocks we can get the
        // exact list we want to work with.
        var itemListId = this._getListElementFromContainerId(moreLessSpan.attr('id'));

        return $(parentDiv).children("#" + itemListId);
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

    _showMoreItems: function(numToShow, type, parent) {
        var relatedList = this._getListFromMoreLessLinksSpan(parent);

        var hiddenItems = relatedList.children("." + this._HIDDEN_CLASS_NAME);
        var currNumHidden = hiddenItems.length;

        var focus_item = relatedList.children(this._HIDDEN_CLASS_NAME + ":first li");

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

        if(currNumHidden === 0) {
            // lets see if we have any to get from the server
            var data = {
                'offset': parent.attr('data-offset'),
                'num_items': this._PAGE_SIZE
            };

            var qsParams = this._getQueryParams();

            data.q = qsParams.q;
            data.location = qsParams.location;
            data.moc = qsParams.moc;
            data.company = qsParams.company;
            data.filter_path = window.location.pathname;

            this._ajax_getItems(type, data, parent);
        }
        focus_item.focus();
    },

    _showLessItems: function(parent, numToHide, minVisible){
        var relatedList = this._getListFromMoreLessLinksSpan(parent);

        var visibleItems = relatedList.children(':visible');
        var numVisible = visibleItems.length;
        var numAvailableToHide = numVisible - minVisible;

        if (numAvailableToHide < numToHide) {
            numToHide = numAvailableToHide;
        }

        if (numToHide > 0) {
            visibleItems.slice(-numToHide).addClass(this._HIDDEN_CLASS_NAME);
        }

    },

    _ajax_getItems: function(type, data, parent){
        // Preserve the reference to "this" so it can be used inside the
        // ajax call.
        var alsoThis = this;
        var url = this._build_url(type);
        $.get(
            url,
            data,
            function(html) {
                alsoThis._getItemsSuccessHandler(url ? html : "", parent);
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

    _getItemsSuccessHandler: function(html, parent) {
        // Since the update was successful, the offset can be updated to
        // reflect the requested amount.
        parent.attr('data-offset', parseInt(parent.attr('data-offset')) + this._PAGE_SIZE);

        // From the Django templates we get a lot of line breaks,
        // so we'll remove them right here, just to be safe.
        html = html.replace(/\n/g, "");

        var parentDiv = $(parent).parent();

        var itemListId = this._getListElementFromContainerId(parent.attr('id'));
        var relatedList = $(parentDiv).children("#" + itemListId);

        $(relatedList).children(":last").after(html);
        this._toggleMoreLink(parent);
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
    var total_clicks = parseInt(window.location.hash.slice(1, 10));
    if (!isNaN(total_clicks)) {
        // Only set hash if one already existed.
        window.location.hash = "";
    }

    $(document).on("click", "a.direct_optionsMore", function(e) {
        var parent = $(this).parent();
        var num_items = parent.attr('data-num-items');
        return pager.showMoreHandler(e, num_items, parent);
    });

	$('#button_moreJobs').click(function(e) {
		e.preventDefault();
		var parent = $(this).parent();
		var num_items = parseInt(parent.attr('data-num-items'));
		var offset = parseInt(parent.attr('offset'));
		var path = window.location.pathname;
		var query = window.location.search;
		var ajax_url = path + "ajax/joblisting/" + query;

        var hiddenFeaturedList = $('#direct_listingDiv .featured_jobListing.direct_hiddenOption .direct_joblisting');
        var hiddenDefaultList = $('#direct_listingDiv .default_jobListing.direct_hiddenOption .direct_joblisting');

        var focus_item;
        var firstItem;
        if(hiddenFeaturedList.length > 0) {
            firstItem = $(hiddenFeaturedList)[0];
        }
        else {
            firstItem = $(hiddenDefaultList)[0];
        }
        focus_item = $(firstItem).find('a');
        focus_item.focus();

        $('#direct_listingDiv .direct_hiddenOption').removeClass('direct_hiddenOption');

		$.ajax({
			url: ajax_url,
			data: {'num_items': num_items, 'offset': offset},
			success: function (data) {
                $('#direct_listingDiv ul:last').after(data);
                parent.attr('offset', (offset + num_items).toString());
                var num_clicks = parseInt(window.location.hash.slice(1, 10));
                if (isNaN(num_clicks) && isNaN(total_clicks)) {
                    window.location.hash = "1";
                } else {
                    if (isNaN(num_clicks)) {
                        num_clicks = 0;
                    }
                    window.location.hash = (++num_clicks).toString();
                    if (!isNaN(total_clicks) && num_clicks < total_clicks) {
                        $('#button_moreJobs').click();
                    }
                }
            }
        });
    });

    if (!isNaN(total_clicks)) {
        $('#button_moreJobs').trigger('click');
    }

	$('a.direct_optionsLess').click(function(e) {
        var parent = $(this).parent();
        var num_items = parent.attr('data-num-items');
		return pager.showLessHandler(e, num_items, parent);
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
