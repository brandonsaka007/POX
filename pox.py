#imports
import os


#Vars
server_name = "www.test.com"
proxy_pass = "0.0.0.0:0000"
ssl_certificate = "/etc/letsencrypt/live/"+server_name+"/fullchain.pem"
ssl_certificate_key = "/etc/letsencrypt/live/"+server_name+"/privkey.pem"
ssl_trusted_certificate = "/etc/letsencrypt/live/"+server_name+"/fullchain.pem"
chk1 = 0
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
        server_name = raw_input("")
        print "The Site you would like to add is:"
        print ">>" + server_name + "<<"
        print "Is this correct? y/n"
        yn = raw_input("")
        if yn == "y":
            chk1 = 1
        else:
            chk1 = 0
    chk1 = 0
    while chk1 is 0:
        print 'Enter the IP address and port of the app you wish to proxy (in the format: ipddress:port):'
        proxy_pass = raw_input("")
        print "Is this correct: "+proxy_pass
        print "y/n"
        yn = raw_input("")
        if yn == "y":
            while chk1 == 0:
                print "Is "+proxy_pass+" an SSL protocol (i.e. Https://"+proxy_pass+')'
                print "(y/n)"
                yn = raw_input("")
                if yn == "y":
                    ssl_proxy = 1
                    chk1 = 1
                if yn == "n":
                    ssl_proxy = 0
                    chk1 = 1
                else:
                    chk1 =0
        else:
            chk1 = 0
    print "Will the user facing site need HTTPS/SSL (i.e https://"+server_name+")"
    print ("""
      1. HTTPS and HTTP
      2. HTTPS Only
      3. HTTP Only 
      4.Exit/Quit
            """)
    print "Enter selection:"
    httpvar = raw_input("")
    if httpvar == 1:
        print "1"
        ssl_certificate = "/etc/letsencrypt/live/" + server_name + "/fullchain.pem"
        ssl_certificate_key = "/etc/letsencrypt/live/" + server_name + "/privkey.pem"
        ssl_trusted_certificate = "/etc/letsencrypt/live/" + server_name + "/fullchain.pem"
        cert_exists = os.path.isdir(ssl_certificate)
        if cert_exists == "True":
            print "idk"
        else:
            os.system('sudo service ngixn stop')
            os.system('sudo letsencrypt certonly -d '+server_name+ ' > /tmp/certoutput')
            cert_gen = 0
            while cert_gen == 0:
                for line in open("/tmp/certoutput"):
                    if "Congratulations!" in line:
                        print line
                        cert_gen = 1
                    else:
                        cert_gen = 0

    if httpvar == 2:
            print "2"
    if httpvar == 3:
            print "3"


else:
    print ('not implemented')