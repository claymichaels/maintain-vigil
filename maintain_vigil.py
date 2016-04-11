#!/usr/bin/python

# Clay Michaels
# Feb-2015
# maintain_vigil
version = '1.0'
# Checks periodically for a vehicle to come online, then runs a command.
# Command output will be sent to the specified email address.
# 
# Interval defaults to 15 minutes between pings if no interval is provided.
# Target could be a host from the etc/hosts file ( apple.362 ) or an IP address.


import os
import time
from sys import exit, argv
import smtplib
import logging
from logging.handlers import RotatingFileHandler


# Set up logging
LOG_FILE = argv[0][:-3] + '.log'
logging.basicConfig(
    filename=LOG_FILE,
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
handler = RotatingFileHandler(LOG_FILE, maxBytes=1000000)
logger.addHandler(handler)


def send_email(msg1, msg2, target, whom_to_notify):
    text = 'Command:\n%s\nResponse:\n%s' % (msg1, msg2)
    subject = 'AUTOMAIL: %s came online!' % target
    fromaddr = 'clay.nomad@gmail.com'
    toaddr = [whom_to_notify, ]
    username = 'clay.nomad'
    password = 'nomad123'
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (fromaddr, ", ".join(toaddr), subject, text)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.sendmail(fromaddr, toaddr, message)
        server.close()
        logger.info('Successfully sent the mail for %s' % target)
        exit()
    except smtplib.SMTPException:
        logger.error('Failed to send mail for %s' % target)
        exit()


def check_if_online(target):
    result = os.popen('ping -i 0.5 -c 2 %s' % target).read()
    if 'icmp_seq' in result:
        logger.info('%s is online!' % target)
        return True
    else:
        logger.info('%s is still offline.', target)
        return False


def get_args(arg_list):
    if len(arg_list) not in [4, 5]:
        print('USAGE:')
        print('python %s <Target> <Command> <Whom to email> [Wait]' % arg_list[0])
        print('<Target> could be a host from the etc/hosts file ( apple.362 ) or an IP address.')
        print('<Command> is anything you would enter on the command line, surrounded by double quotes.')
        print('\tE.x.: \"ssh -q apple.362 \'cat /var/local/unified/05/iccid\'\"')
        print('\tor \"rsync -aP ~/scripts/PROJECT.conf /conf/PROJECT.conf\"')
        print('<Whom to email> An email address to notify that the task has been done.')
        print('\tThe output of the command (if any) is also sent.')
        print('[Wait] is the optional time in minutes between checks. Defaults to 15')
        print('\nCopy and paste the next line into your terminal to see other maintained vigils.')
        print('ps -e -o pid,args | grep next_time_online | grep python')
        print('\nNote that appending "&" to the end of the line will put the script into the background.')
        print('\tE.x.: python %s apple.371 "cat /conf/ME.conf" naservicedesk@nomadrail.com 30 &' % arg_list[0])

        exit()
    else:
        target_in = arg_list[1]
        command_in = arg_list[2]
        notify_address_in = arg_list[3]
        if len(arg_list) is 4:
            wait_in = 15
        else:
            wait_in = int(arg_list[4])
        return target_in, command_in, notify_address_in, wait_in


def main():
    target, command, notify_address, wait = get_args(argv)
    logger.info('Checking status of %s every %d minutes.' % (target, wait))
    logger.info('Running %s and sending output to %s when online.' % (command, notify_address))
    while not check_if_online(target):
        time.sleep(wait * 60.0)
    else:
        logger.info('Issuing command %s to %s.' % (command, target))
        command_response = os.popen(command).read()
        logger.info('Command response from %s is %s.' % (target, command_response))
        logger.info('Sending email with response from %s.' % target)
        send_email(command, command_response, target, notify_address)
        exit()


main()
