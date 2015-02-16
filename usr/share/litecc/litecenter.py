import os
import sys
import subprocess

from configparser import ConfigParser

from gi.repository import Gtk as gtk

import webkit  # ImportError

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

    if lllink == "about":
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
        return True

    if lllink == "admin":
        execute(path)
        return True

    if lllink == "exportdetails":
        dialog = gtk.FileChooserDialog("Select folder to export details to.", None,
                                       gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            export_details(dialog.get_filename())
        dialog.destroy()
        return True
    # uses executep to pipe process fork
    if lllink == "script":
        execute("/usr/share/litecc/scripts/" + path)
        return True

    # need to fix urls
    if lllink == "help":
        execute("exo-open file:///usr/share/doc/litemanual/index.html")
        return True

    if lllink == "forum":
        execute("exo-open http://www.linuxliteos.com/forums/")
        return True

    if lllink == "website":
        execute("exo-open http://www.linuxliteos.com/")
        return True

    if lllink == "facebook":
        execute("exo-open https://www.facebook.com/pages/Linuxlite/572323192787066")
        return True

    if lllink == "twitter":
        execute("exo-open http://www.twitter.com/linuxlite/")
        return True

    if lllink == "google":
        execute("exo-open https://plus.google.com/+linuxliteos/")
        return True

    if lllink == "linkedin":
        execute("exo-open http://www.linkedin.com/in/jerrybezencon")
        return True


def get_info(info):
    """here we gather some over all basic info"""
    try:
        if info == "os":
            return open('/etc/llver', 'r').read().split('\\n')[0]
        if info == "arc":
            return os.uname()[4]
        if info == "host":
            return os.uname()[1]
        if info == "kernel":
            return os.uname()[0] + ' ' + os.uname()[2]
        if info == "processor":
            return execute("cat /proc/cpuinfo | grep 'model name'").split(':')[1]
        if info == "mem":
            mem = execute("free -m|awk '/^Mem:/{print $2}'")
            if float(mem) > 1024:
                return str(round(float(mem) / 1024)) + " GB"
            else:
                return mem + " MB"
        if info == "gfx":
            return execute("lspci |grep VGA").split('controller:')[1].split('(rev')[0].split(',')[0]
        if info == "audio":
            return execute("lspci |grep Audio").split('device:')[1].split('(rev')[0].split(',')[0]
        if info == "netstatus":
            return execute(
                "ping -q -w 1 -c 1 `ip r | grep default | cut -d ' ' -f 3` > /dev/null && echo Active || echo Not connected to any known network")
        if info == "netip":
            return execute("hostname -I")
    except:
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
        os.system("zenity --error --text 'Error : {0}' --title 'Module Loading Error'".format(details.message))
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
    '''build all html junk'''

    filee = open(app_dir + '/frontend/default.html', 'r')
    page = filee.read()
    page = page.replace("{DIR_dir}", "ltr")

    page = page.replace("{string_1}", "System Information")
    page = page.replace("{string_2}", "A brief overview of your system")
    page = page.replace("{string_3}", "Computer")
    page = page.replace("{string_4}", "Operating System: ")
    page = page.replace("{string_5}", "Processor: ")
    page = page.replace("{string_6}", "Architecture: ")
    page = page.replace("{string_7}", "Installed Memory: ")
    page = page.replace("{string_8}", "Devices")
    page = page.replace("{string_9}", "Graphics Card: ")
    page = page.replace("{string_10}", "Sound Card: ")
    page = page.replace("{string_11}", "Ethernet: ")
    page = page.replace("{string_12}", "Misc")
    page = page.replace("{string_13}", "Hostname: ")
    page = page.replace("{string_14}", "Kernel: ")
    page = page.replace("{string_15}", "UNUSED")
    page = page.replace("{string_16}", "Software")
    page = page.replace("{string_17}", "Installing and maintaining software on your system")
    page = page.replace("{string_18}", "Desktop")
    page = page.replace("{string_19}", "Manage your desktop environment")
    page = page.replace("{string_20}", "System")
    page = page.replace("{string_21}", "Configure and customize your computer")
    page = page.replace("{string_22}", "Hardware")
    page = page.replace("{string_23}", "Hardware management and configuration for your computer")
    page = page.replace("{string_24}", "Network")
    page = page.replace("{string_25}", "Manage and configure your home network and connections")
    page = page.replace("{string_26}", "Forum")
    page = page.replace("{string_27}", "Help")
    page = page.replace("{string_28}", "Install Popular Software")
    page = page.replace("{string_29}", "Guide")
    page = page.replace("{string_30}", "Status: ")
    page = page.replace("{string_31}", "Local IP Address: ")
    page = page.replace("{string_32}", "Internet")
    page = page.replace("{string_33}", "TIP: ")
    page = page.replace("{string_34}", "UNUSED")
    page = page.replace("{string_35}", "Install Desktop Extras")
    page = page.replace("{string_36}", "Here you can install Desktop addons, select one to install")
    page = page.replace("{string_37}", "Export system details")
    page = page.replace("{string_38}", "UNUSED")
    page = page.replace("{string_39}", "UNUSED")
    page = page.replace("{string_40}", "save packages")
    page = page.replace("{string_41}", "Hardware drivers and players")
    page = page.replace("{string_42}", "Manage Hardware on your system")
    page = page.replace("{string_43}", "Nvidia graphics card driver")
    page = page.replace("{string_44}", "Bluetooth driver")
    page = page.replace("{string_45}", "Camera driver")
    page = page.replace("{string_46}", "Scanner driver")
    page = page.replace("{string_47}", "Website")
    page = page.replace("{string_48}", "LinkedIn")
    page = page.replace("{string_49}", "Facebook")
    page = page.replace("{string_50}", "Twitter")
    page = page.replace("{string_51}", "Google+")

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
    window.set_icon(gtk.render_icon_pixbuf("/usr/share/litecc/litecc.png"))
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
        print("Exiting due to error: {0}".format(e.message))
        sys.exit(1)
