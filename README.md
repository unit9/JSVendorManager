Sublime JSVendorManager
===============

A Javascript vendor downloader/updater for **Sublime Text 3** that downloads libraries directly from their GIT/CDN sources and places them in the selected folder.

Useful for setting up new projects and download specific version of a library.

Installation
-------------

* Download as ZIP
* Open Preferences -> Browse Packages in Sublime Text 3
* Unzip contents into JSVendorManager subfolder (win) or Packages/JSVendorManager (OSX)

Usage
-------------

* In Sublime Text 3, right-click into any folder 
* Select `Download JS Vendor (cdnjs, slower)` to select from a list of Libraries downloaded directly from http://cdnjs.com/ **WARNING**: this method takes a long time in order to parse the JSON file, be patient
* Select `"Download JS Vendor (github, faster)` to select from a list of Libraries created and mantained internally  **WARNING**: this method is faster but libraries are not guarateed to be up-to-date