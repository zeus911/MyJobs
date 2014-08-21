var Manager;
var query_params = {};
var solr_fields = {
    company: ["company_exact"],
    country: ["country_exact"],
    state: ["state_exact"],
    city: ["city_exact"],
    keyword: ["text"],
    onet: ["onet"],
    title: ["title"],
    querystring: ["raw"]};
    
(function ($) {
    $(function () {
        query_terms = [];
        Manager = new AjaxSolr.Manager({
            solrUrl: "http://ec2-50-19-85-235.compute-1.amazonaws.com:8983/solr/"
        });
        Manager.addWidget(new AjaxSolr.ResultWidget({
            id: "result",
            target: "#id_search_preview"
        }));
        Manager.addWidget(new AjaxSolr.CountWidget({
            id: "count",
            target: "#resultsCount"
        }));
        Manager.init();

        var substring = function (input) {
            return input.split("#@#").join(" OR ");
        };
        
        $(document).ready(function () {
            query_params["raw"] = substring($("#id_querystring").val());
            query_params["title"] = substring($("#id_title").val());
            query_params["text"] = substring($("#id_keyword").val());
            query_params["city_exact"] = substring($("#id_city").val());
            query_params["state_exact"] = substring($("#id_state").val());
            query_params["country_exact"] = substring($("#id_country").val());
            query_params["company_exact"] = substring($("#id_company").val());
            query_params["onet"] = substring($("#id_onet").val());

            $(".cf_field").change(function () {
                query_terms = [];
                key = $(this).attr("name");
                value = $(this).val();
                $.each(solr_fields[key], function(idx, val) {
                    query_params[val] = substring(value);
                });
            });
            
            $("#btnClick0").click(function () {
                for (var k in query_params) {
                    term = query_params[k];
                    if (term != "") {
                        switch(k) {
                          case "raw":
                            query_terms.push("(" + term + ")");
                            break;
                        default:
                            query_terms.push("(" + k + ":" + term + ")");
                        }}};
                Manager.store.addByValue("fq",
                                         "(" + query_terms.join(" AND ") + ")");
                Manager.store.addByValue("q", "*:*");
                Manager.doRequest();
            });
        });
    });
})(django.jQuery);

