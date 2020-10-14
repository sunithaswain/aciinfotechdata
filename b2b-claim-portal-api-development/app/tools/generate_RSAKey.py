from Crypto.PublicKey import RSA

# Generate a public/ private key pair using 8192 bits key length (1024 bytes)
new_key = RSA.generate(8192)
print(1)
# The private key in PEM format
private_key = new_key.exportKey("PEM")
print(2)
# The public key in PEM Format
public_key = new_key.publickey().exportKey("PEM")
print(3)
fd = open("private1.pem", "wb")
fd.write(private_key)
fd.close()
print(4)
fd = open("public1.pem", "wb")
fd.write(public_key)
fd.close()
