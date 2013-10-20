from module.plugins.Account import Account
from module.common.json_layer import json_loads

class RPNetBiz(Account):
    __name__ = "RPNetBiz"
    __version__ = "0.1"
    __type__ = "account"
    __description__ = """RPNet.biz account plugin"""

    __author_name__ = ("Dman")
    __author_mail__ = ("dmanugm@gmail.com")

    def loadAccountInfo(self, user, req):
        
        # Get account information from rpnet.biz
        response = self.getAccountStatus(user, req)
        # Parse account info. Change the trafficleft later to support per host info.
        account_info = {"validuntil": int(response['accountInfo']['premiumExpiry']),
                        "trafficleft": -1} 

        return account_info

    def login(self, user, data, req):
        
        # Get account information from rpnet.biz
        response = self.getAccountStatus(user, req)
        
        # If we have an error in the response, we have wrong login information
        if 'error' in response:
            self.wrongPassword()
    
    def getAccountStatus(self, user, req):
        
        # Using the rpnet API, check if valid premium account
        response = req.load("https://premium.rpnet.biz/client_api.php?username=%s&password=%s&action=showAccountInformation" % (user, self.accounts[user]['password']))            
        return json_loads(response)