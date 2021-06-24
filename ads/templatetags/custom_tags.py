from django import template
from hashlib import md5
from django.template.defaultfilters import stringfilter

register = template.Library()



@register.filter(name='get_tag')
@stringfilter
def get_tag_from_url(value, x):
    list_of_words = value.split('/')
    tag = list_of_words[-1]
    return tag


@register.filter(name='gravatar')
def gravatar(user, size=35):
    email = str(user.email.strip().lower()).encode('utf-8')
    email_hash = md5(email).hexdigest()
    url = "//www.gravatar.com/avatar/{0}?s={1}&d=identicon&r=PG"
    return url.format(email_hash, size)
