from java.util import Properties
from java.io import FileInputStream
import java.io.File
import java.io.FileWriter
import java.io.IOException
import java.io.Writer
import os
import sys
import socket
props = Properties()
# Load properties
def intialize():
	global props
	
	if len(sys.argv) != 2:
		print 'Usage:  domain.py  <property_file>';
		exit();
	try:
		props = Properties()
		input = FileInputStream(sys.argv[1])
		props.load(input)
		input.close()
	except:

		print 'Cannot load properties  !';
		exit();
	
	print 'initialization completed';

def writeFile(directory_name, file_name, content):
	dedirectory = java.io.File(directory_name);
	defile = java.io.File(directory_name + '/' + file_name);
        writer = None;
        try:
                dedirectory.mkdirs();
                defile.createNewFile();
                writer = java.io.FileWriter(defile);
                writer.write(content);
        finally:
                print "start writing"

        try:
                print 'writing file ' + file_name;
                if writer != None:
                        writer.flush();
                        writer.close();
        except java.io.IOException, e:
                e.printStackTrace();

def pathExists(path):
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
                os.makedirs(dir)

def createbootprops(domain_configuration_home,admin_server_name,admin_username,admin_password):
	print 'boot.propties file'
	dirname=domain_configuration_home + '/servers/'+ admin_server_name +'/security';
	content = 'username=' + admin_username + '\npassword=' + admin_password;
	pathExists(dirname);
	writeFile(dirname, 'boot.properties', content);

def startserver(name, scipt,waitTime):
	try:
		
		startCommand = 'nohup '+scipt+' > '+name+'.log 2>&1 &'
		print ('The following start command will be used: '+startCommand)
		os.system(startCommand)
		os.system("sleep 3")
		java.lang.Thread.sleep(waitTime)
	except OSError:
		print "Exception while starting the "+name+" !"
	dumpStack()


def createManagedServer(usr,pswd, aurl, name, port, machine):
	print "create managed server"
	connnectToAdminServer(usr, pswd, aurl)
	#connect(usr, pswd, aurl)
	edit()
	startEdit()
	cd('/')
	cmo.createServer(name)	
	cd('/Servers/' + name)
	cmo.setListenAddress("")	
	cmo.setListenPort(int(port))
	activate()
	startEdit()
	cmo.setListenPortEnabled(true)
	cmo.setJavaCompiler('javac')
	cmo.setClientCertProxyEnabled(false)
	cmo.setMachine(getMBean('/Machines/' + machine))
	cmo.setCluster(None)
	#cd('/Servers/' + name + '/SSL/' + name)
	#cmo.setEnabled(false)
	#cd('/Servers/NewManagedServer/DataSource/NewManagedServer')
	#cmo.setRmiJDBCSecurity(None)
	activate()
	
	print "Managed server \""+ name + "\" created"

def connnectToAdminServer(usr,pswd,adminURL):
	
	currentcount = 0;
	adminServerIsRunning = 'false';
	while ((adminServerIsRunning=='false')  and (currentcount<30)):
		try:
			print 'Connecting to the Admin Server ('+adminURL+')';
			connect(usr,pswd,adminURL);
			print 'Connected';
                        adminServerIsRunning = 'true';
		except:
			print 'AdminServer is (not yet) running. Will wait for 30 sec.';
			java.lang.Thread.sleep(30000);
			currentcount = currentcount +1;
		if (adminServerIsRunning=='false'):
			print 'Could not connect to admin server - script will be exit !'
			exit();
