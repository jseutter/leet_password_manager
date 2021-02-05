from ansible.constants import DEFAULT_VAULT_ID_MATCH
from ansible.parsing.vault import VaultLib, VaultSecret
from getpass import getpass
import yaml


class Secrets:
    def __init__(self, path, keyphrase):
        self.path = path
        self.keyphrase = keyphrase
        self.data = self.read()

    def read(self):
        vault = VaultLib([(DEFAULT_VAULT_ID_MATCH, VaultSecret(self.keyphrase.encode('utf-8')))])
        with open(self.path) as f:
            ciphered = f.read()
        cleartext = vault.decrypt(ciphered)
        return yaml.safe_load(cleartext)

    def write(self):
        cleartext = yaml.dump(self.data)
        vault = VaultLib([(DEFAULT_VAULT_ID_MATCH, VaultSecret(self.keyphrase.encode('utf-8')))])
        ciphered = vault.encrypt(cleartext)
        with open(self.path, 'wb') as f:
            f.write(ciphered)

    def new_vault(self):
        self.data = {'max_id': 0, 'entries': []}

    def add_entry(self, entry):
        entry['id'] = self.data['max_id'] + 1
        self.data['entries'].append(entry)
        self.data['max_id'] += 1

    def entries(self):
        return self.data['entries']


def main():
    keyphrase = getpass('Keyphrase:')
    s = Secrets('vault.yml', keyphrase)
    s.new_vault()
    s.add_entry({'title': 'wells cargo', 'username': 'unsuspecting', 'password': 'customer'})
    print(s.data)
    s.write()

if __name__ == "__main__":
    main()
