# main.py
#
# Copyright 2023 Bytez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw
from .window import IplookupWindow

from . import ipapi

class IplookupApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='io.github.bytezz.IPLookup',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.create_action('quit', self.on_quit_action, ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('get-your-ip', self.on_get_your_ip_action)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        self.win = self.props.active_window
        if not self.win:
            self.win = IplookupWindow(application=self)
        self.win.present()

        self.win.ip_entry.connect("apply", self.on_search)
        #self.win.search_btn.connect("clicked", self.on_search)

    def on_quit_action(self, widget, _):
        self.quit()

    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutDialog(application_name='IP Lookup',
                                application_icon='io.github.bytezz.IPLookup',
                                developer_name='Bytez',
                                website='https://github.com/Bytezz/IPLookup-gtk',
                                issue_url='https://github.com/Bytezz/IPLookup-gtk/issues',
                                version='0.4.0',
                                developers=['Bytez'],
                                translator_credits=_("translator-credits"),
                                license_type=Gtk.License.GPL_3_0,
                                copyright='Copyright© 2023 Bytez')
        about.present(self.props.active_window)

    def on_get_your_ip_action(self, widget, _):
        self.win.ip_entry.set_text(ipapi.get_your_ip())
        self.win.ip_entry.grab_focus()
        self.win.ip_entry.set_position(-1)
        self.on_search(self)

    def remove_ip_row(self, _, row):
        self.win.ip_row.remove(row)

    def on_search(self, widget):
        # TODO: Call deferred
        # TODO: Show an osd GtkProgressBar
        if self.win.ip_entry.get_text().strip() != "":
            if ipapi.internet_available():
                ipinfo = ipapi.get_ip_info(self.win.ip_entry.get_text())

                if ipinfo != {} and ipinfo["status"] == "success":
                    if not ipapi.is_ip(self.win.ip_entry.get_text()):
                        self.win.ip_row.set_subtitle(ipinfo["query"])

                        for i in ipapi.resolve_ips(self.win.ip_entry.get_text()):
                            row = Adw.ActionRow(title=i, title_selectable=True)
                            self.win.ip_entry.connect("apply", self.remove_ip_row, row)
                            self.win.ip_row.add_row(row)

                        self.win.ip_row.set_visible(True) # TODO: Animate
                    else:
                        self.win.ip_row.set_visible(False)

                    self.win.network_label.set_label(ipinfo["as"])
                    self.win.isp_label.set_label(ipinfo["isp"])
                    self.win.org_label.set_label(ipinfo["org"])

                    self.win.city_label.set_label(ipinfo["city"])
                    self.win.region_label.set_label(ipinfo["regionName"]+", "+ipinfo["region"])
                    self.win.country_label.set_label(ipinfo["country"]+", "+ipinfo["countryCode"])
                    self.win.zip_label.set_label(ipinfo["zip"])
                    self.win.timezone_label.set_label(ipinfo["timezone"])
                    self.win.coordinates_label.set_label(str(ipinfo["lat"])+", "+str(ipinfo["lon"]))
                    self.win.coordinates_label.set_uri("geo://"+str(ipinfo["lat"])+","+str(ipinfo["lon"]))
                    self.win.coordinates_label.set_visible(True)
                elif "message" in ipinfo:
                    self.win.toast.add_toast(Adw.Toast.new(ipinfo["message"].capitalize()))
            else:
                # TODO: Repleace with a banner
                self.win.error_dialog.set_body("No internet connection available.")
                self.win.error_dialog.present()

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    app = IplookupApplication()
    return app.run(sys.argv)


