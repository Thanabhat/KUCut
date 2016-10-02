#!/usr/bin/python

import os,os.path,sys


def error(msg):
	print msg
	sys.exit(1)

def warning(msg):
	print msg,
	ans = sys.__stdin__.readline()
	return ans

def getpath(msg,default):
	print '%s \n\t(default = %s) ' % (msg,default),
	path = sys.__stdin__.readline()
	if not os.path.abspath(path):
		error('%s is not absolute path' % (path))

	path = path.strip()
	if len(path) == 0:
		path = default
		
	if not os.path.exists(path):
		ans = warning('\nThis directory does not exist, Do you want to create it [yes/no]? ')
		if ans.strip() == 'yes':
			try:
				os.makedirs(path)
			except OSError:
				print '\nAbort installation : You do not permit to create this directory'
				sys.exit(1)
		else:
			sys.exit(1)
			
	return path

def unpack(tgz_file, target_dir):
	uid = os.getuid()
	gid = os.getgid()
	options = ('-xvzk --directory="%s" --file="%s"' % (target_dir, tgz_file))
	tar_cmd = 'tar' + ' ' + options
	redirect_cmd = 'sh -c "export UMASK=0022; %s 2>&1"' % tar_cmd
	print redirect_cmd
	child_out = os.popen(redirect_cmd, 'r')
	cmd = 'chown -R %s.%s %s' % (str(uid),str(gid), target_dir)
	if os.system(cmd) != 0:
		error('Error: Failed to change file owner in installation.')
	else:
		print 'Set ownership of installation to user=%s and group=%s' % (str(uid),str(gid))
	try:
		line = child_out.readline()
		while line != '':
			if line[:len('tar:')] == 'tar:':
				fields = line.split(':')
				if len(fields) == 4 and fields[3].strip() == 'File exists':
					print 'The file "%s" already exists and won\' be overwritten' % (fields[1].strip())
			line = child_out.readline()
	except OSError:
		error('Failed to expand %s' % (tgz_file))
		

def create_execute_file(home_path,exec_file):
	exec_full = os.path.join(home_path,exec_file)
	if os.path.exists(exec_full):
		error('The file %s already exists' % (exec_full))
	fd_exec = open(exec_full,'w')
	
	fd_exec.write('#!/bin/sh\n\n'
				  'WORDCUT_HOME=%s\n'
				  'export WORDCUT_HOME\n\n'
				  'python $WORDCUT_HOME/kucut.py "$@"' % (home_path))
	
	cmd = 'chmod 755 %s' % (exec_full)

	if os.system(cmd) != 0:
		error('Error: Failed to change file mode in installation.')
	else:
		print 'Set mode of file %s to 755' % (exec_full)
		
	fd_exec.close()
				  
def create_link_file(home_path,exec_file,bin_path):
	exec_full = os.path.join(home_path,exec_file)
	if not os.path.exists(exec_full):
		error('Not found the file %s' % (exec_full))
		
	bin_full = os.path.join(bin_path,exec_file)
	if os.path.exists(bin_full):
		error('The file %s already exists' % (bin_full))

	cmd = 'ln -s %s %s' % (os.path.join(home_path,exec_file), os.path.join(bin_path,exec_file))
	if os.system(cmd) != 0:
		error('Error: Failed to create link to execute file')
	else:
		print '\nCreate link to execute file %s' % (exec_file)
	
inst_path = getpath('Where do you want to install the support files for KU Wordcut?','/usr/local/lib/kucut-1.0')
unpack('kucut.tar.gz',inst_path)
create_execute_file(inst_path,'kucut')
bin_path = getpath('Where do you want to install execute file for KU Wordcut?','/usr/local/bin')
create_link_file(inst_path,'kucut',bin_path)

print 'Installation success.'
