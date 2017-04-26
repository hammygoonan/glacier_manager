#!/usr/bin/env python3
"""
    glacier
    ~~~~~~~

    A Command Line Interface for intialising Glacier jobs and downloading output.
"""

import json
import os
import uuid
import click
import boto3
import pprint


AWS_ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
GLACIER_VAULT = os.getenv('GLACIER_VAULT')
AWS_REGION = os.getenv('AWS_REGION')


def get_client():
    """Return boto3 Glacier client."""
    return boto3.client(
        'glacier', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )


@click.group()
def glacier():
    pass


@glacier.command()
@click.option('--description', prompt='Description', help="It is recommended you use the filename")
@click.option('--filename', prompt='Filename', help="Filename with full path")
def upload(description, filename):
    """Upload new achieves.

    WARNING: Totally untested.
    """
    if(os.path.isfile(filename) is False):
        click.echo("Can't find the file to upload!")
        raise click.Abort

    client = get_client()
    chunk_size = 1048575
    file_size = os.path.getsize(filename)
    position = 0
    upload_id = uuid.uuid4()
    with open(filename, 'rb') as f:
        for data in f.read(chunk_size):
            start = position
            end = position + chunk_size
            if end > file_size:
                end = file_size
            response = client.upload_multipart_part(
                body=data,
                vaultName=GLACIER_VAULT,
                uploadId=upload_id,
                range='bytes {}-{}/*'.format(start, end),
            )
            pprint.pprint(response)


@glacier.command()
@click.option('--archive_id', prompt='Archive ID')
def archive_retrieval(archive_id):
    """Initialise the retreval of an archive."""
    client = get_client()
    response = client.initiate_job(
        vaultName=GLACIER_VAULT,
        jobParameters={
            'Type': 'archive-retrieval',
            'ArchiveId': archive_id
        }
    )
    click.echo('Your job is being retreved.')
    click.echo('Job Id: ' + response['jobId'])


@glacier.command()
def inventory_retrieval():
    """Initialise the retreval of an inventory."""
    client = get_client()
    response = client.initiate_job(
        vaultName=GLACIER_VAULT,
        jobParameters={
            'Type': 'inventory-retrieval'
        }
    )
    click.echo('Your job is being retreved.')
    click.echo('Job Id: ' + response['jobId'])


@glacier.command()
@click.option('--job_id', prompt='Job ID')
def download(job_id):
    """Download output of job.

    Assumes that the job description is the filename.
    """
    client = get_client()
    job_description = client.describe_job(
        vaultName=GLACIER_VAULT,
        jobId=job_id
    )
    if job_description['StatusCode'] == 'Succeeded':
        job_output = client.get_job_output(
            vaultName=GLACIER_VAULT,
            jobId=job_id
        )
        chunk_size = 1048575  # bytes
        total = int(job_description['ArchiveSizeInBytes'])
        position = 0
        end = 0

        click.echo(
            'Starting Download - {} ({} bytes)'.format(job_output['archiveDescription'], total)
        )
        with click.progressbar(length=total, label="Progress") as bar:
            with open(job_output['archiveDescription'], 'wb') as f:
                while end != total:
                    start = position
                    end = position + chunk_size
                    if end > total:
                        end = total
                    position = end + 1
                    output = client.get_job_output(
                        vaultName=GLACIER_VAULT, jobId=job_id, range='bytes={}-{}'.format(start, end)
                    )
                    f.write(output['body'].read())
                    bar.update(position)
        click.echo('Finshed Downloading')
    else:
        click.echo('Status: ' + job_description['StatusCode'])
        pprint.pprint(job_description)


@glacier.command()
@click.option('--job_id', prompt='Job ID')
def get_inventory(job_id):
    """Download inventory output."""
    client = get_client()
    job_description = client.describe_job(
        vaultName=GLACIER_VAULT,
        jobId=job_id
    )
    if job_description['StatusCode'] == 'Succeeded':
        click.echo('Retrieving Inventory')
        with open('inventory.txt', 'w') as f:
            output = client.get_job_output(
                vaultName=GLACIER_VAULT, jobId=job_id
            )
            json_output = json.loads(output['body'].read().decode('utf-8'))
            pprint.pprint(json_output, f)
        click.echo('Finshed')
    else:
        click.echo('Status: ' + job_description['StatusCode'])
        pprint.pprint(job_description)


if __name__ == '__main__':
    glacier()
