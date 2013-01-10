import os.path

# The email address for your GCS service account being used for signatures.
SERVICE_ACCOUNT_EMAIL = ('abcdef1234567890@developer.gserviceaccount.com')

# Bucket name to use for writing example file.
BUCKET_NAME = 'bucket-name'
# Object name to use for writing example file.
OBJECT_NAME = 'object.txt'

# Set this to the path of your service account private key file, in DER format.
#
# Given a GCS key in pkcs12 format, convert it to PEM using this command:
#   openssl pkcs12 -in path/to/key.p12 -nodes -nocerts > path/to/key.pem
# Given a GCS key in PEM format, convert it to DER format using this command:
#   openssl rsa -in privatekey.pem -inform PEM -out privatekey.der -outform DER
PRIVATE_KEY_PATH = os.path.join(os.path.dirname(__file__), 'privatekey.der')
