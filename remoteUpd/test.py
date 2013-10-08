import paramiko
import sys

port = 22
password="root"          # when production will start
patchDir="/home/carel/patch/1.0.x/"
t = paramiko.Transport((sys.argv[1], port))
t.connect(username="root", password=password)

#cleaner = t.open_channel("session")
#cmd = 'rm -rf '+ patchDir.rsplit('/',2)[0]+'/* '
#print cmd
#cleaner.exec_command(cmd)
#if cleaner.recv_exit_status() == 0:
#    print 'Process response = ' + str(cleaner.recv_exit_status())
#else:
#    print 'Cleaning Error.'
#cleaner.close()

version=patchDir+"backup"
#launch client updater
launcher = t.open_channel("session")
cmd = '(cd /home/carel/pwserver; ./cu.sh '+ version +' '+patchDir +' > /home/carel/pwserver/logUpdate )'
launcher.exec_command(cmd)
if launcher.recv_exit_status() == 0:
    print 'Process response = ' + str(launcher.recv_exit_status())
else:
    print 'Client Updater not launched. Error.'