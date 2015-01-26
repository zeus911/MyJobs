# -*- coding: utf-8 -*-
from itertools import ifilter

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template import Context, Template
from django.template.defaultfilters import safe, urlencode
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

import logging
from seo.templatetags.seo_extras import facet_text, facet_url, smart_truncate


def join_paths_of_same_type(item_type, path1, path2):
    """
    Combines two paths of the same slug type into a single path.

    :param item_type: The type types of paths that are being
                      combined - e.g. 'facet' or 'location'
    :param path1: The first path to combine.
    :param path2: The other path to combine.

    :return: path1 and path2 combined as a single path. If the path
             contains multiple slugs the slugs will be sorted
             alphabetically.

    """
    # The "featured" item_type corresponds to feature company,
    # which for the purpose of a slug tag is just company.
    item_type = 'company' if item_type == 'featured' else item_type
    slug_tag = "%s_slug" % item_type
    slug_tag = settings.SLUG_TAGS[slug_tag]

    new_path = "%s/%s" % (path1, path2)

    # Strip out the slug tag so it can be sorted.
    new_path = new_path.replace(slug_tag, '/')

    # Sort them alphabetically.
    new_path = new_path.split('/')
    new_path = sorted(new_path)

    # Recombine and readd the slug tag.
    new_path = "/".join(new_path)
    new_path = "%s/%s" % (new_path, slug_tag.strip('/'))
    return new_path


