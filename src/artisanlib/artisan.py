import multiprocessing

from artisanlib import pyqtversion

if pyqtversion < 6:
    from PyQt5.QtCore import pyqtSlot, QEvent, QUrl
else:
    from PyQt6.QtCore import pyqtSlot, QEvent, QUrl

from artisanlib.qtsingleapplication import QtSingleApplication


appGuid = '9068bd2fa8e54945a6be1f1a0a589e92'
viewerAppGuid = '9068bd2fa8e54945a6be1f1a0a589e93'


class Artisan(QtSingleApplication):
    def __init__(self, args):
        super(Artisan, self).__init__(appGuid,viewerAppGuid,args)

        self.sentToBackground = None # set to timestamp on putting app to background without any open dialog
        self.plus_sync_cache_expiration = 1*60 # how long a plus sync is valid in seconds

        if multiprocessing.current_process().name == 'MainProcess' and self.isRunning():
            self.artisanviewerMode = True
            if not platf=="Windows" and self.isRunningViewer(): sys.exit(0) # there is already one ArtisanViewer running, we terminate
        else:
            self.artisanviewerMode = False
        self.messageReceived.connect(self.receiveMessage)
        self.focusChanged.connect(self.appRaised)

    @pyqtSlot("QWidget*","QWidget*")
    def appRaised(self,oldFocusWidget,newFocusWidget):
        try:
            if not sip.isdeleted(aw): # sip not supported on older PyQt versions (eg. RPi)
                if oldFocusWidget is None and newFocusWidget is not None and aw is not None and aw.centralWidget() == newFocusWidget and self.sentToBackground is not None:
                    #focus gained
                    try:
                        if aw is not None and aw.plus_account is not None and aw.qmc.roastUUID is not None and aw.curFile is not None and \
                                libtime.time() - self.sentToBackground > self.plus_sync_cache_expiration:
                            plus.sync.getUpdate(aw.qmc.roastUUID,aw.curFile)
                    except:
                        pass
                    self.sentToBackground = None

                elif oldFocusWidget is not None and newFocusWidget is None and aw is not None and aw.centralWidget() == oldFocusWidget:
                    # focus released
                    self.sentToBackground = libtime.time() # keep the timestamp on sending the app with the main window to background
                else: # on raising another dialog/widget was open, reset timer
                    self.sentToBackground = None
        except:
            pass

    # takes a QUrl and interprets it as follows
    # artisan://roast/<UUID>         : loads profile from path associated with the given roast <UUID>
    # artisan://template/<UUID>      : loads background profile from path associated with the given roast <UUID>
    # artisan://profile?url=<url>    : loads proflie from given URL
    # file://<path>                  : loads file from path
    #                                  if query is "background" Artisan is not raised to the foreground
    #                                  if query is "template" and the file has an .alog extension, the profile is loaded as background profile
    def open_url(self, url):
        if not aw.qmc.flagon and not aw.qmc.designerflag and not aw.qmc.wheelflag and aw.qmc.flavorchart_plot is None: # only if not yet monitoring
            if url.scheme() == "artisan" and url.authority() in ['roast','template']:
                # we try to resolve this one into a file URL and recurse
                roast_UUID = url.toString(QUrl.RemoveScheme | QUrl.RemoveAuthority | QUrl.RemoveQuery | QUrl.RemoveFragment | QUrl.StripTrailingSlash)[1:]
                if aw.qmc.roastUUID is None or aw.qmc.roastUUID != roast_UUID:
                    # not yet open, lets try to find the path to that roastUUID and open it
                    profile_path = plus.register.getPath(roast_UUID)
                    if profile_path:
                        aw.sendmessage(QApplication.translate("Message","URL open profile: {0}",None).format(profile_path))
                        file_url = QUrl.fromLocalFile(profile_path)
                        if url.authority() == 'template':
                            file_url.setQuery("template")
                        self.open_url(file_url)
            elif url.scheme() == "artisan" and url.authority() == 'profile' and url.hasQuery():
                try:
                    query = QUrlQuery(url.query())
                    if query.hasQueryItem("url"):
                        QTimer.singleShot(5,lambda: aw.importExternalURL(aw.artisanURLextractor,url=QUrl(query.queryItemValue("url"))))
                except Exception:
