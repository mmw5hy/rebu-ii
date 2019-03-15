// This file contains the onclick method to allow horizontal bars

function favoritesScroll(rightScroll, numb) {
    /* Scroll horizontal-scroll-numb

    Scrolls the element with id "horizontal-scroll-<numb>" right (if rightScroll
    is True) or left (if rightScroll is False). The element will be scrolled by
    one elements width. This method will not scroll past an edge.

    Attributes:
        rightScroll (bool): Boolean determining whether to scroll right.
                            False means scroll left.
        numb (int): Element with id "horizontal-scroll-<numb>" will be scrolled
    */
    var container = document.getElementById('horizontal-scroll-'+numb);
    var elementWidth = container.firstElementChild.getBoundingClientRect().width;
    scrollAmount = 0
    distance = elementWidth + 6;
    step = elementWidth/10.;
    finalScroll = container.scrollLeft;
    if (rightScroll) {
        finalScroll += distance;
    } else {
        finalScroll -= distance;
    }
    var slideTimer = setInterval(function() {
        if (rightScroll) {
            container.scrollLeft += step;
            if (container.scrollLeft > 0) {
                document.getElementById('scroll-left-btn-'+numb).style.visibility = "visible"
            }
            if (container.scrollLeft == (container.scrollWidth - container.offsetWidth)) {
                document.getElementById('scroll-right-btn-'+numb).style.visibility = "hidden"
            }
        } else {
            container.scrollLeft -= step;
            if (container.scrollLeft == 0) {
                document.getElementById('scroll-left-btn-'+numb).style.visibility = "hidden"
            }
            if (container.scrollLeft < (container.scrollWidth - container.offsetWidth)) {
                document.getElementById('scroll-right-btn-'+numb).style.visibility = "visible"
            }
        }
        scrollAmount += step;
        if (scrollAmount >= distance) {
            container.scrollLeft = finalScroll;
            window.clearInterval(slideTimer)
        }
    }, 25);
}
