import re
from django.conf import settings
from django.db.models import Q

APPEND_TO_SLUG = "-copy"
copy_slug_re = re.compile(r'^.*-copy(?:-(\d)*)?$')

def is_valid_page_slug(page, parent, lang, slug, site):
    """Validates given slug depending on settings.
    """
    from cms.models import Title
    qs = Title.objects.filter(page__site=site, slug=slug, publisher_is_draft=True).exclude(page=page)
    
    if settings.i18n_installed:
        qs = qs.filter(language=lang)
    
    if not settings.CMS_FLAT_URLS:
        if parent and not parent.is_home(): 
            qs = qs.filter(page__parent=parent)
        else:
            qs = qs.filter(page__parent__isnull=True)

    if page.pk:
        qs = qs.exclude(language=lang, page=page)
        
    
    # Only pages which are published in that time period, are counted as overlapping
    #
    # O: Other page (in database)
    # N: New page (or page which is changed)
    # ?S: Start datetime
    # ?E: End datetime
    #
    # We only have to filter if the new/changed page is not always published:
    if not (page.publication_date is None and page.publication_end_date is None):
        # Case: (Other page always published)
        #
        # ------------O--------------
        #
        # OS and OE is None
        qobject = (Q(page__publication_date__isnull=True) & Q(page__publication_end_date__isnull=True))
        
        def oe_none(qobject):
            # Case:
            # 
            # OS-------
            # ??-----NE
            #
            # OS is before NE, when OE is None
            return qobject | (Q(page__publication_date__lt=page.publication_end_date) & Q(page__publication_end_date__isnull=True))
    
        def os_none(qobject):
            # Case:
            # 
            # --------OE
            # NS---------
            #
            # OE is after NS, when OS is None
            return qobject | (Q(page__publication_end_date__gt=page.publication_date) & Q(page__publication_date__isnull=True))
        
        if page.publication_date is None:
            # Case:
            #
            # OS---??
            # -------NE
            #
            # OS is before NE, when NS is None
            qobject |= Q(page__publication_date__lt=page.publication_end_date)
            
            qobject = oe_none(qobject)
        elif page.publication_end_date is None:
            # Case:
            #
            # ??----OE
            # NS-------
            #
            # OE is after NS, when NE is None
            qobject |= Q(page__publication_end_date__gt=page.publication_date)
            
            qobject = os_none(qobject)
        else:            
            # Case:
            #
            #       OS-------OE
            #    NS------NE 
            #
            # OS is after NS but before NE
            qobject |= (Q(page__publication_date__gte=page.publication_date) & Q(page__publication_date__lt=page.publication_end_date))
            # Case
            #
            #    OS-------OE
            #        NS---------NE
            #
            # OE is before NE but after NS
            qobject |= (Q(page__publication_end_date__lte=page.publication_end_date) & Q(page__publication_end_date__gt=page.publication_date))
            # Case
            #
            #  OS----------OE
            #     NS----NE
            #
            # OS is before NS and OE is after NE
            qobject |= (Q(page__publication_date__lte=page.publication_date) & Q(page__publication_end_date__gte=page.publication_end_date))
            
            qobject = oe_none(qobject)
            qobject = os_none(qobject)
    
        qs = qs.filter(qobject)

    if qs.count():
        return False
    return True


def get_available_slug(title, new_slug=None):
    """Smart function generates slug for title if current title slug cannot be
    used. Appends APPEND_TO_SLUG to slug and checks it again.
    
    (Used in page copy function)
    
    Returns: slug
    """
    slug = new_slug or title.slug
    if is_valid_page_slug(title.page, title.page.parent, title.language, slug, title.page.site):
        return slug
    
    # add nice copy attribute, first is -copy, then -copy-2, -copy-3, .... 
    match = copy_slug_re.match(slug)
    if match:
        try:
            next = int(match.groups()[0]) + 1
            slug = "-".join(slug.split('-')[:-1]) + "-%d" % next
        except TypeError:
            slug = slug + "-2"
         
    else:
        slug = slug + APPEND_TO_SLUG
    return get_available_slug(title, slug)


def check_title_slugs(page):
    """Checks page title slugs for duplicity if required, used after page move/
    cut/paste.
    """
    for title in page.title_set.all():
        old_slug = title.slug
        title.slug = get_available_slug(title)
        if title.slug != old_slug:
            title.save()