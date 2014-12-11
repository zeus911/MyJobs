# -*- coding: utf-8 -*-
from itertools import ifilter

from django.contrib.humanize.templatetags.humanize import intcomma
from django.template import Context, Template
from django.template.defaultfilters import safe, urlencode
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

import logging
from seo.templatetags.seo_extras import facet_text, facet_url, smart_truncate


class Widget(object):

    slug_order = {'location': 2, 'title': 1, 'moc': 3, 'facet': 4, 'company': 5,
                  'mapped_moc': 3}
    
    def __init__(self, request, site_config, _type, items, path_dict):
        self.request = request
        self.site_config = site_config
        self._type = _type
        self.items = items
        self.path_dict = path_dict

    def get_req_path(self):
        return self.request.path


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
            criteria_output = _(getattr(self.site_config, "browse_%s_text" % _type))
        num_items = self.site_config.num_filter_items_to_show
        col_hdr = (
            """\
            <h3><span class="direct_filterLabel">%s</span> <span class="direct_highlightedText">%s</span>\
            </h3>\
            """ % (filter_output, criteria_output)
        )
        # Javascript in pager.js uses splits that assume there are no '_'
        # characters in the type
        selector_type = _type.replace('_', '')
        ul_open = '<ul role="menu" id="direct_%sDisambig">' % selector_type
        output = [col_hdr, ul_open]
        counter = 1

        # hidden options is a boolean used to track whether there are more
        # items to display than there are slots to display them. It is False
        # by default, and switched to true if there are hidden fields created
        # or the counter matches or exceeds the num_items value
        hidden_options=False
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
            if counter <= num_items:
                li_class = ""
            else:
                li_class = "direct_hiddenOption"
                hidden_options=True
            
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
            item_template = Template(
                """\
                <li role="menuitem" {% if li_class %} \
                    class='{{li_class}}'{% endif %}>\
                <a href="{{ item_url }}">\
                    {{ item_name }} \
                    {% if item_count %}\
                    ({{ item_count }})\
                    {% endif %}
                </a></li>"""
                )
            
            # render the above template and context into a string variable
            href = item_template.render(item_context)
            
            output.append(href)
            counter += 1

        more_less = (
            """\
            <span id="direct_moreLessLinks_%(type)sDisambig" data-type="%(type)s"\
             class="more_less_links_container" data-num-items="%(num_items)s"\
             data-total-items="%(total_items)s" data-offset="%(offset)s">
              <a class="direct_optionsMore" href="#" rel="nofollow">%(more)s</a>
              <a class="direct_optionsLess" href="#" rel="nofollow">%(less)s</a>
            </span>\
            """ % dict(num_items=self.site_config.num_filter_items_to_show,
                       type=selector_type, total_items=counter,
                       more=more_output, less=less_output,
                       offset=self.site_config.num_filter_items_to_show*2)
            )
 
        output.append('</ul>')
        if hidden_options or self._show_more(items, num_items):
            output.append(more_less)

        return mark_safe('\n'.join(output))

    def _show_more(self, items, num_to_show):
        # 2*num_to_show is currently the max length of items, passed in
        # by helpers.get_widgets
        return len(items) >= 2*num_to_show

    def _show_widget(self, items):
        if self._type == 'featured':
            return True
        else:
            show = getattr(self.site_config, 'browse_{t}_show'.format(t=self._type))

        if self._type == 'facet':
            retval = (bool(len(items)) and show)
        else:
            retval = (len(items) > 1 and show)

        return retval

    def get_abs_url(self, item, *args, **kwargs):
        """
        Calculates the absolute URL for each item in a particular filter
        <ul> tag. It then returns this as a string to be rendered in the
        template.
        
        """
        url_atoms = {'location': '', 'title': '', 'facet': '', 'featured': '',
                     'moc': '', 'company': ''}
        if self._type in ('country', 'city', 'state'):
            t = 'location'
        else:
            t = self._type

        url_atoms[t] = urlencode(facet_url(item[0]))

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
        if item[1]:
            url_atoms = self._build_path_dict(t, url_atoms)
            
        # Create a list of intermediate 2-tuples, with the url_atoms
        # value and the ordering data from self.slug_order. Then sort
        # them based on that ordering data. Finally, join all values
        # from this sorted list to create the canonical URL.
        results = sorted([(url_atoms[k], self.slug_order['company']\
                        if k=='featured' else self.slug_order[k])\
                        for k in url_atoms], key=lambda result: result[1])
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
        for atom in path_map:
            s = '%s_slug' % atom
            if atom != item_type:
                if s in self.path_dict:
                    path_map[atom] = self.path_dict[s].strip('/')

        return path_map
        

class SearchFacetListWidget(FacetListWidget):
    
    def get_abs_url(self, item, *args, **kwargs):
        item_name = safe(smart_truncate(facet_text(item[0])))
        loc_val = self.request.GET.get('location', '')
        moc_val = self.request.GET.get('moc', '')
        t_val = self.request.GET.get('q', '')
        company_val = self.request.GET.get('company', '')
        exact_loc = self.request.GET.get('exact_loc', '')
        exact_title = self.request.GET.get('exact_title', '')
        qs_dict = {'location': loc_val, 'q': t_val, 'company': company_val,
                   'exact_loc': exact_loc, 'exact_title': exact_title}
        if moc_val:
            qs_dict['moc'] = moc_val.split(' - ')[0]

        if self._type in ('city', 'state', 'country', 'cities', 'states',
                          'countries'):
            qs_dict['exact_loc'] = 'true'
            qs_dict['location'] = item_name
        elif self._type in ('moc', 'mocs'):
            qs_dict[self._type] = item_name.split(' - ')[0]
        elif self._type in ('title', 'titles'):
            qs_dict['exact_title'] = 'true'
            qs_dict['q'] = safe(facet_text(item[0]))
        else:
            qs_dict[self._type] = safe(facet_text(item[0]))

        # Using safe_urlencode here because without it, search terms like
        # Düsseldorf will throw an exception since urllib.urlencode chokes
        # on UTF-8 values which can't fail down to ascii.
        return './search?{qs}'.format(qs=safe_urlencode(qs_dict))
