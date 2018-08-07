#!/usr/bin/env Python

import argparse
import wget
import sys
import re
import time
from subprocess import Popen, call, check_output
import os
from os.path import expanduser

parser = argparse.ArgumentParser()

parser.add_argument(
  "version", type=str, help="EOS image version", default=None)

parser.add_argument(
  "-p", "--package", type=str, default="eos", choices=["eos", "vmdk", "veos", "ceos", "all"],
  help="specify which EOS packaging", required=False)

args = parser.parse_args()
version = args.version

images = []
urls = []
outputFilename = []

if args.package == "veos":
  images = ['vEOS-lab']
elif args.package == "ceos":
  images = ['cEOS']
elif args.package == "vmdk":
  images = ['EOS.']
elif args.package == "all":
  images = ['EOS', 'cEOS', 'vEOS-lab', 'EOS.']
else:
  images = ['EOS']

if not version:
  version = raw_input("Enter EOS Version: ").strip()

home = expanduser("~")
outputDir = home + "/Downloads/"

for image in images:
  if image == "ceos":
    ext = ".tar.xz"
  elif image == "EOS.":
    ext = "vmdk"
  else:
    ext = ".swi"
  urls.append("http://dist/release/EOS-" + version + "/final/images/" + image + ext)  
  outputFilename.append(outputDir + image + "-" + version + ext)

#print(urls)
#outputFilename = outputDir + image + "-" + version + ".swi"


vpncheckBin = check_output(["scutil", "--nc", "status", "Arista VPN"])
vpncheckStr = vpncheckBin.split("\n")
#print ("vpn check string: " + vpncheckStr[0])

if vpncheckStr[0] == "Connected":
  print("VPN Connection is up...\n")
  try:
    for url, filename in map(None, urls, outputFilename):
      # print ("URL is " + url)
      # print ("Filename is " + filename)
      file = wget.download(url, filename)
      print("\nFile downloaded to " + filename)
    failed = False
  except:
    failed = True
else:
  print("VPN Connection is down...\n")
  print("Attempting to connect to Arista VPN")
  check_output(["scutil", "--nc", "start", "Arista VPN"])
  while True:
    vpncheckBin = check_output(["scutil", "--nc", "status", "Arista VPN"])
    vpncheckStr = vpncheckBin.split("\n")
    vpncheckResult = vpncheckStr[0].strip()
    if vpncheckResult == "Connected":
      break
  #print ("Downloading EOS: " + images + " To: " + outputDir)
  try:
    for url, filename in map(None, urls, outputFilename):
      # print ("URL is " + url)
      # print ("Filename is " + filename)
      file = wget.download(url, filename)
      print("\nFile downloaded to " + filename)
    failed = False
  except:
    failed = True

if failed is False:
  for filename, urls in map(None, outputFilename, urls):
    filesize = os.stat(filename)[6]
    if filesize < 1024:
      with open(filename) as myfile:
        content = myfile.read()
      match = re.search(r'<p>(.*).</p>', content)
      reason = match.group(1)
      os.remove(filename)
      print ("\n\nThere was an error downloading: " + url + "\n")
      print ("\t" + reason + "\n")