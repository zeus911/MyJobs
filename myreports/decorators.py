from functools import partial

from universal.decorators import not_found_when

restrict_to_staff_when = partial(
    not_found_when,
    feature="MyReports",
    message="Feature currently restricted to DirectEmployers staff.")
