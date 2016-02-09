# Copyright 2013 Google, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Contains an example of using Google Cloud Storage Signed URLs."""

import base64
import datetime
import md5
import sys
import time

import Crypto.Hash.SHA256 as SHA256
import Crypto.PublicKey.RSA as RSA
import Crypto.Signature.PKCS1_v1_5 as PKCS1_v1_5
import requests

try:
  import conf
except ImportError:
  sys.exit('Configuration module not found. You must create a conf.py file. '
           'See the example in conf.example.py.')

# The Google Cloud Storage API endpoint. You should not need to change this.
GCS_API_ENDPOINT = 'https://storage.googleapis.com'


class CloudStorageURLSigner(object):
  """Contains methods for generating signed URLs for Google Cloud Storage."""

  def __init__(self, key, client_id_email, gcs_api_endpoint, expiration=None,
               session=None):
    """Creates a CloudStorageURLSigner that can be used to access signed URLs.

    Args:
      key: A PyCrypto private key.
      client_id_email: GCS service account email.
      gcs_api_endpoint: Base URL for GCS API.
      expiration: An instance of datetime.datetime containing the time when the
                  signed URL should expire.
      session: A requests.session.Session to use for issuing requests. If not
               supplied, a new session is created.
    """
    self.key = key
    self.client_id_email = client_id_email
    self.gcs_api_endpoint = gcs_api_endpoint

    self.expiration = expiration or (datetime.datetime.now() +
                                     datetime.timedelta(days=1))
    self.expiration = int(time.mktime(self.expiration.timetuple()))

    self.session = session or requests.Session()

  def _Base64Sign(self, plaintext):
    """Signs and returns a base64-encoded SHA256 digest."""
    shahash = SHA256.new(plaintext)
    signer = PKCS1_v1_5.new(self.key)
    signature_bytes = signer.sign(shahash)
    return base64.b64encode(signature_bytes)

  def _MakeSignatureString(self, verb, path, content_md5, content_type):
    """Creates the signature string for signing according to GCS docs."""
    signature_string = ('{verb}\n'
                        '{content_md5}\n'
                        '{content_type}\n'
                        '{expiration}\n'
                        '{resource}')
    return signature_string.format(verb=verb,
                                   content_md5=content_md5,
                                   content_type=content_type,
                                   expiration=self.expiration,
                                   resource=path)

  def _MakeUrl(self, verb, path, content_type='', content_md5=''):
    """Forms and returns the full signed URL to access GCS."""
    base_url = '%s%s' % (self.gcs_api_endpoint, path)
    signature_string = self._MakeSignatureString(verb, path, content_md5,
                                                 content_type)
    signature_signed = self._Base64Sign(signature_string)
    query_params = {'GoogleAccessId': self.client_id_email,
                    'Expires': str(self.expiration),
                    'Signature': signature_signed}
    return base_url, query_params

  def Get(self, path):
    """Performs a GET request.

    Args:
      path: The relative API path to access, e.g. '/bucket/object'.

    Returns:
      An instance of requests.Response containing the HTTP response.
    """
    base_url, query_params = self._MakeUrl('GET', path)
    return self.session.get(base_url, params=query_params)

  def Put(self, path, content_type, data):
    """Performs a PUT request.

    Args:
      path: The relative API path to access, e.g. '/bucket/object'.
      content_type: The content type to assign to the upload.
      data: The file data to upload to the new file.

    Returns:
      An instance of requests.Response containing the HTTP response.
    """
    md5_digest = base64.b64encode(md5.new(data).digest())
    base_url, query_params = self._MakeUrl('PUT', path, content_type,
                                           md5_digest)
    headers = {}
    headers['Content-Type'] = content_type
    headers['Content-Length'] = str(len(data))
    headers['Content-MD5'] = md5_digest
    return self.session.put(base_url, params=query_params, headers=headers,
                            data=data)

  def Delete(self, path):
    """Performs a DELETE request.

    Args:
      path: The relative API path to access, e.g. '/bucket/object'.

    Returns:
      An instance of requests.Response containing the HTTP response.
    """
    base_url, query_params = self._MakeUrl('DELETE', path)
    return self.session.delete(base_url, params=query_params)


def ProcessResponse(r, expected_status=200):
  """Prints request and response information and checks for desired return code.

  Args:
    r: A requests.Response object.
    expected_status: The expected HTTP status code.

  Raises:
    SystemExit if the response code doesn't match expected_status.
  """
  print '--- Request ---'
  print r.request.url
  for header, value in r.request.headers.iteritems():
    print '%s: %s' % (header, value)
  print '---------------'
  print '--- Response (Status %s) ---' % r.status_code
  print r.content
  print '-----------------------------'
  print
  if r.status_code != expected_status:
    sys.exit('Exiting due to receiving %d status code when expecting %d.'
             % (r.status_code, expected_status))


def main():
  try:
    keytext = open(conf.PRIVATE_KEY_PATH, 'rb').read()
  except IOError as e:
    sys.exit('Error while reading private key: %s' % e)

  private_key = RSA.importKey(keytext)
  signer = CloudStorageURLSigner(private_key, conf.SERVICE_ACCOUNT_EMAIL,
                                 GCS_API_ENDPOINT)

  file_path = '/%s/%s' % (conf.BUCKET_NAME, conf.OBJECT_NAME)

  print 'Creating file...'
  print '================'
  r = signer.Put(file_path, 'text/plain', 'blah blah')
  ProcessResponse(r)
  print 'Retrieving file...'
  print '=================='
  r = signer.Get(file_path)
  ProcessResponse(r)
  print 'Deleting file...'
  print '================'
  r = signer.Delete(file_path)
  ProcessResponse(r, expected_status=204)
  print 'Done.'

if __name__ == '__main__':
  main()
