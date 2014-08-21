/*=============================================================================
                       DirectEmployers Member Widget

  Usage:
  Insert `<div id="de-member-carousel"></div>` where you want the widget.

  Put `<script src="//d2e48ltfsb5exy.cloudfront.net/widgets/de_member_carousel.js"></script>`
  at the end of the document. That's it!
  
  Optional attributes on the de-member-carousel tag:
  `num-icons` determines the number of icons to display per page. The default of 
  7 fits nicely on a page width of 960px. If the container is too small for the 
  number of icons displayed, the additional icons will be hidden (and skipped 
  when the user pages forwards or backwards).

  `arrows` -- Set to 'false' to hide the arrows. Use this when you don't need
  the ability to page.
  
  EXAMPLE: <div id="de-member-carousel" arrows="false" num-icons=4></div> will
  create a logo carousel with 4 icons and no paging arrows.
 =============================================================================*/

// Create jQuery object for this widget.
// See http://alexmarandon.com/articles/web_widget_jquery/
(function(){
    // Localize jQuery variable
    var jQuery;

    /******** Load jQuery if not present *********/
    if (window.jQuery === undefined || window.jQuery.fn.jquery !== '1.4.2') {
        var script_tag = document.createElement('script');
        script_tag.setAttribute("type","text/javascript");
        script_tag.setAttribute("src",
            "http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js");
        if (script_tag.readyState) {
          script_tag.onreadystatechange = function () { // For old versions of IE
              if (this.readyState == 'complete' || this.readyState == 'loaded') {
                  scriptLoadHandler();
              }
          };
        } else {
          script_tag.onload = scriptLoadHandler;
        }
        // Try to find the head, otherwise default to the documentElement
        (document.getElementsByTagName("head")[0] || document.documentElement).appendChild(script_tag);
    } else {
        // The jQuery version on the window is the one we want to use
        de$ = window.jQuery;
        main();
    }

    /******** Called once jQuery has loaded ******/
    function scriptLoadHandler() {
        // Restore $ and window.jQuery to their previous values and store the
        // new jQuery in our local jQuery variable
        de$ = window.jQuery.noConflict(true);
        // Call our main function
        main(); 
    }

    function main() {
        // Add the HTML skeleton, default to 7 logos and navigational arrows
        var numIcons = parseInt(de$('#de-member-carousel').attr("num-icons"));
        de_PgSize = isNaN(numIcons) ? 7 : numIcons;
        var carouselArrows = de$('#de-member-carousel').attr('arrows');
        if (carouselArrows === 'false') {
            de$('#de-member-carousel').append('<span id="de-icon-container"></span>');
        } else {
            de$('#de-member-carousel').append(
                '<a class="prev browse left" id="direct_dotJobsLogoPageLeft"></a>',
                '<a class="next browse right"></a>',
                '<span id="de-icon-container"></span>'
            );
        }

        // Click handler
        de$("#de-member-carousel .browse").click(function(){
            var logoPage = [];
            var direction = de$(this).hasClass("prev") ? -1 : 1;

            // Ensure the starting position is a valid index
            de_startIndex = de_startIndex + (de_PgSize * direction);
            if (de_startIndex < 0) {
                de_startIndex = de_member_cos.length + de_startIndex;
            } else if (de_startIndex >= de_member_cos.length) {
                de_startIndex = de_startIndex - de_member_cos.length;
            }

            // Ensure enough jobs are in the array
            logoPage = de_member_cos.slice(de_startIndex, de_startIndex + de_PgSize);
            if (logoPage.length < de_PgSize) {
                var missing = de_PgSize - logoPage.length;
                logoPage = logoPage.concat(de_member_cos.slice(0, missing));
            }

            de$("#de-icon-container").hide();
            populateCarousel(logoPage);
            de$("#de-icon-container").fadeIn(500);
        });
    }
})();

// Add the style rules for the widget to the document
(function(){
    var css_rules = document.createElement('link');
    css_rules.rel = 'stylesheet';
    css_rules.type = 'text/css';
    css_rules.href = '//d2e48ltfsb5exy.cloudfront.net/widgets/de_icon_bar.css';
    document.getElementsByTagName("head")[0].appendChild(css_rules);
})();

function fisherYates(myArray){
    /*
    Array randomizing function.
    Inputs
        :myArray: array to randomly reorder    
    Returns
        :myArray: randomized Array
    Credit:
        http://sedition.com/perl/javascript-fy.html
    */
    var i = myArray.length;
    if (i == 0) return false;
    while (--i){
        var j = Math.floor( Math.random() * ( i + 1 ) );
        var tempi = myArray[i];
        var tempj = myArray[j];
        myArray[i] = tempj;
        myArray[j] = tempi;
    }
    return myArray;
}

de_startIndex = 0      // initial state for the carousel index

function member_carousel_callback(companies){
    window.de_member_cos = fisherYates(companies);
    populateCarousel(de_member_cos.slice(de_startIndex, de_PgSize));
}

// Get the data using JSONP, triggers a call to member_carousel_callback
(function(){
    var jsonp_tag = document.createElement('script');
    jsonp_tag.src = "//www.my.jobs/ajax/member-companies/jsonp";
    document.getElementsByTagName('body')[0].appendChild(jsonp_tag)
})();

function populateCarousel(cos){
    var co, tag, image;
    var icon_bar = document.getElementById('de-icon-container');
    icon_bar.innerHTML = null;
    for (var i = 0; i < cos.length; i++) {
        co = cos[i];

        image = document.createElement('img');
        image.src = "//d2e48ltfsb5exy.cloudfront.net/100x50/logo.gif";
        image.style.backgroundImage = "url(" + co.image + ")";
        image.alt = co.name + " Careers";
        image.className = "carousel-image"

        tag = document.createElement('a');
        tag.href = co.url.substr(0,4) === 'http' ? co.url : 'http://www.my.jobs' + co.url;
        tag.className = "carousel-icon";
        tag.appendChild(image);

        icon_bar.appendChild(tag);
    };
};