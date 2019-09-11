
import boto3
import sys
import logging

from cStringIO import StringIO


logger = logging.getLogger()
logger.setLevel(logging.WARNING)
mystdout = StringIO()



def get_tag_value(instance_id, tag, region):
    ec2 = boto3.resource('ec2', region)
    ec2_instance = ec2.Instance(instance_id)
    noname = "NO-NAME"

    try:
        for tags in ec2_instance.tags:
            if tag == tags['Key']:
                name=tags['Value']
                if name != " " and name != "":
                    return name
                else:
                    return noname

    except Exception as e:
        print e
        ret = "NO-NAME"

    return ret


def generate_report():
    from datetime import datetime

    ec2 = boto3.client('ec2', region_name='us-west-1')
    regions = ec2.describe_regions()

    date_format = "%Y-%m-%dT%H:%M:%S"
    header = "<!DOCTYPE html>\n<html>\n<body>"
    footer = "</body>\n</html>"
    begintable = "\n<table border=\"1\" style=\"border: 1px solid #e3e3e3;background-color:#f2f2f2;width:100%;border-radius:6px;-webkit-border-radius:6px;-moz-border-radius:6px;\">"
    tablehead =  "<thead><th>Region</th><th>Name</th><th>ID</th><th>Instance Type</th><th>Uptime</th>"
    endtable = "</table>"
    space = "<br>"
    response = ""
    mystdout.write('\n')

    print >>mystdout, header
    print >>mystdout, begintable
    print >>mystdout, tablehead

    ec2 = boto3.client('ec2', region_name='us-west-1')

    tags = []
    instance_name_value = ""
    for region in regions['Regions']:
        rname = region['RegionName']
        client = boto3.client('ec2', region_name=rname)
        running_instances = client.describe_instances(
            Filters=[
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
            ])
        for reservation in running_instances['Reservations']:
            for instance in reservation['Instances']:
                instance_type=instance['InstanceType']
                launch=instance['LaunchTime']
                instance_id=instance['InstanceId']

                instance_name_value = get_tag_value(instance_id, 'Name', region['RegionName'])

                start = str(launch)
                from datetime import datetime
                now = datetime.utcnow()
                # format time:
                date_format = "%Y-%m-%dT%H:%M:%S"
                now_formatted = datetime.strftime(now, date_format)
                now_string = str(now_formatted)
                now_strip = datetime.strptime(now_string, date_format)
                launch_time_formatted = datetime.strftime(launch, date_format)
                launch_time_string = str(launch_time_formatted)
                launch_time_strip = datetime.strptime(launch_time_string, date_format)
                ## calculation:
                uptime = (now_strip - launch_time_strip)

                output_one = "<tr><td style=\"line-height:20px;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:14px;border-bottom:1px solid #fff;border-top:1px solid #fff;\">%s</td><td style=\"line-height:20px;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:14px;border-bottom:1px solid #fff;border-top:1px solid #fff;\">%s</td><td style=\"line-height:20px;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:14px;border-bottom:1px solid #fff;border-top:1px solid #fff;\">%s</td><td style=\"line-height:20px;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:14px;border-bottom:1px solid #fff;border-top:1px solid #fff;\">%s</td><td style=\"line-height:20px;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:14px;border-bottom:1px solid #fff;border-top:1px solid #fff;\">%s</td></tr>" % (rname, instance_name_value, instance_id, instance_type, uptime)

            print >>mystdout, output_one


    print >>mystdout, endtable
    print >>mystdout, space


    # RDS Report
    print >>mystdout, begintable
    print >>mystdout, tablehead

    ec2 = boto3.client('rds', region_name='us-west-2')

    for region in regions['Regions']:
        rname = region['RegionName']
        if rname not in [ 'cn-north-1', 'us-gov-west-1' ]:
            client = boto3.client('rds', region_name=rname)
            instances = client.describe_db_instances()

            for instance in instances['DBInstances']:

                engine = instance['Engine']
                address = instance['Endpoint']['Address']
                instance_type = instance['DBInstanceClass']
                instance_id = instance['DBInstanceIdentifier']

                # format time:
                date_format = "%Y-%m-%dT%H:%M:%S"
                now = datetime.utcnow()
                now_formatted = datetime.strftime(now, date_format)
                now_string = str(now_formatted)
                now_strip = datetime.strptime(now_string, date_format)

                # Create time:
                launch_time = instance['InstanceCreateTime']
                launch_time_formatted = datetime.strftime(launch_time, date_format)
                launch_time_strip = datetime.strptime(launch_time_formatted, date_format)

                # Calculation:
                uptime = (now_strip - launch_time_strip)

                output_two = "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (rname, instance_id, address, instance_type, uptime)

                print >>mystdout, output_two


    body = mystdout.getvalue()

    # Sending email
    client = boto3.client('ses', region_name='us-west-2')
    fromaddr = "<from-email-to-email>"
    response = client.send_email(
        Source='<from-email-to-email>',
        Destination={
            'ToAddresses': [
                '<recipient1>',
            ],
            'CcAddresses': [
                '<recipient2>'
            ]
        },
        Message={
            'Subject': {
                'Data': 'AWS Uptime Report - Lambda',
                'Charset': 'utf-8'
            },
            'Body': {
                'Text': {
                    'Data': body,
                    'Charset': 'utf-8'
                },
                'Html': {
                    'Data': body,
                    'Charset': 'utf-8'
                }
            }
        },
        ReplyToAddresses=[
            fromaddr,
        ],
        ReturnPath='<from-email-to-email>',
    )
    print response['MessageId']

def lambda_send_email(event, context):
    try:
        generate_report()

    except Exception, e:
        raise
