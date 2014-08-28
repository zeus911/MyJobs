from postajob.models import Job

# A dict that maps state names and their abbreviations to valid synonyms. For
# example, synonyms['IN'] and synonyms['Indiana'] both return ['IN',
# 'Indiana'].
synonyms = dict(
    [(key, [key, value]) for key, value in Job.get_state_choices()] +
    [(value, [key, value]) for key, value in Job.get_state_choices()])
