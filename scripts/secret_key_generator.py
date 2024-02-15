import os
import binascii

""" START - This code was copied from refereced resources. Please see referenced links. 
"""

random_secret_key = binascii.hexlify(os.urandom(32)).decode()
print(random_secret_key)

# References:
# https://docs.python.org/3/library/binascii.html
# https://programtalk.com/python-examples/binascii.hexlify.decode/?ipage=2

""" END - This code was copied from refereced resources. Please see referenced links. 
"""
