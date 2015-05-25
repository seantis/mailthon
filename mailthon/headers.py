"""
    mailthon.headers
    ~~~~~~~~~~~~~~~~

    Implements RFC compliant headers, and is the
    recommended way to put headers into enclosures
    or envelopes.

    :copyright: (c) 2015 by Eeo Jun
    :license: MIT, see LICENSE for details.
"""

from email.utils import quote, formatdate, make_msgid, getaddresses


class Headers(dict):
    """
    RFC 2822 compliant subclass of a dictionary. The
    semantics of the dictionary is different from
    that of the standard library MIME object- only
    the latest header is preserved instead of
    preserving all headers. This makes header lookup
    deterministic and sane.
    """

    @property
    def resent(self):
        """
        Tells whether the email was resent, i.e.
        whether the ``Resent-Date`` header was set.
        """
        return 'Resent-Date' in self

    @property
    def sender(self):
        """
        Returns the sender, respecting the Resent-*
        headers. In any case, prefer Sender over From,
        meaning that if Sender is present then From is
        ignored, as per the RFC.
        """
        to_fetch = (
            ['Resent-Sender', 'Resent-From'] if self.resent else
            ['Sender', 'From']
        )
        for item in to_fetch:
            if item in self:
                return self[item]

    @property
    def receivers(self):
        """
        Returns a list of receivers, obtained from the
        To, Cc, and Bcc headers, respecting the Resent-*
        headers if the email was resent.
        """
        attrs = (
            ['Resent-To', 'Resent-Cc', 'Resent-Bcc'] if self.resent else
            ['To', 'Cc', 'Bcc']
        )
        addrs = (f for f in (self.get(item) for item in attrs) if f)
        return [a[1] for a in getaddresses(addrs)]

    def prepare(self, mime):
        """
        Preprares a MIME object by applying the headers
        to the *mime* object. Ignores any Bcc or
        Resent-Bcc headers.
        """
        for key in self:
            if key == 'Bcc' or key == 'Resent-Bcc':
                continue
            del mime[key]
            mime[key] = self[key]


def subject(text):
    """
    Generates a Subject header with a given *text*.
    """
    yield 'Subject'
    yield text


def sender(address):
    """
    Generates a Sender header with a given *text*.
    """
    yield 'Sender'
    yield address


def to(*addrs):
    """
    Generates a To header with the given *addrs*,
    where addrs can be made of ``Name <address>``
    or ``address`` strings, or a mix of both.
    """
    yield 'To'
    yield ', '.join(addrs)


def cc(*addrs):
    """
    Similar to ``to`` function. Generates a Cc
    hedaer.
    """
    yield 'Cc'
    yield ', '.join(addrs)


def bcc(*addrs):
    """
    Generates a Bcc header. This is safe when using
    the mailthon Headers implementation because the
    Bcc headers will not be included in the MIME
    object.
    """
    yield 'Bcc'
    yield ', '.join(addrs)


def content_disposition(disposition, filename):
    """
    Generates a content disposition hedaer given
    a *disposition* and a *filename*. The filename
    needs to be the base name of the path, i.e.
    instead of ``~/file.txt`` you need to pass in
    ``file.txt``. The filename is automatically
    quoted.
    """
    yield 'Content-Disposition'
    yield '%s; filename="%s"' % (disposition, quote(filename))


def date(time=None):
    """
    Generates a Date header. Yields the *time*
    as the key if specified, else returns an
    RFC compliant date generated by formatdate.
    """
    yield 'Date'
    yield time or formatdate(localtime=True)


def message_id(string=None, idstring=None):
    """
    Generates a Message-ID header, by yielding a
    given *string* if specified, else an RFC
    compliant message-id generated by make_msgid
    and strengthened by an optional *idstring*.
    """
    yield 'Message-ID'
    yield string or make_msgid(idstring)