#                    import traceback
#                    traceback.print_exc(file=sys.stdout)
                    pass
            elif url.scheme() == "file":
                aw.sendmessage(QApplication.translate("Message","URL open profile: {0}",None).format(url.toDisplayString()))
                url_query = None
                if url.hasQuery():
                    url_query = url.query()
                if url_query is None or url_query != "background":
                    # by default we raise Artisan to the foreground
                    QTimer.singleShot(20,lambda: self.activateWindow())
                url.setQuery(None) # remove any query to get a valid file path
                url.setFragment(None) # remove also any potential fragment
                filename = url.toString(QUrl.PreferLocalFile)
                qfile = QFileInfo(filename)
                file_suffix = qfile.suffix()
                if file_suffix == "alog":
                    if bool(aw.comparator):
                        # add Artisan profile to the comparator selection
                        QTimer.singleShot(20,lambda : aw.comparator.addProfiles([filename]))
                    else:
                        # load Artisan profile on double-click on *.alog file
                        if url_query is not None and url_query == "template":
                            aw.loadBackgroundSignal.emit(filename)
                        else:
                            QTimer.singleShot(20,lambda : aw.loadFile(filename))
                elif file_suffix == "alrm":
                    # load Artisan alarms on double-click on *.alrm file
                    QTimer.singleShot(20,lambda : aw.loadAlarms(filename))
                elif file_suffix == "apal":
                    # load Artisan palettes on double-click on *.apal file
                    QTimer.singleShot(20,lambda : aw.getPalettes(filename,aw.buttonpalette))

        elif platf == "Windows" and not self.artisanviewerMode:
            msg = url.toString()  #here we don't want a local file, preserve the windows file:///
            self.sendMessage2ArtisanInstance(msg,self._viewer_id)

    @pyqtSlot(str)
    def receiveMessage(self,msg):
        url = QUrl()
        url.setUrl(msg)
        self.open_url(url)

    # to send message to main Artisan instance: id = appGuid
    # to send message to viewer:                id = viewerAppGuid
    def sendMessage2ArtisanInstance(self,message,instance_id):
        if platf == "Windows":
            try:
                if instance_id == self._viewer_id:
                    res = self._sendMessage2ArtisanInstance(message,self._viewer_id)
                elif instance_id == self._id:
                    res = self._sendMessage2ArtisanInstance(message,self._id)
                if not res:
                    # get the path of the artisan.exe file
                    if getattr(sys, 'frozen', False):
                        application_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
                        application_path += "\\artisan.exe"
                    # or the artisan py file if running from source
                    else:
                        application_path = sys.argv[0]
                    application_path = re.sub(r"\\",r"/",application_path)
                    # must start viewer without an argv else it thinks it was started from a link and sends back to artisan
                    os.startfile(application_path)  # @UndefinedVariable
                    QTimer.singleShot(3000,lambda : self._sendMessage2ArtisanInstance(message,instance_id))
            except:
                pass
        else:
            self._sendMessage2ArtisanInstance(message,instance_id)

    def _sendMessage2ArtisanInstance(self,message,instance_id):
        try:
            self._outSocket = QLocalSocket()
            self._outSocket.connectToServer(instance_id)
            self._isRunning = self._outSocket.waitForConnected(-1)
            if self.isRunning():
                self._outStream = QTextStream(self._outSocket)
                self._outStream.setCodec('UTF-8')
                return self.sendMessage(message)
            else:
                return False
        finally:
            self._outSocket = None
            self._outStream = None

    def event(self, event):
        if event.type() == QEvent.FileOpen:
            try:
                url = event.url()
                # files cannot be opend while
                # - sampling
                # - in Designer mode
                # - in Wheel graph mode
                # - while editing the cup profile
                can_open_mode = not aw.qmc.flagon and not aw.qmc.designerflag and not aw.qmc.wheelflag and aw.qmc.flavorchart_plot is None
                if can_open_mode and bool(aw.comparator):
                    # while in comparator mode with the events file already open we rather send it to another instance
                    filename = url.toString(QUrl.PreferLocalFile)
                    can_open_mode = not any(p.filepath == filename for p in aw.comparator.profiles)
                if can_open_mode:
                    self.open_url(url)
                else:
                    message = url.toString()
                    # we send open file in the other instance if running
                    if self.artisanviewerMode:
                        # this is the Viewer, but we cannot open the file, send an open request to the main app if it is running
                        self.sendMessage2ArtisanInstance(message,self._id)
                    else:
                        # try to open the file in Viewer if it is running
                        self.sendMessage2ArtisanInstance(message,self._viewer_id)
            except:
                pass
            return 1
        else:
            return super(Artisan, self).event(event)

