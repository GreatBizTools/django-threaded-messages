from django.test import TestCase

from .utils import strip_mail

class UtilsTest(TestCase):
    def test_strip_quotes(self):
        body = """nyan nyan nyan nyan nyan
        nyan nyan nyan nyan nyan

        nyan nyan nyan nyan nyan








        2011/10/28 Nyan Cat <nyan@nyan.cat>:
         > hey guys
        > sarete il 31 dicembre con Pascal a Firenze?
        > lo spero tanto, nel caso ditemi qualcosa...
        >
        >>>
        >
        >>
        >"""

        body_stripped = """nyan nyan nyan nyan nyan
nyan nyan nyan nyan nyan

nyan nyan nyan nyan nyan
"""

        self.assertEquals(body_stripped.strip(), strip_mail(body).strip())

    def test_single_line_quotes(self):
        body = 'asfasf\n\nOn Thu, Dec 15, 2011 at 12:42 PM, Fabrizio S. <messaging@email.gidsy.com>wrote:\n\n>       [image: Gidsy]  New message\n>   Hi Fabrizio, Andrew M. sent you a message\n>\n> *blabla*\n> gasg\n>\n> View and reply<http://email.gidsy.com/wf/click?c=e36x8iH5CyW6UFPc7U%2FiBSpwHwOcqQc55u6Od0IAvnJWLQwR0RdOslgfJYtFkOT0&rp=7%2Bq%2FuBUXPhfnWd079jPZDJw1s3xtQcNITJcDWjO98HB8tJ6%2BYeP23y9SaOFiXvnpboQhDnEJRnrEZfRP9WnHQiL7q9Y0Plign2S9mx7i8%2Bk%3D&u=icfx5E9JS66UPX7QM9UvGw%2Fh0>\n>\n> Sincerely,\n> the *Gidsy team*<http://email.gidsy.com/wf/click?c=nun%2FbaehJTxhIK1KvYwhU5Tg16XMq0b2DKd6IxvO%2F%2Bw%3D&rp=7%2Bq%2FuBUXPhfnWd079jPZDJw1s3xtQcNITJcDWjO98HB8tJ6%2BYeP23y9SaOFiXvnpboQhDnEJRnrEZfRP9WnHQiL7q9Y0Plign2S9mx7i8%2Bk%3D&u=icfx5E9JS66UPX7QM9UvGw%2Fh1>\n>\n> This email was intended for fabrizio@gidsy.com. If you do not want to\n> receive emails like this from staging.gidsy.com<http://email.gidsy.com/wf/click?c=e36x8iH5CyW6UFPc7U%2FiBY72qxV4NIiQfC%2BfF%2BpSEec%3D&rp=7%2Bq%2FuBUXPhfnWd079jPZDJw1s3xtQcNITJcDWjO98HB8tJ6%2BYeP23y9SaOFiXvnpboQhDnEJRnrEZfRP9WnHQiL7q9Y0Plign2S9mx7i8%2Bk%3D&u=icfx5E9JS66UPX7QM9UvGw%2Fh2>anymore, then please change your Email\n> notification settings <http://notice-email-setting/>.\n>\n> Copyright \ufffd 2011 Gidsy.com, All rights reserved.\n>\n'


        body_stripped = "asfasf"
        self.assertEquals(body_stripped.strip(), strip_mail(body).strip())

    def test_strip_signature(self):
        body = 'signature test\n\nOn Fri, Dec 16, 2011 at 11:06 AM, Fabrizio Sestito <fabrizio@gidsy.com>wrote:\n\n> test\n>\n> asd\n>\n>\n> On Fri, Dec 16, 2011 at 11:05 AM, Fabrizio Sestito <fabrizio@gidsy.com>wrote:\n>\n>> hey\n>>\n>>\n>> On Thu, Dec 15, 2011 at 4:08 PM, Fabrizio S. <messaging@email.gidsy.com>wrote:\n>>\n>>>       [image: Gidsy]  New message\n>>>   Hi Fabrizio, Andrew M. sent you a message\n>>>\n>>> *sdfsdf*\n>>> sadasdasdasd\n>>>\n>>> View and reply<http://email.gidsy.com/wf/click?c=e36x8iH5CyW6UFPc7U%2FiBSpwHwOcqQc55u6Od0IAvnLUol8UpZle1eFZgQF40o%2FA&rp=7%2Bq%2FuBUXPhfnWd079jPZDJw1s3xtQcNITJcDWjO98HC6dm1r92yU0SpAJEPbb%2B6TYHFx5ZDq5B8IwoyftFTyY2YZCtQ%2F66rRPRshi2lf8V8%3D&u=wYte5RSXQ3KUXaXN31g4LQ%2Fh0>\n>>>\n>>> Sincerely,\n>>> the *Gidsy team*<http://email.gidsy.com/wf/click?c=nun%2FbaehJTxhIK1KvYwhU5Tg16XMq0b2DKd6IxvO%2F%2Bw%3D&rp=7%2Bq%2FuBUXPhfnWd079jPZDJw1s3xtQcNITJcDWjO98HC6dm1r92yU0SpAJEPbb%2B6TYHFx5ZDq5B8IwoyftFTyY2YZCtQ%2F66rRPRshi2lf8V8%3D&u=wYte5RSXQ3KUXaXN31g4LQ%2Fh1>\n>>>\n>>> This email was intended for fabrizio@gidsy.com. If you do not want to\n>>> receive emails like this from staging.gidsy.com<http://email.gidsy.com/wf/click?c=e36x8iH5CyW6UFPc7U%2FiBY72qxV4NIiQfC%2BfF%2BpSEec%3D&rp=7%2Bq%2FuBUXPhfnWd079jPZDJw1s3xtQcNITJcDWjO98HC6dm1r92yU0SpAJEPbb%2B6TYHFx5ZDq5B8IwoyftFTyY2YZCtQ%2F66rRPRshi2lf8V8%3D&u=wYte5RSXQ3KUXaXN31g4LQ%2Fh2>anymore, then please change your Email\n>>> notification settings <http://notice-email-setting/>.\n>>>\n>>> Copyright \ufffd 2011 Gidsy.com, All rights reserved.\n>>>\n>>\n>>\n>\n\n\n-- \nFabrizio Sestito\n'

        body_stripped = "signature test"
        self.assertEquals(body_stripped.strip(), strip_mail(body).strip())


    def test_no_signature(self):
        pass
        #TODO: add support for stripped html
        #body = '<div>I am some nasty html</div>'
        #body_stripped = "I am some nasty html"
        #self.assertEquals(body_stripped.strip(), strip_mail(body).strip())
