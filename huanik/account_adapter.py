from allauth.account.adapter import DefaultAccountAdapter

class NoNewUsersAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        # 禁止本地注册
        return False

    def clean_password(self, password, user=None):
        # 阻止用户本地设置密码
        raise NotImplementedError("Password login not supported")
