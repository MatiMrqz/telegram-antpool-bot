import time
import hmac,hashlib
import ssl,requests
coin_type='BTC'
sign_id='matimrqz'
sign_key='e0a4e166a2fd4d5a95f77779ade58b5f'
sign_SECRET='546fed479a2d474ab95539656e483102'
html_poolstats='https://antpool.com/api/poolStats.htm'
html_balance='https://antpool.com/api/account.htm'
html_hashrate_user='https://antpool.com/api/hashrate.htm'
html_hashrate_miner='https://antpool.com/api/workers.htm'
html_payment='https://antpool.com/api/paymentHistory.htm'
html_sub_overview='https://antpool.com/api/accountOverview.htm'
html_user_hash_chart='https://antpool.com/api/userHashrateChart.htm'
def get_signature():#签名操作
	nonce=int(time.time()*1000)#毫秒时间戳
	msgs=sign_id+sign_key+str(nonce)
	ret=[]
	ret.append(hmac.new(sign_SECRET.encode(encoding="utf-8"), msg=msgs.encode(encoding="utf-8"), digestmod=hashlib.sha256).hexdigest().upper())#签名
	ret.append(nonce)#时间戳
	return ret
def get_messages(url):#POST
	api_sign=get_signature()
	# post_data = {'key': sign_key, 'nonce': api_sign[1],'signature': api_sign[0],'coin':coin_type, 'clientUserId':sign_id,'pageEnable':0}#这里是POST参数根据接口自行更改
	post_data = {'key': sign_key, 'nonce': api_sign[1],'signature': api_sign[0],'coin':coin_type, 'userId':sign_id}#这里是POST参数根据接口自行更改
	# post_data = {'key': sign_key, 'nonce': api_sign[1],'signature': api_sign[0],'coinType':coin_type, 'userId':sign_id, 'type':3}#这里是POST参数根据接口自行更改
	request = requests.post(url, data=post_data)
	return(request.text)

def main():
	print(get_messages(html_sub_overview))
main()