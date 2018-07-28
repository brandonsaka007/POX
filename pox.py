# imports
import os
import time
import subprocess


# Vars
server_name = "www.test.com"
proxy_pass = "0.0.0.0:0000"
ssl_certificate = "/etc/letsencrypt/live/"+server_name+"/fullchain.pem"
ssl_certificate_key = "/etc/letsencrypt/live/"+server_name+"/privkey.pem"
ssl_trusted_certificate = "/etc/letsencrypt/live/"+server_name+"/fullchain.pem"
ext_ssl = "na"
ssl_proxy = "na"
chk1 = 0
cert_is_good = 0
ssl_proxy_int = "http://"

print ("""
    >>>SDC POX Utility<<<

    1.Add new site
    2.Disable a site
    3.Enable a site
    4.Exit/Quit
    """)
print "What would you like to do?"
ans = raw_input("Choice: ")


if ans == "1":
    print ('Selection 1')
    while chk1 is 0:
        print "What is the full TLD of the site you would like to add?"
        server_name = raw_input(": ")
        print "The Site you would like to add is:"
        print "" + server_name + ""
        print "Is this correct?"
        yn = raw_input("(y/n): ")
        if yn == "y":
            print "Checking if site is in nginx database..."
            site_exists = os.path.isfile("/etc/nginx/sites-enabled/" + server_name + ".conf")
            site_exists = os.path.isfile("/etc/nginx/sites-available/" + server_name + ".conf")
            # os.system("nslookup " + server_name + " > /tmp/nscheck")
            # TODO: implment check ^
            if site_exists is True:
                print "Site is configured, quitting..."
                quit()
            else:
                chk1 = 1
                print "Check PASSED, continuing..."
        else:
            chk1 = 0
    chk1 = 0
    while chk1 is 0:
        print 'Enter the IP address and port of the app you wish to proxy (in the format: ipaddress:port):'
        proxy_pass = raw_input("")
        print "Is this correct: " + proxy_pass
        yn = raw_input("(y/n): ")
        if yn == "y":
            chk2 = 0
            while chk2 is 0:
                print "Is " + proxy_pass + " an SSL protocol (i.e. https://" + proxy_pass + ')'
                yn2 = raw_input("(y/n): ")
                if yn2 == "n":
                    ssl_proxy = "False"
                    ssl_proxy_int = "http://"
                    chk2 = 1
                    chk1 = 1
                    print "SSL proxy has been set to: " + ssl_proxy
                elif yn2 == "y":
                    ssl_proxy = "True"
                    ssl_proxy_int = "https://"
                    chk2 = 1
                    chk1 = 1
                    print "SSL proxy has been set to: " + ssl_proxy
                else:
                    print "Error"
                    chk2 = 0
        else:
            chk1 = 0
    print "Will the user facing site need HTTPS/SSL (i.e https://"+server_name+")"
    print ("""
      1. HTTPS and HTTP
      2. HTTPS Only 
               """)
    print "Enter selection:"
    ssl_opt = raw_input(": ")
    chk3 = "0"
    while chk3 == "0":
        if ssl_opt == "1":
            chk3 = "1"
            print "Allowing both HTTPS and HTTP connections."
            ext_ssl = "both"
            ssl_certificate = "/etc/letsencrypt/live/" + server_name + "/fullchain.pem"
            ssl_certificate_key = "/etc/letsencrypt/live/" + server_name + "/privkey.pem"
            ssl_trusted_certificate = "/etc/letsencrypt/live/" + server_name + "/fullchain.pem"
        elif ssl_opt == "2":
            chk3 = "1"
            print "Allowing only HTTPS connections."
            ext_ssl = "https"
            ssl_certificate = "/etc/letsencrypt/live/" + server_name + "/fullchain.pem"
            ssl_certificate_key = "/etc/letsencrypt/live/" + server_name + "/privkey.pem"
            ssl_trusted_certificate = "/etc/letsencrypt/live/" + server_name + "/fullchain.pem"