def createdomain():
	global props
	weblogicHome=props.getProperty("WEBLOGIC_HOME")
	domName=props.getProperty("DOMAIN_NAME")
	javaHome=props.getProperty("JAVA_HOME")						
	nodemanagerHome=props.getProperty("NODEMANAGER_HOME")
	nodemanagerPassword=props.getProperty("NODEMANAGER_ADDRESS")
	nodemmanagerUsername=props.getProperty("NODEMANAGER_USERNAME")
	props.getProperty("NODEMANAGER_PASSWORD")
	adminServerUsername=props.getProperty("ADMIN_USERNAME")
	adminServerPassword=props.getProperty("ADMIN_PASSWORD")
	domainConfigurationHome=props.getProperty("DOMAIN_CONFIGURATION_HOME")
	props.getProperty("WEBLOGIC_HOME")
	domainAppsHome=props.getProperty("DOMAIN_APPLICATIONS_HOME")
	adminServerName=props.getProperty("ADMIN_SERVER_NAME")
	adminServerPort=props.getProperty("ADMIN_SERVER_PORT")
	adminServerPortSsl=props.getProperty("ADMIN_SERVER_PORT_SSL")
	adminServerAddress=props.getProperty("ADMIN_SERVER_ADDRESS")
	envType=props.getProperty("ENV_TYPE")
	#Managed Servers
	machine=props.getProperty("MACHINE")
	managedServer=props.getProperty("MANAGED_SERVER")
	managedServerPort=props.getProperty("MANAGED_SERVER_PORT")
	jvmPam=props.getProperty("JVM_PARAM")
	monitorUser=props.getProperty("MONITOR_USER")
	monitorPass =props.getProperty("MONITOR_PASSWORD")
	monitorGroup =props.getProperty("MONITOR_GROUP")
	domainConfiguration=domainConfigurationHome +"/"+domName
	pathExists(domainConfiguration)
	pathExists(domainAppsHome)
	print 'Create template Paths'
	weblogicTemplate=weblogicHome+ '/common/templates/wls/wls.jar'
	readTemplate(weblogicTemplate)
	setOption('DomainName', domainConfiguration);
	#setOption('OverwriteDomain', 'true');
	#setOption('JavaHome', javaHome);
	setOption('ServerStartMode', envType);
	#setOption('NodeManagerType', 'CustomLocationNodeManager');
	#setOption('NodeManagerHome', nodemanagerHome);
	setOption('AppDir', domainAppsHome);
	cd('Servers/AdminServer')
	set('ListenAddress','')
	set('ListenPort',int(adminServerPort))
	create('AdminServer','SSL')
	cd('SSL/AdminServer')
	set('Enabled', 'True')
	set('ListenPort', int(adminServerPortSsl))
	cd('/Servers/AdminServer/SSL/AdminServer')
	cmo.setHostnameVerificationIgnored(true)
	cmo.setHostnameVerifier(None)
	cmo.setTwoWaySSLEnabled(false)
	cmo.setClientCertificateEnforced(false)
	cd('/')
	cd('Security/base_domain/User/'+adminServerUsername)
	cmo.setPassword(adminServerPassword)	
	setOption('OverwriteDomain', 'true')
	cd('/')
	cd('NMProperties')
	set('ListenAddress',adminServerAddress)
	writeDomain(domainConfiguration)
	closeTemplate()
	print domName +" Domain created"
	createbootprops(domainConfiguration,adminServerName,adminServerUsername,adminServerPassword);
	print "Start Nodemanager"
	startserver("NodeManager", domainConfiguration+"/bin/startNodeManager.sh",6000)
	print "Nodemanager started"
	print "Start admin  server"
	aurl="t3://"+adminServerAddress+":"+adminServerPort
	#startserver("AdminServer", domain_configuration+"/startWebLogic.sh",100000)
	#startNodeManager(verbose='false', NodeManagerHome=nodemanagerHome, ListenPort='5556')
	startServer(adminServerName,domName,aurl,adminServerUsername,adminServerPassword,domainConfiguration,'false', 240000, jvmArgs=jvmPam)
	#os.system("sleep 30")
	java.lang.Thread.sleep(120000);
	print "Admin Server started"
	java.lang.Thread.sleep(120000);	
	#print "connect param username "+ adminServerUsername+" pasword " + " url "+aurl	
	createManagedServer(adminServerUsername,adminServerPassword, aurl, managedServer, managedServerPort, machine)
	java.lang.Thread.sleep(120000);
	print "Add  Monitoring user"	
	addUser(adminServerUsername,adminServerPassword,aurl,monitorUser,monitorPass,monitorGroup)
	print "Add monitoring user"

def addUser(wusername,wpassword,aurl,basename,pw,group):
	connect(wusername, wpassword, aurl);
	
	try:
				
		atnr=cmo.getSecurityConfiguration().getDefaultRealm().lookupAuthenticationProvider('DefaultAuthenticator')
		atnr.createUser(basename,pw,'')
		atnr.addMemberToGroup( group, basename)
			
	except:
		print"Error::", sys.exc_info()[0]
		objs = jarray.array([], java.lang.Object)
		strs = jarray.array([], java.lang.String)
	raise

	disconnect()

#           Main Code Execution
# ================================================================
if __name__== "main":
	
	print ' Start domain creation \n';
	intialize()
	createdomain()

