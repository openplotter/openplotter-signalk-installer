## openplotter-signalk-installer

OpenPlotter app to manage Signal K node server installation

### Installing

#### For production

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **production** and just install this app from *OpenPlotter Apps* tab.

#### For development

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **development**.

Install openplotter-signalk-installer dependencies:

`sudo apt install libnss-mdns avahi-utils libavahi-compat-libdnssd-dev nodejs canboat`

Clone the repository:

`git clone https://github.com/openplotter/openplotter-signalk-installer`

Make your changes and create the package:

```
cd openplotter-signalk-installer
dpkg-buildpackage -b
```

Install the package:

```
cd ..
sudo dpkg -i openplotter-signalk-installer_x.x.x-xxx_all.deb
```

Run post-installation script:

`sudo signalkPostInstall`

Run:

`openplotter-signalk-installer`

Make your changes and repeat package, installation and post-installation steps to test. Pull request your changes to github and we will check and add them to the next version of the [Debian package](https://launchpad.net/~openplotter/+archive/ubuntu/openplotter).

### Documentation

https://openplotter.readthedocs.io

### Support

http://forum.openmarine.net/forumdisplay.php?fid=1