class FacetListWidget(object):
    """
    HTML Widget which renders Custom Facets & other facets in an HTML list.

    """
    slug_order = {'title': 1, 'location': 2, 'moc': 3, 'facet': 4, 'company': 5,
                  'featured': 5, 'mapped_moc': 3}
    
    def __init__(self, request, site_config, _type, items, filters,
                 offset=None, query_string=None):
        self.request = request
        self.site_config = site_config

        self.widget_type = _type
        self.selector_type = self.widget_type.replace('_', '')

        self.items = filter(lambda x: x[0], items)
        self.path_dict = self.filters_to_paths(filters.copy())
        self.num_to_show = self.site_config.num_filter_items_to_show
        self.offset = offset or self.num_to_show * 2

        if hasattr(request, 'META') and not query_string:
            self.query_string = query_string or request.META.get('QUERY_STRING')
        else:
            self.query_string = query_string or ''

        self._num_items_rendered = 0
        self._has_hidden_items = False

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

    def facet_type_to_slug(self):
        if self.widget_type in ['city', 'state', 'country']:
            return 'location_slug'
        elif self.widget_type in ['featured', 'company']:
            return 'company_slug'
        return '%s_slug' % self.widget_type

    def get_title(self):
        """
        Gets the "Browse by ___" title for the widget.

        :return: A string containing the title.

        """
        if self.widget_type == 'featured':
            return 'Featured Company'

        # When you add custom keywords to a microsite, you will need to manually
        # enter a translation to directseo/locale<LANG>/LC_MESSAGES/django.po
        # for each language. Examples are "Profession" or "Area".
        facet_title_field = 'browse_%s_text' % self.widget_type
        facet_title = getattr(self.site_config, facet_title_field)
        return _(facet_title)

    def render(self):
        """
        :return: A string containing the facets in self.items rendered as a ul.

        """
        self._has_hidden_items = False
        self._num_items_rendered = 1

        if not self._show_widget(self.items):
            return

        output = [self._as_ul()]

        if self._has_hidden_items or self._show_more(self.items):
            more_less = self._render_more_less()
            output.append(more_less)

        return mark_safe('\n'.join(output))

    def _render_li(self, item):
        """
        Turns a facet tuple into an li containing the correct link
        to the item.

        :param item: A facet (slug, count) tuple to be rendered.
        :return: The <li></li> block representing the item.

        """
        try:
            item_name = safe(smart_truncate(facet_text(item[0])))
        except IndexError:
            # Even though this will issue a log msg for each failed
            # iteration, I put all items in each message for easy
            # access to all the slabs in any given message.
            logging.critical('IndexError while splitting slabs',
                             extra={'data': {'slab_items': self.items}})
            return None
        if item_name in ('None', '') or item_name.startswith("Virtual"):
            return None

        item_url = self.get_abs_url(item)

        if self._num_items_rendered <= self.num_to_show:
            li_class = ""
        else:
            li_class = "direct_hiddenOption"
            self._has_hidden_items = True

        # build item_count using humanized. This is usally called inside the
        # django template, but this widget doesn't use a specific template
        # so it makes more sense to do it directly in the python here.
        item_count = intcomma(item[1]) if item[1] else False

        if self.widget_type == 'facet':
            # When this was added most of the custom facet
            # names ended with " Jobs" (for prettier titles). In order to
            #  ensure that the slugs/paths for these facets remained the
            # same, we decided to keep " Jobs" in these slugs, so it needs
            # stripped out to match all the other facet types that
            # don't end in " Jobs".
            if item_name.endswith(" Jobs"):
                item_name = item_name[:-5]

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

        return href

    def _render_lis(self):
        """
        Renders all the items in self.items.

        :return: A list of all of the rendered items.

        """
        rendered_items = []
        for item in self.items:
            rendered_item = self._render_li(item)
            if rendered_item:
                rendered_items.append(rendered_item)
                self._num_items_rendered += 1
        self._num_items_rendered += len(rendered_items)
        return rendered_items

    def _as_ul(self):
        """
        Renders the complete ul containing li items for all valid items
        in self.items.

        :return: A string containing the rendered ul.

        """
        column_header = ('<h3><span class="direct_filterLabel">%s</span> '
                         '<span class="direct_highlightedText">%s</span></h3>')
        column_header = column_header % (_("Filter by"), self.get_title())

        # Javascript in pager.js uses splits that assume there are no '_'
        # characters in the type
        ul_open = '<ul role="menu" id="direct_%sDisambig">'
        ul_open = ul_open % self.selector_type

        output = [column_header, ul_open]

        list_items = self._render_lis()
        output = output + list_items

        output.append('</ul>')
        return ''.join(output)

    def _render_more_less(self):
        """
        :return: A string containing the span with the
                 "More" and "Less" buttons.

        """
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

        more_less = more_less % dict(num_items=self.num_to_show,
                                     type=self.selector_type,
                                     total_items=self._num_items_rendered,
                                     more=_("More"),
                                     less=_("Less"),
                                     offset=self.offset)
        return more_less

    def _show_more(self, items):
        # 2 * num_to_show is currently the max length of items, passed in
        # by helpers.get_widgets
        return len(items) >= 2 * self.num_to_show

    def _show_widget(self, items):
        if self.widget_type == 'featured':
            return True

        show_field = 'browse_{t}_show'.format(t=self.widget_type)
        show = getattr(self.site_config, show_field)

        if self.widget_type == 'facet':
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

        if self.widget_type in ('country', 'city', 'state'):
            facet_type = 'location'
        else:
            facet_type = self.widget_type

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
            url = ("%s?%s" % (url, self.query_string)
                   if self.query_string else url)

        return url

    def _build_path_dict(self, item_type, path_map):
        # This loop transfers any URL information from the
        # path_dict (which is the existing path broken down by filter type)
        # to the url_atoms dict after stripping leading/trailing
        # slashes.
        for atom, path in path_map.iteritems():
            if atom in self.path_dict:
                allow_multiple = settings.ALLOW_MULTIPLE_SLUG_TAGS[atom]
                if atom == item_type and allow_multiple:
                    existing_path = self.path_dict[atom]
                    new_path = join_paths_of_same_type(item_type, path,
                                                       existing_path)
                    # The code that builds out urls assumes the path
                    #  doesn't start with a '/'
                    new_path = new_path.lstrip('/')

                    path_map[atom] = new_path
                elif atom != item_type:
                    path_map[atom] = self.path_dict[atom].strip('/')
        return path_map
