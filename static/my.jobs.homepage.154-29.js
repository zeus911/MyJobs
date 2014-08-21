$(document).ready(function(){rotate_tagline();});

function rotate_tagline(){
    /*
    Rotates the tagline target audience keyword.

    Inputs: none
    Returns: none (DOM manipulation)
    */
    var tagline = $('#direct_tagline a'),
        phrases = ["Compliance",
                   "Jobs",
                   "Employers",
                   "Diversity",
                   "Veterans"],
        fadeDuration = 1500,
        random_phrases = shuffle(phrases),
        loop = function(index, list) {
    	    if(index == list.length) return false;

    	    tagline.fadeOut(fadeDuration/5, function() {
    		    tagline.html(list[index]);
    	    })
    	    .fadeIn(fadeDuration, function() {
    		    loop(index + 1, list);
    	    });
        };

    tagline.html(random_phrases[0]);
    tagline.fadeIn('fast');
    var selected_phrases = random_phrases.slice(0,3);
    selected_phrases[selected_phrases.length] = "You.";
    setTimeout(function() {
    	loop(1, selected_phrases);
    }, fadeDuration);
}

function shuffle(list) {
    /*
    Fisher-Yates Shuffle

    Inputs:
    :list:      The source array

    Returns:
    :list:      A randomized array
    */
    var i = list.length;
    if(i == 0) return false;
    while(--i) {
    	var j = Math.floor( Math.random() * (i + 1) ),
    	tempi = list[i],
    	tempj = list[j];
    	list[i] = tempj;
    	list[j] = tempi;
    }
    return list;
}
