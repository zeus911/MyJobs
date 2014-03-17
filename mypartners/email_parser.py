from datetime import datetime
from email.utils import getaddresses, parsedate
from re import compile, findall, split
from time import mktime

header_block = compile('((?:.{0,10}?(?:From|To|CC|Cc|Date|Sent|Subject): .*\n){4,})')
header_line = compile('((?:.{0,10}?(From|To|CC|Cc|Date|Sent|Subject): (.*))\n)')


def get_forward_headers(email_body):
    return findall(header_block, email_body)


def parse_forward_header(header_str):
    header_dict = {}
    header_bits = header_line.findall(header_str)
    for bit in header_bits:
        try:
            header_dict[bit[1]] = bit[2]
        except KeyError:
            pass

    return header_dict


def get_forward_header_dict(header_str):
    header = parse_forward_header(header_str)
    date = header.get('Date') if 'Date' in header else header.get('Sent')
    sender = header.get('From')
    to = header.get('To', '')
    cc = header.get('CC') if 'CC' in header else header.get('Cc', '')

    date_time = (mktime(parsedate(date.replace(" at", "")))) if date else None
    date_time = datetime.fromtimestamp(date_time) if date_time else None
    from_email = getaddresses([sender]) if sender else None
    to_addresses = getaddresses([header.get('To', '')]) if to else []
    cc_addresses = getaddresses([cc]) if cc else []
    recipient_addresses = to_addresses + cc_addresses

    return {
        'from': from_email,
        'to': to_addresses,
        'cc': cc_addresses,
        'recipients': recipient_addresses,
        'date': date_time,
        'subject': header.get('Subject'),
        'header': header_str,
    }


def sort_dict_by_date(headers_list, descending=True):
    return sorted(headers_list, key=lambda k: k['date'], reverse=descending)


def get_email_body_for_header(split_body, header_str):
    try:
        index = split_body.index(header_str)
        return split_body[index+1]
    except (IndexError, ValueError):
        return ''


def build_email_dicts(email_body):
    headers = get_forward_headers(email_body)
    headers = [get_forward_header_dict(header) for header in headers]
    split_body = split(header_block, email_body)

    for header in headers:
        header['body'] = get_email_body_for_header(split_body, header['header'])

    return sort_dict_by_date(headers)