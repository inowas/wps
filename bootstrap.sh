    sudo apt-get update
    sudo apt-get install -y apache2 libxml2-dev libxslt1-dev libgdal-dev python-gdal python-setuptools python-magic python-lxml python-pip git vim libfreetype6-dev libxft-dev libpng-dev pkg-config python-dev python-scipy libapache2-mod-wsgi 
    sudo a2enmod wsgi

    sudo echo "
WSGIScriptAlias / /var/www/wps/wsgiwps.py    
WSGIPythonPath /var/www/wps

<VirtualHost *:80>
    DocumentRoot /var/www/wps

    SetEnv PYTHONPATH /usr/local/pywps/pywps
    SetEnv PYWPS_CFG /usr/local/wps/pywps.cfg
    SetEnv PYWPS_PROCESSES /usr/local/wps/processes

    <Directory /var/www/>
        <Files wsgiwps.py>
            Order deny,allow
            Allow from all
        </Files>
    </Directory>

    LogLevel debug

    ErrorLog /tmp/error_wps.log
    CustomLog /tmp/access_wps.log combined
</VirtualHost>
" >> /etc/apache2/sites-available/wps.conf
    sudo a2ensite wps
    sudo a2dissite 000-default
    cd /usr/local
    sudo git clone https://github.com/geopython/pywps.git -b pywps-3.2 --single-branch
    sudo chmod 777 /usr/local/pywps/pywps/Templates/1_0_0
    cd /usr/local/pywps
    sudo echo "" > requirements.txt
    sudo python setup.py install
    sudo pip install matplotlib
    sudo pip install pyKriging
    sudo pip install flopy
    sudp pip install demjson
