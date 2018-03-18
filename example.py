from wosclient.wosclient import WoSClient

if __name__ == '__main__':
    # Change 'login' for your login and 'password' for your password
    with WoSClient('login', 'password') as client:
        json_object = client.search('TS=(cadmium OR lead)')
        print(json_object)
        print(json_object['records'][0])
        print(client.search('TS=(cadmium OR lead)', True).content)
