from wosclient.wosclient import WoSClient

if __name__ == '__main__':
    # Change 'login' for your login and 'password' for your password
    with WoSClient('login', 'password') as client:
        print(client.search('TS=(cadmium OR lead)', True).content)
        print(client.search('TS=(cadmium OR lead)', False))
