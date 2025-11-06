from cryptography.fernet import Fernet

async def encryptt(amount:str):
    encoded_statement = amount.encode()
    key = Fernet.generate_key()
    encryptor = Fernet(key)
    token = encryptor.encrypt(encoded_statement)

    return key, token