def load_secret_clientId():
    with open('secret.txt', 'r') as fp:
        secret = fp.readline().split('\n')[0]
        client_id = fp.readline()
        return (secret, client_id)
