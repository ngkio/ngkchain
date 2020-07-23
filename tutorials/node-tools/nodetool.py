#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys
import time

args = None
logFile = None

unlockTimeout = 90

def jsonArg(a):
    return " '" + json.dumps(a) + "' "

def run(args):
    print('nodetools.py:', args)
    logFile.write(args + '\n')
    if subprocess.call(args, shell=True):
        print('nodetools.py: exiting because of error')
        sys.exit(1)

def retry(args):
    while True:
        print('nodetools.py: ', args)
        logFile.write(args + '\n')
        if subprocess.call(args, shell=True):
            print('*** Retry')
            sleep(2)
        else:
            break

def background(args):
    print('nodetools.py:', args)
    logFile.write(args + '\n')
    return subprocess.Popen(args, shell=True)

def getOutput(args):
    print('nodetools.py:', args)
    logFile.write(args + '\n')
    proc = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
    return proc.communicate()[0].decode('utf-8')

def getJsonOutput(args):
    return json.loads(getOutput(args))

def sleep(t):
    print('sleep', t, '...')
    time.sleep(t)
    print('resume')

def startWallet():
    run('rm -rf ' + os.path.abspath(args.wallet_dir))
    run('mkdir -p ' + os.path.abspath(args.wallet_dir))
    background(args.kngkd + ' --unlock-timeout %d --http-server-address 127.0.0.1:6666 --wallet-dir %s' % (unlockTimeout, os.path.abspath(args.wallet_dir)))
    sleep(.4)
    run(args.clngk + 'wallet create -f %s/default_pwd' % (os.path.abspath(args.wallet_dir)))

def importKeys():
    keys = {}
    for a in accounts:
        key = a['pvt']
        if not key in keys:
            if len(keys) >= 1000:
                break
            keys[key] = True
            run(args.clngk + 'wallet import --private-key ' + key)

def startNode(nodeIndex, account):
    dir = args.nodes_dir + account['name'] + '/'
    run('rm -rf ' + dir)
    run('mkdir -p ' + dir)
    cmd = (
            args.nodengk +
            '    --genesis-json ' + os.path.abspath(args.genesis) +
            '    --blocks-dir ' + os.path.abspath(dir) + '/blocks' +
            '    --config-dir ' + os.path.abspath(args.config_dir) +
            '    --data-dir ' + os.path.abspath(dir) +
            '    --http-server-address 0.0.0.0:' + str(8100 + nodeIndex) +
            '    --p2p-listen-endpoint 0.0.0.0:' + str(9100 + nodeIndex) +
            '    --producer-name ' + account['name'] +
            '    --private-key \'["' + account['pub'] + '","' + account['pvt'] + '"]\''
            )
    with open(dir + 'stderr', mode='w') as f:
        f.write(cmd + '\n\n')
    background(cmd + '    2>>' + dir + 'stderr')

def startProducers(b, e):
    for i in range(b, e):
        startNode(i - b + 1, accounts[i])


def stepStartWallet():
    startWallet()
    importKeys()
def stepStartProducers():
    startProducers(0, len(accounts))


# Command Line Arguments

parser = argparse.ArgumentParser()

commands = [
    ('w', 'wallet',             stepStartWallet,            True,    "Start kngkd, create wallet, fill with keys"),
    ('P', 'start-prod',         stepStartProducers,         True,    "Start producers"),
]

parser.add_argument('--clngk', metavar='', help="clngk command", default='../../build/programs/clngk/clngk --wallet-url http://127.0.0.1:6666 ')
parser.add_argument('--kngkd', metavar='', help="Path to kngkd binary", default='../../build/programs/kngkd/kngkd')
parser.add_argument('--nodengk', metavar='', help="Path to nodengk binary", default='../../build/programs/nodengk/nodengk')
parser.add_argument('--nodes-dir', metavar='', help="Path to nodes directory", default='./nodes/')
parser.add_argument('--genesis', metavar='', help="Path to genesis.json", default="./genesis.json")
parser.add_argument('--config-dir', metavar='', help="Path to config directory", default='./config/')
parser.add_argument('--wallet-dir', metavar='', help="Path to wallet directory", default='./wallet/')
parser.add_argument('--log-path', metavar='', help="Path to log file", default='./output.log')
parser.add_argument('-a', '--all', action='store_true', help="Do everything marked with (*)")
parser.add_argument('-H', '--http-port', type=int, default=8000, metavar='', help='HTTP port for clngk')

for (flag, command, function, inAll, help) in commands:
    prefix = ''
    if inAll: prefix += '*'
    if prefix: help = '(' + prefix + ') ' + help
    if flag:
        parser.add_argument('-' + flag, '--' + command, action='store_true', help=help, dest=command)
    else:
        parser.add_argument('--' + command, action='store_true', help=help, dest=command)

args = parser.parse_args()

args.clngk += ' --url http://127.0.0.1:%d ' % args.http_port

logFile = open(args.log_path, 'a')

logFile.write('\n\n' + '*' * 80 + '\n\n\n')

with open('nodetool_accounts.json') as f:
    a = json.load(f)
    accounts = a['users']

haveCommand = False
for (flag, command, function, inAll, help) in commands:
    if getattr(args, command) or inAll and args.all:
        if function:
            haveCommand = True
            function()
if not haveCommand:
    print('nodetools.py: Tell me what to do. -a does almost everything. -h shows options.')