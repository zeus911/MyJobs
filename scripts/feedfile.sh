#!/bin/bash
# This file belongs in /home/ubuntu/. It is not part of the deployment process of this project.
# It should be set up as a cron job to run once per day. For more information about the s3cmd
# command line tool for Amazon S3, please visit: http://s3tools.org/s3cmd
date=`date "+%Y%m%d"`
file="/tmp/dseo-feeds-${date}.tar.gz"
cd /home/web/data
tar cvf - *.xml | gzip > $file
s3cmd put $file s3://feedfiles/ 2> /dev/null
rm -f $file
rm /home/web/data/*


