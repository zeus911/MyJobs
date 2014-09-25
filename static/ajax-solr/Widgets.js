(function ($) {
    AjaxSolr.ResultWidget = AjaxSolr.AbstractWidget.extend({
        afterRequest: function () {
            $(this.target).empty();
            for (var i = 0, l = this.manager.response.response.docs.length;
                 i < l; i++) {
                var doc = this.manager.response.response.docs[i];
                $(this.target).append("Job Title: " + doc.title +
                                      " - Company: " + doc.company +
                                      "\n");
            }
        }
    });
    
    AjaxSolr.CountWidget = AjaxSolr.AbstractWidget.extend({
        afterRequest: function () {
            var countStr = "Total jobs found for this query: ";
            var count = this.manager.response.response.numFound;
            $(this.target).empty();
            $(this.target).text(countStr + count);
        }
    });
})(django.jQuery);
