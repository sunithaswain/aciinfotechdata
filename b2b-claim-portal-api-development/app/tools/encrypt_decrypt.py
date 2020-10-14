from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64


def encrypt(input_str):
    # Use the public key for encryption
    with open("public.pem", "rb") as fd:
        public_key = fd.read()

    rsa_key = RSA.importKey(public_key)
    rsa_key = PKCS1_OAEP.new(rsa_key)
    print(input_str)
    input_str = str.encode(input_str)
    encrypted = rsa_key.encrypt(input_str)

    return base64.b64encode(encrypted)


def decrypt(encrypted_str):
    # Use the private key for encryption
    with open("private.pem", "rb") as fd:
        private_key = fd.read()

    rsa_key = RSA.importKey(private_key)
    rsa_key = PKCS1_OAEP.new(rsa_key)

    # Base 64 decode the data
    encrypted_str = base64.b64decode(encrypted_str)
    return rsa_key.decrypt(encrypted_str)


encrypted_str = "iFJrhtud7pZm1RAavyp3zCxsx05MbmDeTMFjWtZIfbX57FQAtgPOiu9tiuHNaaWeni+khGumfQWGiyQir4z9uDET5LKPc3SEcopuCBPV37NHpVl6DAVoDXMpcMpiLiBVgEvNYdA38Mt929htbvDfsfwShaibung9GrZyJSNpD1Oy6uQ53A0DAO45f4AtBIqySxv0j3pameBcG3jXVbPGMKRiktmxdx1hcPuyYw61bar/H6jkcYTDtCDzFrS1QcvrU2336pzI8mKjbA+SYKcXONzd6RYrSc9pNj00vEa/OS8OozbD2nTsfGT08jso9rhvErwtZuI2y2I2WuJECGSgj3nnenq2f3/idd9cZmYYhYT5P62c+MpRtlyGTB5h6OjHmvzgtux0Ko8D13MqI3IsQ79nlh51RbtiTsx2o8OLDKrmTO7ZT4y9spNV6QlFdSfXCfUbg3cFEltobmTWbFxnVjt4W4U3TTKxzog1hK7XajaPx4X4uDUnWNcl3ozSUzviVaqONB04PwizUKc320thHOtWIfFn/oUjKCuV6HzncQ6xYDrRQnL2tgarauHqqUyXO2I2/vfwwSrNGD4zhgS4P9YxAOWrdz3lq7M6ul3TNaw2wuEkuWOJi1Wq0Yisqyufw//VKIz8/pktmytkwVe1aKpjwGCAcIeApclbGQ74wBk="


if __name__ == "__main__":
    #encryptedString = encrypt("D08pzWmXY630")
    print(encrypted_str)
    decryptedString = decrypt(encrypted_str)
    # print(encryptedString)
    print(decryptedString)
