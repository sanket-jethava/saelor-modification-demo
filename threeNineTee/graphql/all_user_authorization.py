from ..account import models

def CommonAuthorization(info):
    data = info.context.META.get('HTTP_AUTHORIZATION')
    if models.LoginSummary.objects.filter(login_token_key=data):
        data = models.LoginSummary.objects.get(login_token_key=data)
        try:
            data = models.User.objects.get(id = data.user_id)
            return True
        except:
            raise Exception("Authorization Failed. Please try again.")    
    else:
        raise Exception("Authorization Failed. Please try again.")

def AdminAuthorization(info):
    data = info.context.META.get('HTTP_AUTHORIZATION')
    if models.LoginSummary.objects.filter(login_token_key=data):
        data = models.LoginSummary.objects.get(login_token_key=data)
        try:
            admindata = models.User.objects.get(id = data.user_id,is_superuser=True,is_staff=True)
            return True
        except:
            raise Exception("Only admin have rights to perform this task.")    
    else:
        raise Exception("Authorization Failed. Please try again.")

def ArtistAuthorization(info):
    data = info.context.META.get('HTTP_AUTHORIZATION')
    if models.LoginSummary.objects.filter(login_token_key=data):
        data = models.LoginSummary.objects.get(login_token_key=data)
        try:
            artistdata = models.User.objects.get(id = data.user_id,is_superuser=False,is_artist=True,is_staff=False,is_buyer=False)
            return True
        except:
            return False
            #raise Exception("Only artist have rights to perform this task.")
    else:
        raise Exception("Authorization Failed. Please try again.")

def B2BUserAuthorization(info):
    data = info.context.META.get('HTTP_AUTHORIZATION')
    if models.LoginSummary.objects.filter(login_token_key=data):
        data = models.LoginSummary.objects.get(login_token_key=data)
        try:
            data = models.User.objects.get(id = data.user_id,is_superuser=False,is_artist=False,is_staff=False,is_buyer=False)
            return True
        except:
            raise Exception("Only B2B user have rights to perform this task.")    
    else:
        raise Exception("Authorization Failed. Please try again.")

def UserAuthorization(info):
    data = info.context.META.get('HTTP_AUTHORIZATION')
    if models.LoginSummary.objects.filter(login_token_key=data):
        data = models.LoginSummary.objects.get(login_token_key=data)
        try:
            data = models.User.objects.get(id = data.user_id,is_superuser=False,is_artist=False,is_staff=False,is_buyer=True)
            return True
        except:
            raise Exception("Only user have rights to perform this task.")    
    else:
        raise Exception("Authorization Failed. Please try again.")

def StaffAuthorization(info):
    data = info.context.META.get('HTTP_AUTHORIZATION')
    if models.LoginSummary.objects.filter(login_token_key=data):
        data = models.LoginSummary.objects.get(login_token_key=data)
        try:
            data = models.User.objects.get(id = data.user_id,is_superuser=False,is_artist=False,is_staff=True,is_buyer=False)
            return True
        except:
            raise Exception("Only staff member have rights to perform this task.")    
    else:
        raise Exception("Authorization Failed. Please try again.")