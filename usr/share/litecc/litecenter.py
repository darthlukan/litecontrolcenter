import os
import sys
import subprocess

from configparser import ConfigParser

from gi.repository import Gtk as gtk
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import WebKit as webkit

from locale import getdefaultlocale

"""
# Linux Lite Control Center
# Developers - John 'ShaggyTwoDope' Jenkins, Jerry Bezencon
# Dependencies - python, python-webkit
# Licence - GPL v2
# Website - http://www.linuxliteos.com
"""

app_dir = '/usr/share/litecc'
lang = getdefaultlocale()[0].split('_')[0]


def execute(command, ret=True):
    """function to exec everything, subprocess used to fork"""

    if ret is True:
        p = os.popen(command)
        return p.readline()
    else:
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


# explictly use subprocess
def executep(command, ret=True):
    """function to exec everything, subprocess used to fork"""

    if ret is True:
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def functions(view, frame, req, data=None):
    """base functions"""
    uri = req.get_uri()
    lllink, path = uri.split('://', 1)
    path = path.replace("%20", " ")
    print(lllink)
    print(uri)
    if lllink == "file":
        return False
    elif lllink == "about":
        '''about dialog, need to add LDC members whom helped'''
        about = gtk.AboutDialog()
        about.set_program_name("Linux Lite Control Center")
        about.set_version("1.0-0010")
        about.set_license('''This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA. ''')
        about.set_authors([
            '''
            Johnathan 'ShaggyTwoDope' Jenkins
            <shaggytwodope@linuxliteos.com>

            Jerry Bezencon
            <valtam@linuxliteos.com>
            '''])
        about.set_comments("Designed for Linux Lite")
        about.set_website("http://www.linuxliteos.com")
        about.set_logo(gtk.render_icon_pixbuf("/usr/share/litecc/litecc.png"))
        about.run()
        about.destroy()
    elif lllink == "admin":
        execute(path)
    elif lllink == "exportdetails":
        dialog = gtk.FileChooserDialog("Select folder to export details to.", None,
                                       gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            export_details(dialog.get_filename())
        dialog.destroy()
    # uses executep to pipe process fork
    elif lllink == "script":
        execute("/usr/share/litecc/scripts/" + path)
    # need to fix urls
    elif lllink == "help":
        execute("exo-open file:///usr/share/doc/litemanual/index.html")
    elif lllink == "forum":
        execute("exo-open http://www.linuxliteos.com/forums/")
    elif lllink == "website":
        execute("exo-open http://www.linuxliteos.com/")
    elif lllink == "facebook":
        execute("exo-open https://www.facebook.com/pages/Linuxlite/572323192787066")
    elif lllink == "twitter":
        execute("exo-open http://www.twitter.com/linuxlite/")
    elif lllink == "google":
        execute("exo-open https://plus.google.com/+linuxliteos/")
    elif lllink == "linkedin":
        execute("exo-open http://www.linkedin.com/in/jerrybezencon")

    return True


def get_info(info):
    """here we gather some over all basic info"""
    try:
        if info == "os":
            return open('/etc/llver', 'r').read().split('\\n')[0]
        elif info == "arc":
            return os.uname()[4]
        elif info == "host":
            return os.uname()[1]
        elif info == "kernel":
            return os.uname()[0] + ' ' + os.uname()[2]
        elif info == "processor":
            return execute("cat /proc/cpuinfo | grep 'model name'").split(':')[1]
        elif info == "mem":
            mem = execute("free -m|awk '/^Mem:/{print $2}'")
            if float(mem) > 1024:
                return str(round(float(mem) / 1024)) + " GB"
            else:
                return "{0} MB".format(mem)
        elif info == "gfx":
            return execute("lspci | grep VGA").split('controller:')[1].split('(rev')[0].split(',')[0]
        elif info == "audio":
            return execute("lspci | grep Audio").split('device:')[1].split('(rev')[0].split(',')[0]
        elif info == "netstatus":
            return execute(
                "ping -q -w 1 -c 1 `ip r | grep default | cut -d ' ' -f 3` > /dev/null && echo Active || echo Not connected to any known network")
        elif info == "netip":
            ip = execute("hostname -i").split()
            if len(ip) > 1:
                ip = ip[0]
            return ip
    except (OSError, TypeError, Exception) as e:
        print(e)
        return " "


def export_details(file):
    x = open("%s/details.txt" % file, "w")
    x.write('''
Operating System: %s
Kernel: %s
Processor: %s
Architecture: %s
RAM: %s
Devices:
%s
Hard disks:

Mount Points:


This file was generated by Linux Lite Control Center. '''
            % (get_info("os"), get_info("kernel"), get_info("processor"),
               get_info("arc"), get_info("mem"), execute("lspci")))


def get_modules(section):
    """we try and load errrors"""
    try:
        mod_dir = os.listdir("/usr/share/litecc/modules/%s/" % section)
        mod_dir.sort()
    except Exception as details:
        os.system("zenity --error --text 'Error : {0}' --title 'Module Loading Error'".format(details))
        return exit()

    if isinstance(mod_dir, list) and len(mod_dir) < 1:
        return "<p>" + "no modules found!" + "</p>"
    else:
        parser = ConfigParser()
        admin = ""
        mod_dir.sort()
        for i in mod_dir:
            parser.read("/usr/share/litecc/modules/%s/%s" % (section, i))
            '''look for icons'''
            ico = parser.get('module', 'ico')
            # check if the icon exists
            ico = "/usr/share/litecc/frontend/icons/modules/" + ico

            # check if the name has a different language
            if parser.has_option('module', 'name[%s]'):
                name = parser.get('module', 'name[%s]')
            else:
                name = parser.get('module', 'name')

            # check if the description has a different language
            if parser.has_option('module', 'desc[%s]'):
                desc = parser.get('module', 'desc[%s]')
            else:
                desc = parser.get('module', 'desc')

            command = parser.get('module', 'command')
            command = command.replace("'", ''' \\' ''')

            admin += '''<div class="launcher" onclick="location.href='admin://%s'" >
            <img src="%s" onerror='this.src = "/usr/share/litecc/frontend/icons/modules/notfound.png"'/>
            <h3>%s</h3>
            <span>%s</span>
            </div>''' % (command, ico, name, desc)
        return admin


def frontend_fill():
    """build all html junk"""

    strings_to_replace = {
        "{DIR_dir}": "ltr",
        "{string_1}": "System Information",
        "{string_2}": "A brief overview of your system",
        "{string_3}": "Computer",
        "{string_4}": "Operating System: ",
        "{string_5}": "Processor: ",
        "{string_6}": "Architecture: ",
        "{string_7}": "Installed Memory: ",
        "{string_8}": "Devices",
        "{string_9}": "Graphics Card: ",
        "{string_10}": "Sound Card: ",
        "{string_11}": "Ethernet: ",
        "{string_12}": "Misc",
        "{string_13}": "Hostname: ",
        "{string_14}": "Kernel: ",
        "{string_15}": "UNUSED",
        "{string_16}": "Software",
        "{string_17}": "Installing and maintaining software on your system",
        "{string_18}": "Desktop",
        "{string_19}": "Manage your desktop environment",
        "{string_20}": "System",
        "{string_21}": "Configure and customize your computer",
        "{string_22}": "Hardware",
        "{string_23}": "Hardware management and configuration for your computer",
        "{string_24}": "Network",
        "{string_25}": "Manage and configure your home network and connections",
        "{string_26}": "Forum",
        "{string_27}": "Help",
        "{string_28}": "Install Popular Software",
        "{string_29}": "Guide",
        "{string_30}": "Status: ",
        "{string_31}": "Local IP Address: ",
        "{string_32}": "Internet",
        "{string_33}": "TIP: ",
        "{string_34}": "UNUSED",
        "{string_35}": "Install Desktop Extras",
        "{string_36}": "Here you can install Desktop addons, select one to install",
        "{string_37}": "Export system details",
        "{string_38}": "UNUSED",
        "{string_39}": "UNUSED",
        "{string_40}": "save packages",
        "{string_41}": "Hardware drivers and players",
        "{string_42}": "Manage Hardware on your system",
        "{string_43}": "Nvidia graphics card driver",
        "{string_44}": "Bluetooth driver",
        "{string_45}": "Camera driver",
        "{string_46}": "Scanner driver",
        "{string_47}": "Website",
        "{string_48}": "LinkedIn",
        "{string_49}": "Facebook",
        "{string_50}": "Twitter",
        "{string_51}": "Google+"
    }
    filee = open(app_dir + '/frontend/default.html', 'r')
    page = filee.read()
    for key, value in strings_to_replace.items():
        page = page.replace(key, value)

    for i in ['os', 'arc', 'processor', 'mem', 'gfx', 'audio', 'kernel', 'host', 'netstatus', 'netip']:
        page = page.replace("{%s}" % i, get_info(i))

    sections = ['software', 'system', 'desktop', 'hardware', 'networking']
    sections.sort()
    for i in sections:
        page = page.replace("{%s_list}" % i, get_modules(i))
    filee.close()
    return page


def main():
    global browser
    global window

    frontend = frontend_fill()

    window = gtk.Window()
    window.connect('destroy', gtk.main_quit)
    window.set_title("Linux Lite Control Center")
    window.set_icon(Pixbuf.new_from_file("/usr/share/litecc/litecc.png"))
    window.set_size_request(870, 570)
    # Valtam do we need to resize window?
    window.set_resizable(False)
    window.set_position(gtk.WindowPosition.CENTER),
    browser = webkit.WebView()
    swindow = gtk.ScrolledWindow()
    window.add(swindow)
    swindow.add(browser)
    window.show_all()
    browser.connect("navigation-requested", functions)
    browser.load_html_string(frontend, 'file:///usr/share/litecc/frontend/')
    # no right click menu
    settings = browser.get_settings()
    settings.set_property('enable-default-context-menu', False)
    browser.set_settings(settings)
    # Engage
    gtk.main()

if __name__ == '__main__':
    try:
        main()
    except (Exception, AttributeError, FileNotFoundError) as e:
        print("Exiting due to error: {0}".format(e))
        sys.exit(1)
