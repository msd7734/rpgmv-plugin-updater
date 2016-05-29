===================================
=== RPG Maker MV Plugin Updater ===
===       By: EdLolington       ===
===================================

Purpose
-------
If you've developing a project using certain plugins, you'll want to keep them
up to date to ensure you're getting bugfixes and can develop with the plugins'
latest features in mind. But this isn't too easy since you have to go out to
various sources online to check for updates all the time, which can get tedious,
especially if you have a lot of plugins.

This plugin updater can read which plugins you've installed in a project and
check a user-defined internet update source against your local versions each
time you run it. You can set it to automatically overwrite your old plugins
with new versions if they're found, or download them to a separate folder.

Files
-----
The following files should come with the plugin updater:
	PluginUpdater.exe - 	The program you run
	updateconfig.ini - 	Configure PluginUpdater's behavior
	readme.txt - 		This file

Usage
-----
Place PluginUpdater and updateconfig in the same folder. By default the program
expects this folder will be a project root folder (the same folder as the
Game.rpgproject file). The default config provided will look for your plugins.js
file in the /js folder, and for your plugins themselves in /js/plugins .

In addition, updateconfig.ini is setup by default to check for and update any and
all installed Yanfly plugins.

If you want to place these files somewhere else or add different plugins for update
checking, you'll have to edit updateconfig.ini. Explanations of what each setting
does can be found as comments in updateconfig.ini
