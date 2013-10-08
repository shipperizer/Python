#!/usr/bin/env python

# Copyright (C) 2003-2007  Robey Pointer <robeypointer@gmail.com>
#
# This file is part of paramiko.
#
# Paramiko is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paramiko is distrubuted in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Paramiko; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.

# based on code provided by raymond mosteller (thanks!)

import base64
import getpass
import os
import socket
import sys
import traceback
import time
import zipfile
import tarfile
import platform

import paramiko
import pwMaster

def validation(filename):
    maxPatchSize=50
    if zipfile.is_zipfile(filename)==False and tarfile.is_tarfile(filename)==False:
	print 'Not valid archive file, Not a valid patch file.'
	return False
    if os.path.getsize(filename) > maxPatchSize*1024*1024:  # maxPatchSize in MB
	print 'Maximum size exceeded, Not a valid patch file.'
	return False
    with open("versionPw") as f:
	ver= f.readline() + "".rstrip()
	if platform.system()=='Windows':
	    patchName=filename.rsplit("\\",1)[1]+""           #Windows path
	else:
	    patchName=filename.rsplit("/",1)[1]+""            #Linux path
	if patchName.find(ver.replace(".","").rstrip())!=1 :
	    print "Version error, Not a valid patch file."
	    return False
    return True



# setup logging
paramiko.util.log_to_file('patcher.log')

# connect and use paramiko Transport to negotiate SSH2 across the connection
try:
    remotePwVer="/home/carel/app/conf/version/ver"
    patchDir="/home/carel/patch/1.0.x/"
    port = 22
    if len(sys.argv) > 3:
        password=pwMaster.getPW(sys.argv[3])
    else :                       # to be deleted
        password="root"          # when production will start
    
    t = paramiko.Transport((sys.argv[2], port))
    t.connect(username="root", password=password)
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.get(remotePwVer, "versionPw")
        
    if validation(sys.argv[1])==False:
	raise Exception
    #clean dir
    cleaner = t.open_channel("session")
    cmd = 'rm -rf '+ patchDir.rsplit('/',2)[0]+'/* '
    print cmd
    cleaner.exec_command(cmd)
    if cleaner.recv_exit_status() == 0:
	print 'Process response = ' + str(cleaner.recv_exit_status())
    else:
	print 'Cleaning Error.'
    cleaner.close()	
    #create dir into pw
    try:
        sftp.chdir(patchDir)
	print '(assuming patch directory already exists)'
    except IOError:
        sftp.mkdir(patchDir)
	print 'created /home/carel/patch/1.0.x on the server'

    #copy of patch into the pw
    tmp=""+sys.argv[1]
    print "Patch file " + tmp
    
    if platform.system()=='Windows':
	print 'Windows'
	if tmp.find('/') != -1:					  				  #Windows path
	    tmp=tmp.replace('/', os.sep)								  #Windows path
	sftp.put( tmp, patchDir + tmp.rsplit("\\" ,1)[1])	  	  				           #Windows path
	sftp.put( tmp.replace(os.sep+tmp.rsplit( os.sep,1)[1], "")+ os.sep +'versions', patchDir+'/versions')	   #Windows path
	sftp.put( tmp.replace(os.sep+tmp.rsplit(os.sep,1)[1], "")+ os.sep +'spversion', patchDir+'/spversion')	   #Windows path
    else:
	print 'Linux'
	print  patchDir + tmp.rsplit("/",1)[1] 
	sftp.put( tmp, patchDir + tmp.rsplit("/",1)[1] )   		  		  #Linux path
	sftp.put( tmp.rpartition("/")[0]+'/versions', patchDir+'/versions')	  	  #Linux path
	sftp.put( tmp.rpartition("/")[0]+'/spversion', patchDir+'/spversion')	  	  #Linux path

    #c:\python27\python.exe sftp_updater.py full\path\to.zip ip mac
    
    
    version=patchDir                          #same path as patchDir 'cause backup session needs this parameter, exes script will add "backup" on trail to perform the rescue
    #launch client updater
    launcher = t.open_channel("session")
    cmd = '(cd /home/carel/pwserver; ./cu.sh '+ version +' '+patchDir +' >> /home/carel/pwserver/logUpdate 2>&1 )'
    launcher.exec_command(cmd)
    if launcher.recv_exit_status() == 0:
	print 'Process response = ' + str(launcher.recv_exit_status())
    else:
	print 'Client Updater not launched. Error.'
    t.close()

except Exception, e:
    print '*** Caught exception: %s: %s' % (e.__class__, e)
    traceback.print_exc()
    try:
        t.close()
    except:
        pass
    sys.exit(1)

