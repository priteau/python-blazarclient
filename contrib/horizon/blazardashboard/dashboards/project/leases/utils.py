from blazardashboard.api import blazar
from django.utils.translation import ugettext_lazy as _


def reservation_data(request, include_empty_option=False):
    """Returns a list of tuples of all reservations for a user.

    Generates a list of reservations available. And returns a list of
    (id, name) tuples.

    :param request: django http request object
    :param include_empty_option: flag to include a empty tuple in the front of
        the list
    :return: list of (id, name) tuples
    """

    leases = blazar.lease_list(request)
    if leases:
        reservations = []
        for l in leases:
            reservations += [(r['id'], '{} ({})'.format(l['name'], r['id']))
                             for r in l.reservations if r['status'] == 'active']

        if include_empty_option:
            return [('', _('Select Reservation')), ] + reservations
        else:
            return reservations

    if include_empty_option:
        return [('', _('No Reservation Available')), ]
    return []
