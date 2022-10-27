from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        data = form.cleaned_data
        print("data", data)
        # 기본 저장 필드: first_name, last_name, username, email
        user = super().save_user(request, user, form, False)
        print("user", user) 
        name = data.get("name")
        if name:
            user.name = name
        print("new user", user)
        user.save()
        return user