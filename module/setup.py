#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License,
    or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <http://www.gnu.org/licenses/>.
    
    @author: RaNaN
"""
from getpass import getpass
import gettext
from hashlib import sha1
from os import remove
from os.path import abspath
from os.path import dirname
from os.path import isfile
from os.path import join
import random
import re
from subprocess import PIPE
from subprocess import call
import sys

class Setup():
    """
    pyLoads initial setup configuration assistent
    """
    def __init__(self, path, config):

        self.path = path
        self.config = config


    def start(self):
        
        lang = self.ask("Choose your Language / Wähle deine Sprache", "en", ["en", "de"])
        translation = gettext.translation("setup", join(self.path, "locale"), languages=[lang])
        translation.install(unicode=(True if  sys.getfilesystemencoding().startswith("utf") else False))

        print ""
        print _("Welcome to the pyLoad Configuration Assistent.")
        print _("It will check your system and make a basic setup in order to run pyLoad.")
        print ""
        print _("The value in brackets [] always is the default value,")
        print _("in case you don't want to change it or you are unsure what to choose, just hit enter.")
        print _("Don't forget: You can always rerun this assistent with --setup or -s parameter, when you start pyLoadCore.")
        print _("If you have any problems with this assistent hit STRG-C,")
        print _("to abort and don't let him start with pyLoadCore automatically anymore.")
        print ""
        print _("When you are ready for system check, hit enter.")
        raw_input()

        basic, ssl, captcha, gui, web = self.system_check()
        print ""

        if not basic:
            print _("You need pycurl and python 2.5 or 2.6 to run pyLoad.")
            print _("Please correct this and re run pyLoad.")
            print _("Setup will now close.")
            raw_input()
            return False

        raw_input(_("System check finished, hit enter to see your status report."))
        print ""
        print _("## Status ##")

        print _("py-crypto available") if self.check_module("Crypto") else _("no py-crypto available")
        print _("You need this if you want to decrypt container files.")
        print ""
        print _("SSL available") if ssl else _("no SSL available")
        print _("This is needed if you want to establish a secure connection to core or webinterface.")
        print _("If you only want to access locally to pyLoad ssl is not usefull.")
        print ""
        print _("Captcha Recognition available") if captcha else _("no Captcha Recognition available")
        print _("Only needed for some hosters and as freeuser.")
        print ""
        print _("Gui available") if gui else _("Gui not available")
        print _("The Graphical User Interface.")
        print ""
        print _("Webinterface available") if web else _("no Webinterface available")
        print _("Gives abillity to control pyLoad with your webbrowser.")
        print ""
        print _("You can abort the setup now and fix some dependicies if you want.")

        con = self.ask(_("Continue with setup?"), "y", bool=True)

        if not con:
            return False

        print ""
        print _("Do you want to configure basic settings?")
        print _("This is recommend for first run.")
        con = self.ask(_("Make basic setup?"), "y", bool=True)

        if con:
            self.conf_basic()

        if ssl:
            print ""
            print _("Do you want to configure ssl?")
            ssl = self.ask(_("Configure ssl?"), "n", bool=True)
            if ssl:
                self.conf_ssl()

        if web:
            print ""
            print _("Do you want to configure webinterface?")
            web = self.ask(_("Configure webinterface?"), "y", bool=True)
            if web:
                self.conf_web()

        print ""
        print _("Setup finished successfully.")
        return True

    def system_check(self):
        """ make a systemcheck and return the results"""
        print _("## System Check ##")

        python = False

        if sys.version_info > (2, 7):
            print _("Your python version is to new, Please use Python 2.6")
            python = False
        elif sys.version_info < (2, 5):
            print _("Your python version is to old, Please use at least Python 2.5")
            python = False
        else:
            print _("Python Version: OK")
            python = True

        if not self.check_prog(["python", "-V"]):
            print _("Unable to execute the 'python' command")
            print _("Please add python to system path or create a symlink")
            python = False

        curl = self.check_module("pycurl")
        self.print_dep("pycurl", curl)

        crypto = self.check_module("Crypto")
        self.print_dep("pycrypto", crypto)

        basic = python and curl

        ssl = self.check_module("OpenSSL")
        self.print_dep("OpenSSL", ssl)

        print ""

        pil = self.check_module("Image")
        self.print_dep("py-imaging", pil)

        tesser = self.check_prog(["tesseract", "-v"])
        self.print_dep("tesseract", tesser)

        gocr = self.check_prog(["gocr", "-h"])
        self.print_dep("gocr", gocr)

        captcha = pil and tesser

        print ""

        gui = self.check_module("PyQt4")
        self.print_dep("PyQt4", gui)

        print ""

        web = self.check_module("django")
        sqlite = self.check_module("sqlite3")

        try:
            import django

            if django.VERSION < (1, 1):
                print _("Your django version is to old, please upgrade to django 1.1")
                web = False
            elif django.VERSION > (1, 3):
                print _("Your django version is to new, please use django 1.2")
                web = False
        except:
            web = False

        self.print_dep("django", web)
        self.print_dep("sqlite3", sqlite)
        web = web and sqlite

        return (basic, ssl, captcha, gui, web)

    def conf_basic(self):
        print ""
        print _("## Basic Setup ##")

        print ""
        print _("The following logindata are only valid for CLI and GUI, but NOT for webinterface.")
        self.config["remote"]["username"] = self.ask(_("Username"), "User")
        self.config["remote"]["password"] = self.ask("", "", password=True)

        print ""
        self.config["general"]["language"] = self.ask(_("Language"), "en", ["en", "de", "fr", "nl", "pl"])
        self.config["general"]["download_Folder"] = self.ask(_("Downloadfolder"), "Downloads")
        self.config["general"]["max_downloads"] = self.ask(_("Max parallel downloads"), "3")
        print _("You should disable checksum proofing, if you have low hardware requirements.")
        self.config["general"]["checksum"] = self.ask(_("Proof checksum?"), "y", bool=True)

        reconnect = self.ask(_("Use Reconnect?"), "n", bool=True)
        self.config["reconnect"]["activated"] = reconnect
        if reconnect:
            self.config["reconnect"]["method"] = self.ask(_("Reconnect script location"), "./reconnect.sh")


    def conf_web(self):
        print ""
        print _("## Webinterface Setup ##")

        db_path = join(self.path, "module", "web", "pyload.db")
        is_db = isfile(db_path)
        db_setup = True

        if is_db:
            print _("You already have a database for the webinterface.")
            db_setup = self.ask(_("Do you want to delete it and make a new one?"), "n", bool=True)

        if db_setup:
            if is_db: remove(db_path)
            import sqlite3

            
            print ""
            call(["python", join(self.path, "module", "web", "manage.py"), "syncdb", "--noinput"])
            print _("If you see no errors, your db should be fine and we're adding an user now.")
            username = self.ask(_("Username"), "User")
            call(['python', join(self.path, "module", "web", "manage.py"), 'createsuperuser', '--email=email@trash-mail.com', '--username=%s' % username, '--noinput'])

            password = self.ask("", "", password=True)
            salt = reduce(lambda x, y: x + y, [str(random.randint(0, 9)) for i in range(0, 5)])
            hash = sha1(salt + password)
            password = "sha1$%s$%s" % (salt, hash.hexdigest())

            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute('UPDATE "main"."auth_user" SET "password"=? WHERE "username"=?', (password, username))

            conn.commit()
            c.close()

        print ""
        self.config["webinterface"]["activated"] = self.ask(_("Activate webinterface?"), "y", bool=True)
        print ""
        print _("Listen address, if you use 127.0.0.1 or localhost, the webinterface will only accessible locally.")
        self.config["webinterface"]["host"] = self.ask(_("Address"), "0.0.0.0")
        self.config["webinterface"]["port"] = self.ask(_("Port"), "8000")
        #@TODO setup for additional webservers

    def conf_ssl(self):
        print ""
        print _("## SSL Setup ##")
        print ""
        print _("Execute these commands from pyLoad folder to make ssl certificates:")
        print ""
        print "openssl genrsa - 1024 > ssl.key"
        print "openssl req -new -key ssl.key -out ssl.csr"
        print "openssl req -days 36500 -x509 -key ssl.key -in ssl.csr > ssl.crt "
        print ""
        print _("If you're done and everything went fine, you can activate ssl now.")

        self.config["ssl"]["activated"] = self.ask(_("Activate SSL?"), "y", bool=True)

    def set_user(self):

        translation = gettext.translation("setup", join(self.path, "locale"), languages=[self.config["general"]["language"]])
        translation.install(unicode=(True if  sys.getfilesystemencoding().startswith("utf") else False))
        print _("Setting new username and password")
        print ""
        self.config["remote"]["username"] = self.ask(_("Username"), "User")
        self.config["remote"]["password"] = self.ask("", "", password=True)

    def print_dep(self, name, value):
        """Print Status of dependency"""
        if value:
            print _("%s: OK" % name)
        else:
            print _("%s: missing" % name)


    def check_module(self, module):
        try:
            __import__(module)
            return True
        except:
            return False

    def check_prog(self, command):
        pipe = PIPE
        try:
            call(command, stdout=pipe, stderr=pipe)
            return True
        except:
            return False

    def ask(self, qst, default, answers=[], bool=False, password=False):
        """produce one line to asking for input"""
        if answers:
            info = "("

            for i, answer in enumerate(answers):
                info += (", " if i != 0 else "") + str((answer == default and "[%s]" % answer) or answer)

            info += ")"
        elif bool:
            if default == "y":
                info = "([y]/n)"
            else:
                info = "(y/[n])"
        else:
            info = "[%s]" % default

        if password:
            p1 = True
            p2 = False
            while p1 != p2:
                p1 = getpass(_("Password: "))

                if len(p1) < 4:
                    print _("Password to short. Use at least 4 symbols.")
                    continue

                p2 = getpass(_("Password (again): "))

                if p1 == p2:
                    return p1
                else:
                    print _("Passwords did not match.")

        while True:
            input = raw_input(qst + " %s: " % info)

            if input.strip() == "":
                input = default

            if bool:
                if re.match(r"(y|yes|j|ja|true)", input.lower().strip()):
                    return True
                elif re.match(r"(n|no|nein|false)", input.lower().strip()):
                    return False
                else:
                    print _("Invalid Input")
                    continue


            if not answers:
                return input

            else:
                if input in answers:
                    return input
                else:
                    print _("Invalid Input")


if __name__ == "__main__":
    test = Setup(join(abspath(dirname(__file__)), ".."), None)
    test.start()