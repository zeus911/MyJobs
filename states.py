from postajob.models import Job

# A dict that maps state names and their abbreviations to valid synonyms. For
# example, synonyms['IN'] and synonyms['Indiana'] both return ['IN',
# 'Indiana'].
synonyms = dict(
    [(key.lower(), [key, value]) for key, value in Job.get_state_map().items()] +
    [(value.lower(), [key, value]) for key, value in Job.get_state_map().items()])
