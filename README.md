# Google Cloud Storage Signed URLs Example

This script is an example of using a service account's private key to create
signatures required for clients to access Google Cloud Storage using [signed URL
authentication](https://developers.google.com/storage/docs/accesscontrol#Signed-URLs).

## Required Dependencies

The following third-party Python modules are required:

 * [requests](http://docs.python-requests.org/en/latest/)
 * [PyCrypto](https://www.dlitz.net/software/pycrypto/)

The easiest way to install the dependencies is to run:

    pip install -r requirements.txt

## Configuration

The `conf.example.py` file must be copied to `conf.py` and the variables in the
file must be filled in. See the example file for explanation of each variable.

## Example Flow

The example script's flow is as follows:

  * Generates a signature for a PUT request and uses it to upload a new file.
  * Generates a signature for a GET request and uses it to download the new
    file that was just uploaded.
  * Generates a signature for a DELETE request and uses it to delete the file
    that was created.
