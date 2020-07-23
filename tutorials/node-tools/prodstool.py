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
    print('prodstool.py:', args)
    logFile.write(args + '\n')
    if subprocess.call(args, shell=True):
        print('prodstool.py: exiting because of error')
        sys.exit(1)

def retry(args):
    while True:
        print('prodstool.py: ', args)
        logFile.write(args + '\n')
        if subprocess.call(args, shell=True):
            print('*** Retry')
            sleep(2)
        else:
            break

def background(args):
    print('prodstool.py:', args)
    logFile.write(args + '\n')
    return subprocess.Popen(args, shell=True)

def getOutput(args):
    print('prodstool.py:', args)
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

def vote(a, b, e):
    voter = accounts[a]['name']
    prods = ' '.join(map(lambda x: accounts[x]['name'], range(b, e)))
    retry(args.clngk + 'system voteproducer prods ' + voter + ' ' + prods)

def proxyVotes():
    vote(firstProducer + 1, firstNewProducer + 3, len(accounts))
    proxy = accounts[firstProducer + 1]['name']
    retry(args.clngk + 'system regproxy ' + proxy)
    sleep(1.0)
    for i in range(0, firstProducer):
        voter = accounts[i]['name']
        retry(args.clngk + 'system voteproducer proxy ' + voter + ' ' + proxy)

def regProducer():
    for i in range(firstNewProducer, len(accounts)):
        a = accounts[i]
        retry(args.clngk + 'system regproducer ' + a['name'] + ' ' + a['pub'] + ' https://')

def listProducers():
    run(args.clngk + 'system listproducers')

def stepStartWallet():
    startWallet()
    importKeys()
def stepRegProducers():
    regProducer()
    sleep(1)
def stepProxyVotes():
    proxyVotes()
    vote(firstProducer, firstProducer, firstNewProducer + 3)
    listProducers()
def stepSetSystemContract():
    # install ngk.system latest version
    retry(args.clngk + 'set abi ngk ' + args.contracts_dir + '/ngk.system/ngk.system.abi -x 90')
    retry(args.clngk + 'set code ngk ' + args.contracts_dir + '/ngk.system/ngk.system.wasm -x 90')
    sleep(30)

# Command Line Arguments

parser = argparse.ArgumentParser()

commands = [
    ('w', 'wallet',             stepStartWallet,            True,    "Start kngkd, create wallet, fill with keys"),
    ('p', 'reg-prod',           stepRegProducers,           True,    "Register producers"),
    ('x', 'proxy',              stepProxyVotes,             True,    "Proxy votes"),
    ('S', 'sys-contract',       stepSetSystemContract,      True,    "Set system contract")
]

parser.add_argument('--clngk', metavar='', help="clngk command", default='../../build/programs/clngk/clngk --wallet-url http://127.0.0.1:6666 ')
parser.add_argument('--kngkd', metavar='', help="Path to kngkd binary", default='../../build/programs/kngkd/kngkd')
parser.add_argument('--contracts-dir', metavar='', help="Path to latest contracts directory", default='../../build/contracts/')
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

with open('prodstool_accounts.json') as f:
    a = json.load(f)

    firstProducer = len(a['users'])
    firstNewProducer = firstProducer + len(a['producers'])
    # numProducers = len(a['producers'])
    accounts = a['users'] + a['producers'] + a["newproducers"]

haveCommand = False
for (flag, command, function, inAll, help) in commands:
    if getattr(args, command) or inAll and args.all:
        if function:
            haveCommand = True
            function()
if not haveCommand:
    print('prodstool.py: Tell me what to do. -a does almost everything. -h shows options.')