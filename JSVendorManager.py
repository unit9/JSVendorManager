import sublime
import sublime_plugin
import os

try:
    from urllib.request import Request
    from urllib.request import urlopen
    from urllib.error import HTTPError
    from urllib.error import URLError
    from urllib.request import ProxyHandler
    from urllib.request import build_opener
    from urllib.request import install_opener
except:
    from urllib2 import Request
    from urllib2 import urlopen
    from urllib2 import HTTPError
    from urllib2 import URLError
    from urllib2 import ProxyHandler
    from urllib2 import build_opener
    from urllib2 import install_opener

try:
    import simplejson as json
except ImportError:
    import json
# import json

# global lists, cahced in memory for now
cdnJSList = None
gitJSList = None

class JsvendormanagerCommand(sublime_plugin.WindowCommand):

    def __init__(self,someArgs):
        self.isEnabled = True

    def log(sefl,msg):
        sublime.active_window().active_view().set_status("JSVendorManager","[JSVendorManager] "+msg)
        print("[JSVendorManager] "+msg)

    def dlfile(self,url,dest_path,callback = None):
        # Open the url

        try:
            self.log("Downloading List...")
            f = urlopen(url)

            if(callback is None):
                bn = os.path.basename(url)
                dst = dest_path+"/"+bn
                print("downloading " + url + " to "+dst)
                # Open our local file for writing
                with open( dst, "wb") as local_file:
                    local_file.write(f.read())
            else:
                sublime.message_dialog("Parsing the JSON list may take a little while\nPlease be patient...")
                self.log("List Downloaded. Parsing JSON...")
                output = json.loads( f.read().decode("utf-8") )
                self.log("JSON parsed. Building list...")
                callback(output)
                
  

        #handle errors
        except HTTPError as e:
            print("HTTP Error:", e.code, url )
        except URLError as e:
            print("URL Error:", e.reason, url )

        self.isEnabled = True

    def DlAsync(self,url,dest_path,callback = None):
        sublime.set_timeout_async(lambda: self.dlfile(url,dest_path,callback), 0)


    ###########################################################################################

    def onCDNListLoaded(self,listObject):

        self.isEnabled = True
        global cdnJSList
        cdnJSList = listObject;

        self.listObject = listObject['packages']
        self.lst = []

        for item in self.listObject:

            text = []
            if( item.get('name') is not None ):
                text.append(item.get('name'))
            else:
                text.append("No Name")

            if( item.get('description') is not None ):
                desc = item.get('description')
                if(desc.__len__() > 70):
                    text.append(desc[:70]+"...") 
                else:
                    text.append(desc)   
            else:
                text.append("No Description")

            # if( item.get('homepage') is not None ):
            #     text.append("HomePage: "+item.get('homepage'))
            # else:
            #     text.append("No HomePage")



            self.lst.append( text )

        sublime.set_timeout(lambda: sublime.active_window().show_quick_panel(self.lst,self.onCDNPacketSelect), 10)   
        self.log("DONE")     

    def onCDNPacketSelect(self,selected):
        if(selected != -1):
            sel = self.listObject[selected]
            self.lst = []
            self.packetListObject = sel.get('assets');

            for item in self.packetListObject:
                
                item['name'] = sel.get("name")

                text = []

                if( item.get('version') is not None ):
                    text.append(item.get('version'))
                else:
                    text.append("Unknown Version")


                self.lst.append( text )

            sublime.set_timeout(lambda: sublime.active_window().show_quick_panel(self.lst,self.onCDNVersionSelect), 10)

    def onCDNVersionSelect(self,selected):
        if(selected != -1):
            sel = self.packetListObject[selected]
            self.lst = []
            self.filesListObject = []#sel.get('files');

            for item in sel.get('files'):
                
                itm = {}
                itm['name'] = sel.get("name")
                itm['version'] = sel.get("version")
                itm['filename'] = item
                self.filesListObject.append(itm)

                self.lst.append( item )

            sublime.set_timeout(lambda: sublime.active_window().show_quick_panel(self.lst,self.onCDNFileSelect), 10)

        
        
    def onCDNFileSelect(self,selected):
        if(selected != -1):
            sel = self.filesListObject[selected]
            url = "http://cdnjs.cloudflare.com/ajax/libs/"+sel.get('name')+"/"+sel.get('version')+"/"+sel.get('filename')

            # destination path

            dest_path = self.dest_path
            
            if dest_path is None:
                dest_path = sublime.active_window().project_file_name()

                if dest_path is None:
                    # look for open folders
                    folders = sublime.active_window().folders()
                    dest_path = folders[0]
                else:
                    # strip project name from project file path
                    ind = dest_path.rfind("\\")
                    dest_path = dest_path[:ind]

            self.DlAsync(url,dest_path)  
            
    ###########################################################################################

    def onListLoaded(self,listObject):
        
        self.isEnabled = True
        global gitJSList
        gitJSList = listObject;

        self.listObject = listObject
        self.lst = []

        for item in listObject:
            self.lst.append(item['caption'])

        sublime.set_timeout(lambda: sublime.active_window().show_quick_panel(self.lst,self.onListSelect), 10)
        self.log("DONE")
        


    def onListSelect(self,selected):
        if(selected != -1):
            sel = self.listObject[selected]
            self.lst = []
            self.subListObject = sel['packages']
            for item in self.subListObject:
                self.lst.append(item['caption'])

            sublime.set_timeout(lambda: sublime.active_window().show_quick_panel(self.lst,self.onSubListSelect), 10)

            


    def onSubListSelect(self,selected):
        if(selected != -1):
            sel = self.subListObject[selected]
            url = sel['url']

            # destination path

            dest_path = self.dest_path
            
            if dest_path is None:
                dest_path = sublime.active_window().project_file_name()

                if dest_path is None:
                    # look for open folders
                    folders = sublime.active_window().folders()
                    dest_path = folders[0]
                else:
                    # strip project name from project file path
                    ind = dest_path.rfind("\\")
                    dest_path = dest_path[:ind]

            self.DlAsync(url,dest_path)            

    ###########################################################################################

    def is_enabled(self):
        return self.isEnabled

    def run(self,dirs,mode = None):

        if(dirs is None or len(dirs) == 0):
            sublime.error_message("Please select a folder")
            return


        self.isEnabled = False
        self.dest_path = dirs[0]

        global cdnJSList
        global gitJSList

        if(mode == "cdnjs"):
            if cdnJSList is None:
                self.DlAsync("http://cdnjs.com/packages.json",None,self.onCDNListLoaded)
            else :
                self.onCDNListLoaded(cdnJSList)

        else:
            if gitJSList is None:
                self.DlAsync("https://raw.github.com/unit9IT/JSVendorManager/master/JSVendorPackages.json",None,self.onListLoaded)
            else:
                self.onListLoaded(gitJSList)


