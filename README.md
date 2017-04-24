# Glacier Manager

A very basic Archive manager for AWS's Glacier service. At the moment it can only initialise a job and download a job.

Please note that this project is in it's infancy and still pretty flakey! Use at own risk. Pull requests welcome.

## Requirements

- Python 3 (should work with Python 2 but totally untested)
- [boto3](https://boto3.readthedocs.io/en/latest/)
- [click](http://click.pocoo.org)

## Installation:

Clone repository and change directory:

`$ git clone git@github.com:hammygoonan/glacier_manager.git glacier_manager && cd glacier_manager`

Create `.env` file:

`$ cp env.default .env`

Edit `.env` file and add your credentials

Set environment variables:

`$ source .env`

## Usage

Set environment variables (if you haven't already):

`$ source .env`

To initialise a job (Download only at this stage):

`$ ./glacier.py init_job`

To download an archive:

`$ ./glacier.py download`

To upload an archive (<small>**Please note this is currently totally untested.**</small>:)

`$ ./glacier.py upload`
