from ...checkout import models
from ...core.permissions import CheckoutPermissions
from ..utils import get_user_or_app_from_context
from ..all_user_authorization import AdminAuthorization, B2BUserAuthorization, UserAuthorization
from threeNineTee.graphql.core.utils import from_global_id_strict_type
from ...account.models import Address, User

def resolve_checkout_lines():
    queryset = models.CheckoutLine.objects.all()
    return queryset


def resolve_checkouts():
    queryset = models.Checkout.objects.all()
    return queryset


def resolve_checkout(info, token):
    checkout = models.Checkout.objects.filter(token=token).first()

    if checkout is None:
        return None

    # resolve checkout for anonymous customer
    if not checkout.user:
        return checkout

    # resolve checkout for logged-in customer
    if checkout.user == info.context.user:
        return checkout

    # resolve checkout for staff user
    requester = get_user_or_app_from_context(info.context)
    if requester.has_perm(CheckoutPermissions.MANAGE_CHECKOUTS):
        return checkout

    return None

#Checkout address
def resolve_checkout_addresses(info,uid):
    if UserAuthorization(info):
        try:
            uid = from_global_id_strict_type(uid, only_type="User", field="pk") #onlytype me iska type

            a = User.objects.get(id=uid)
            b = a.addresses
            all_data = b.filter(user_addresses=uid)
            # all_data = Address.objects.all()
            
            return all_data
        except Exception as e:
            pass

#Checkout address testing
def resolve_checkout_address(info,uid):
    if UserAuthorization(info):
        try:
            uid = from_global_id_strict_type(uid, only_type="Address", field="pk") #onlytype me iska type

            # a = User.objects.get(id=uid)
            # b = a.addresses
            # all_data = b.filter(user_addresses=uid)
            all_data = Address.objects.get(id=uid)
            return all_data
        except Exception as e:
            pass

