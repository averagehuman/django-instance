

# borrowed from mezzanine.utils.views
def paginate(objects, page_num, per_page=None, max_paging_links=None):
    """
    Return a paginated page for the given objects, giving it a custom
    ``visible_page_range`` attribute calculated from ``max_paging_links``.
    """
    from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
    from instance.conf import settings
    if per_page is None:
        per_page = settings.get('DEFAULT_PAGINATION_ITEMS', 30)
    if max_paging_links is None:
        max_paging_links = settings.get('DEFAULT_PAGINATION_MAX_LINKS', 10)
    if not per_page:
        return Paginator(objects, 0)
    paginator = Paginator(objects, per_page)
    try:
        objects = paginator.page(page_num)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    page_range = objects.paginator.page_range
    if len(page_range) > max_paging_links:
        start = min(objects.paginator.num_pages - max_paging_links,
            max(0, objects.number - (max_paging_links // 2) - 1))
        page_range = page_range[start:start + max_paging_links]
    objects.visible_page_range = page_range
    return objects