#    if ssl_opt == "3":
#            print "Allowing only HTTP connections."
#            ext_ssl = "http"
        else:
            print "Error Not Implemented"
            chk3 = 0

    print """   Dose this information look correct: """
    print """   Server Name: """ + server_name
    print """   External connection default (https or http) : """ + ext_ssl
    print """   Local server address: """ + proxy_pass
    print """   Internal SSL connection to """ + proxy_pass + """ : """ + ssl_proxy

    confirm = raw_input("Confirm info (y/n): ")
    if confirm == "y":
        print "leggo :D... "
        cert_exists = os.path.isfile(ssl_certificate)
        if cert_exists == True:
            print "Skipping Cert Generation"
            cert_is_good = 1
        else:
            print "Stoping Nginx..."
            os.system('sudo service nginx stop')
            print "Nginx Stopped..."
            print "Executing LetsEncrypt..."
            subprocess.call('sudo letsencrypt certonly -d ' + server_name + ' > /tmp/certoutput', shell=True)
            print "LetsEncrypt started waiting..."
            print "Checking Cert..."
            cert_gen = 0
            while cert_gen < 20:
                for line in open("/tmp/certoutput"):
                    if "Congratulations!" in line:
                        cert_gen = 21
                        print "Congratulations! Cert has ben generated for: https://" + server_name
                        os.system('sudo service nginx start')
                        print "Restarted Nginx"
                        cert_is_good = 1
                    else:
                        time.sleep(1)
                        cert_gen = 1 + cert_gen
                        print "Killing in 20: " + cert_gen
                        cert_is_good = 0
            if cert_is_good == 1:
                print "Creating nginx conf file..."
                if ext_ssl == "both":
                    with open('/etc/nginx/sites-available/' + server_name + '.conf', 'a') as conf_file:
                        conf_file.write("""server {
                        listen 80;
                        server_name """ + server_name + """;
                        return  302 https://""" + server_name + """"$request_uri;

                }

                server {
                        listen 172.16.20.20:443;
                        server_name """ + server_name + """;

                        ssl_certificate """ + ssl_certificate + """;
                        ssl_certificate_key """ + ssl_certificate_key + """;
                        ssl_trusted_certificate """ + ssl_trusted_certificate + """;

                        access_log /var/log/nginx/""" + server_name + """.access.log;
                        error_log /var/log/nginx/""" + server_name + """.error.log;

                        location / {
                                proxy_set_header Host $http_host;
                                proxy_set_header X-Real-IP $remote_addr;
                                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                                proxy_redirect off;
                                proxy_pass """ + ssl_proxy_int + proxy_pass + """;
                                proxy_read_timeout 90;
                                proxy_ssl_verify off;
                        }
                }""")
                    print "Done"
                    #        if ext_ssl == "http":
                    #            print "not implemented cuz dont use http"
                if ext_ssl == "https":
                    with open('/etc/nginx/sites-available/' + server_name + '.conf', 'a') as conf_file:
                        conf_file.write("""server {
                                listen 172.16.20.20:443;
                                server_name """ + server_name + """;

                                ssl_certificate """ + ssl_certificate + """;
                                ssl_certificate_key """ + ssl_certificate_key + """;
                                ssl_trusted_certificate """ + ssl_trusted_certificate + """;

                                access_log /var/log/nginx/""" + server_name + """.access.log;
                                error_log /var/log/nginx/""" + server_name + """.error.log;

                                location / {
                                        proxy_set_header Host $http_host;
                                        proxy_set_header X-Real-IP $remote_addr;
                                        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                                        proxy_redirect off;
                                        proxy_pass """ + ssl_proxy_int + proxy_pass + """;
                                        proxy_read_timeout 90;
                                        proxy_ssl_verify off;
                                }
                        }""")
                    print "Done"
                print "Moving file into production..."
                os.system('sudo mv /etc/nginx/sites-available/' + server_name + '.conf /etc/nginx/sites-enabled/' + server_name + '.conf')
                print "Restarting Nginx..."
                os.system('sudo service nginx restart')
                print "Nginx Restarted..."
                print "New site successfully configured!"
                quit()
            else:
                os.system('sudo service nginx start')
                print "Something went wrong with cert generation quiting..."
                print "Please check if DNS entry is publicly accessible and points to SDC"
                quit()
    else:
        print "Failed to verify, quitting..."
        quit()


else:
    print ('Not implemented, quiting...')
    quit()