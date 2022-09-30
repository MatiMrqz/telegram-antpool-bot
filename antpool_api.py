import time
import hmac
import hashlib
import ssl
import requests
# coin_type = 'BTC'
# sign_id = 'matimrqz'
# sign_key = 'e0a4e166a2fd4d5a95f77779ade58b5f'
# sign_SECRET = '546fed479a2d474ab95539656e483102'
html_poolstats = 'https://antpool.com/api/poolStats.htm'
html_balance = 'https://antpool.com/api/account.htm'
html_hashrate_user = 'https://antpool.com/api/hashrate.htm'
html_hashrate_miner = 'https://antpool.com/api/workers.htm'
html_payment = 'https://antpool.com/api/paymentHistory.htm'
html_sub_overview = 'https://antpool.com/api/accountOverview.htm'
html_user_hash_chart = 'https://antpool.com/api/userHashrateChart.htm'


class AntApi:
    def __init__(self) -> None:
        pass

    def __get_signature(self, user):
        print(user)
        nonce = int(time.time()*1000)
        msgs = user['sign_id']+user['sign_key']+str(nonce)
        ret = []
        ret.append(hmac.new(user['sign_SECRET'].encode(encoding="utf-8"), msg=msgs.encode(
            encoding="utf-8"), digestmod=hashlib.sha256).hexdigest().upper())
        ret.append(nonce)
        return ret

    def __get_messages(self, url: str, user: dict, post_data_type: int):  # POST
        api_sign = self.__get_signature(user)
        post_data = {
            1: {'key': user['sign_key'], 'nonce': api_sign[1], 'signature': api_sign[0], 'coin': user['coin_type'], 'userId': user['sign_id']},
            2: {'key': user['sign_key'], 'nonce': api_sign[1], 'signature': api_sign[0], 'coin': user['coin_type'], 'clientUserId': user['sign_id'], 'pageEnable': 0},
            3: {'key': user['sign_key'], 'nonce': api_sign[1], 'signature': api_sign[0], 'coinType': user['coin_type'], 'userId': user['sign_id'], 'type': 3}
        }
        # post_data = {'key': sign_key, 'nonce': api_sign[1],'signature': api_sign[0],'coin':coin_type, 'clientUserId':sign_id,'pageEnable':0}
        # post_data = {'key': sign_key, 'nonce': api_sign[1],'signature': api_sign[0],'coinType':coin_type, 'userId':sign_id, 'type':3}#这里是POST参数根据接口自行更改
        request = requests.post(url, data=post_data.get(post_data_type))
        return (request.text)

    def pool_stats(self, u_parameters: dict):
        return self.__get_messages(html_poolstats, u_parameters, 1)
    
    def sub_overview(self,u_parameters:dict):
        return self.__get_messages(html_sub_overview, u_parameters, 1)


if __name__ == "__main__":
    ant = AntApi()
    user: dict = {"sign_id": 'matimrqz', "sign_key": 'e0a4e166a2fd4d5a95f77779ade58b5f',
                  "sign_SECRET": '546fed479a2d474ab95539656e483102', "coin_type": 'BTC'}
    print(ant.pool_stats(user))
