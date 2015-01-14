# -*- coding: utf-8 -*-
from itertools import ifilter
from pysolr import safe_urlencode

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template import Context, Template
from django.template.defaultfilters import safe, urlencode
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

import logging
from seo.templatetags.seo_extras import facet_text, facet_url, smart_truncate


class Widget(object):
    slug_order = {'location': 2, 'title': 1, 'moc': 3, 'facet': 4, 'company': 5,
                  'featured': 5, 'mapped_moc': 3}
    
    def __init__(self, request, site_config, _type, items, filters,
                 offset=None):
        self.request = request
        self.site_config = site_config
        self._type = _type
        self.items = items
        self.path_dict = self.filters_to_paths(filters.copy())
        self.num_items = self.site_config.num_filter_items_to_show
        self.offset = offset or self.num_items * 2

    def get_req_path(self):
        return self.request.path

    @staticmethod
    def filters_to_paths(filters):
        path_dict = {}
        for slug_type, value in filters.iteritems():
            path = ("%s%s" % (value, settings.SLUG_TAGS[slug_type])
                    if value else '')
            path_dict[slug_type.replace('_slug', '')] = path
        return path_dict


class FacetListWidget(Widget):
    """
    HTML Widget which renders Custom Facets & other facets in an HTML list.

    """
    def render(self):
        _type = self._type
        items = filter(lambda x: x[0], self.items)

        if not self._show_widget(items):
            return

        # When you add custom keywords to a microsite, you will need to manually
        # enter a translation to directseo/locale<LANG>/LC_MESSAGES/django.po
        # for each language. Examples are "Profession" or "Area".
        filter_output = _("Filter by ")
        more_output = _("More")
        less_output = _("Less")
        if self._type == 'featured':
            criteria_output = 'Featured Company'
        else:
            criteria_output = _(getattr(self.site_config, "browse_%s_text"
                                        % _type))

        column_header = ('<h3><span class="direct_filterLabel">%s</span> '
                         '<span class="direct_highlightedText">%s</span></h3>')
        column_header = column_header % (filter_output, criteria_output)

        # Javascript in pager.js uses splits that assume there are no '_'
        # characters in the type
        selector_type = _type.replace('_', '')
        ul_open = '<ul role="menu" id="direct_%sDisambig">' % selector_type

        output = [column_header, ul_open]
        counter = 1

        # hidden options is a boolean used to track whether there are more
        # items to display than there are slots to display them. It is False
        # by default, and switched to true if there are hidden fields created
        # or the counter matches or exceeds the num_items value
        hidden_options = False

        for item in items:
            try:
                item_name = safe(smart_truncate(facet_text(item[0])))
            except IndexError:
                # Even though this will issue a log msg for each failed
                # iteration, I put all items in each message for easy
                # access to all the slabs in any given message.
                logging.critical('IndexError while splitting slabs',
                                 extra={
                                     'data': {
                                         'slab_items': items
                                     }
                                 })
                continue
            if item_name in ('None', '') or item_name.startswith("Virtual"):
                continue
                
            item_url = self.get_abs_url(item)
            if counter <= self.num_items:
                li_class = ""
            else:
                li_class = "direct_hiddenOption"
                hidden_options = True
            
            # build item_count using humanized. This is usally called inside the
            # django template, but this widget doesn't use a specific template
            # so it makes more sense to do it directly in the python here.
            item_count = intcomma(item[1]) if item[1] else False
            
            # Use the django templating system to provide richer string parsing
            item_context = Context({
                "li_class": li_class,
                "item_url": item_url, 
                "item_name": item_name, 
                "item_count": item_count,
            })

            li_item = ('<li role="menuitem" '
                       '{% if li_class %}class="{{li_class}}"{% endif %}>'
                       '<a href="{{ item_url }}">'
                       '{{ item_name }}{% if item_count %} ({{ item_count }})'
                       '{% endif %}</a></li>')
            item_template = Template(li_item)
            href = item_template.render(item_context)
            
            output.append(href)
            counter += 1

        more_less = ('<span id="direct_moreLessLinks_%(type)sDisambig" '
                     'data-type="%(type)s" '
                     'class="more_less_links_container" '
                     'data-num-items="%(num_items)s" '
                     'data-total-items="%(total_items)s" '
                     'data-offset="%(offset)s">'

                     '<a class="direct_optionsMore" '
                     'href="#" rel="nofollow">%(more)s</a>'

                     '<a class="direct_optionsLess" href="#" '
                     'rel="nofollow">%(less)s</a>'

                     '</span>')
        more_less = more_less % dict(num_items=self.num_items,
                                     type=selector_type, total_items=counter,
                                     more=more_output, less=less_output,
                                     offset=self.offset)
 
        output.append('</ul>')

        if hidden_options or self._show_more(items, self.num_items):
            output.append(more_less)

        return mark_safe('\n'.join(output))

    def _show_more(self, items, num_to_show):
        # 2*num_to_show is currently the max length of items, passed in
        # by helpers.get_widgets
        return len(items) >= 2 * num_to_show

    def _show_widget(self, items):
        if self._type == 'featured':
            return True

        show = getattr(self.site_config, 'browse_{t}_show'.format(t=self._type))

        if self._type == 'facet':
            retval = (bool(len(items)) and show)
        else:
            retval = (len(items) > 1 and show)

        return retval

    def get_abs_url(self, facet):
        """
        Calculates the absolute URL for each item in a particular filter
        <ul> tag. It then returns this as a string to be rendered in the
        template.
        
        """
        facet_slab, facet_count = facet
        url_atoms = {'location': '', 'title': '', 'facet': '', 'featured': '',
                     'moc': '', 'company': ''}

        if self._type in ('country', 'city', 'state'):
            facet_type = 'location'
        else:
            facet_type = self._type

        url_atoms[facet_type] = urlencode(facet_url(facet_slab))

        # For custom facets where the "show with or without results" option
        # is checked, we don't want to build out a path relative to the
        # user's current location; the user should just be taken to the page
        # for the custom facet. For example, if a user browses to
        # /north-carolina/usa/jobs then clicks on "CAReer Talent" custom facet
        # for DTNA, and that custom facet has zero results, we don't want the
        # user to go to /north-carolina/usa/jobs/career-talent/new-jobs, but
        # /career-talent/new-jobs.
        #
        # So if the count of jobs is zero, don't execute the process that
        # builds URL path relative to current location :) Clear as mud.
        # Don't worry, we'll take this out once we have proper static pages
        # implemented.
        if facet_count:
            url_atoms = self._build_path_dict(facet_type, url_atoms)
            
        # Create a list of intermediate 2-tuples, with the url_atoms
        # value and the ordering data from self.slug_order.
        url_orders = [(url_atoms[key], self.slug_order[key])
                      for key in url_atoms]

        # Sort them based on that ordering data.
        results = sorted(url_orders, key=lambda result: result[1])

        # Join all values from this sorted list to create
        # the canonical URL.
        url = '/%s/' % '/'.join([i[0] for i in
                                ifilter(lambda r: r[0], results)])

        if hasattr(self.request, 'META'):
            url = "%s?%s" % (url, self.request.META.get('QUERY_STRING'))\
                if self.request.META.get('QUERY_STRING', None) else url

        return url

    def _build_path_dict(self, item_type, path_map):
        # This loop transfers any URL information from the path_dict
        # (which is the bread_box_path from home_page/job_list_by_slug_tag
        # views) to the url_atoms dict after stripping leading/trailing
        # slashes.
        for atom, path in path_map.iteritems():
            if atom in self.path_dict:
                allow_multiple = settings.ALLOW_MULTIPLE_SLUG_TAGS[atom]
                if atom == item_type and allow_multiple:
                    # The "featured" item_type corresponds to feature company,
                    # which for the purpose of a slug tag is just company.
                    slug_tag_type = ('company' if item_type == 'featured'
                                     else item_type)
                    slug_tag = "%s_slug" % slug_tag_type
                    slug_tag = settings.SLUG_TAGS[slug_tag]


                    new_path = "%s/%s" % (path, self.path_dict[atom].strip('/'))


                    # Strip out the slug tag so it can be sorted.
                    new_path = new_path.replace(slug_tag, '')
                    print new_path

                    # Sort them alphabetically.
                    new_path = new_path.split('/')
                    new_path = sorted(new_path)

                    # Recombine and readd the slug tag.
                    new_path = "/".join(new_path)
                    new_path = "%s/%s" % (new_path, slug_tag.strip('/'))

                    path_map[atom] = new_path
                elif atom != item_type:
                    path_map[atom] = self.path_dict[atom].strip('/')
        return path_map
