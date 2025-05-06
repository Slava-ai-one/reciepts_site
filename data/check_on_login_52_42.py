class Checking_login_im_inspect_you_shell_not_pass():
    def __init__(self):
        self.login_check_52_42 = 0

    def logined(self):
        self.login_check_52_42 = 1

    def ulogin(self):
        self.login_check_52_42 = 0

    def check(self):
        return self.login_check_52_42 == 1