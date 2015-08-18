from django import template
from django.contrib.humanize.templatetags.humanize import naturaltime

from datetime import timedelta, date as date_module
from bleach import clean

register = template.Library()

@register.filter(name='pretty_date')
def date_prettifier(date):
    """
    This assumes that only dates in the past will be encountered.
    :param date:
    :return: humanized date
    """
    if date.date() == date_module.today(): #if it's today
        return naturaltime(date)
    elif date.date() == date_module.today() + timedelta(days=-1): #if it's yesterday
        return "Yesterday at " + date.strftime("%I:%M %p")
    else:
        return date.strftime("%m/%d/%y at %I:%M %p")


@register.filter(name='clean_with_bleach')
def html_cleaner(html):
    allowed_tags = []
    allowed_attributes = []
    styles = []
    return clean(html, tags=allowed_tags, attributes=allowed_attributes, styles=styles,strip=True, strip_comments=True)



@register.inclusion_tag('django_messages/threaded_inclusion_tag_templates/messaging_well.html', takes_context=False)
def messaging_well(*args, **kwargs):
    return None

@register.inclusion_tag('django_messages/threaded_inclusion_tag_templates/messaging_nav_readfilter.html', takes_context=True)
def messaging_nav_readfilter(context, *args, **kwargs):
    return {
        'page_type': context['page_type'],
        'only_read': context['only_read'],
        'only_unread': context['only_unread'],
        'only_unreplied': context['only_unreplied'],
        'django_url': context['django_url'],
    }

@register.inclusion_tag('django_messages/threaded_inclusion_tag_templates/messaging_nav_nofilter.html', takes_context=True)
def messaging_nav_nofilter(context, *args, **kwargs):
    return {
        'page_type': context['page_type'],
    }


@register.inclusion_tag('django_messages/threaded_inclusion_tag_templates/message_table.html', takes_context=True)
def message_table(context, *args, **kwargs):
    return {
        'thread_list': context['thread_list'],
        'header': context['header'],
        'page_type': context['page_type'],
        'only_read': context['only_read'],
        'only_unread': context['only_unread'],
        'only_unreplied': context['only_unreplied'],
        'active_sort': context['active_sort'],
        'django_url': context['django_url'],
    }

@register.simple_tag(name="determine_sort_filter", takes_context=True)
def determiner(context,*args, **kwargs):
    only_unread = context['only_unread']
    only_read = context['only_read']
    active_sort = context['active_sort']
    list_to_join = []
    if active_sort == 'sent_ascending':
        list_to_join.append('&sort_sent=1')
    elif active_sort == 'subject_ascending':
        list_to_join.append('&sort_subject=1')
    elif active_sort == 'subject_descending':
        list_to_join.append('&sort_subject=2')

    if only_read:
        list_to_join.append('&only_read=1')
    elif only_unread:
        list_to_join.append('&only_unread=1')

    return "".join(list_to_join)