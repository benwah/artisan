#!/usr/bin/env python3

# ABOUT
# Artisan Autosave Dialog

# LICENSE
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later versison. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

# AUTHOR
# Marko Luther, 2020

from artisanlib.dialogs import ArtisanDialog
from help import autosave_help

from PyQt5.QtCore import Qt, pyqtSlot, QSettings
from PyQt5.QtWidgets import (QApplication, QLabel, QPushButton, QDialogButtonBox, 
    QComboBox, QHBoxLayout, QVBoxLayout, QCheckBox, QGridLayout, QLineEdit)

class autosaveDlg(ArtisanDialog):
    def __init__(self, parent = None, aw = None):
        super(autosaveDlg,self).__init__(parent, aw)
        self.setModal(True)
        self.setWindowTitle(QApplication.translate("Form Caption","Autosave", None))

        settings = QSettings()
        if settings.contains("autosaveGeometry"):
            self.restoreGeometry(settings.value("autosaveGeometry"))
        
        self.helpdialog = None

        self.prefixEdit = QLineEdit(self.aw.qmc.autosaveprefix)
        self.prefixEdit.setToolTip(QApplication.translate("Tooltip", "Automatic generated name",None))
        self.prefixEdit.textChanged.connect(self.prefixChanged)
        prefixpreviewLabel = QLabel()
        prefixpreviewLabel.setAlignment(Qt.Alignment(Qt.AlignCenter | Qt.AlignRight))
        prefixpreviewLabel.setText(QApplication.translate("Label", "Preview:",None))
        self.prefixPreview = QLabel()
        self.prefixpreviewrecordingLabel = QLabel()
        self.prefixpreviewrecordingLabel.setAlignment(Qt.Alignment(Qt.AlignCenter | Qt.AlignRight))
        self.prefixPreviewrecording = QLabel()
        self.prefixChanged()
 
        autochecklabel = QLabel(QApplication.translate("CheckBox","Autosave [a]", None))
        self.autocheckbox = QCheckBox()
        self.autocheckbox.setToolTip(QApplication.translate("Tooltip", "ON/OFF of automatic saving when pressing keyboard letter [a]",None))
        self.autocheckbox.setChecked(self.aw.qmc.autosaveflag)

        addtorecentfileslabel = QLabel(QApplication.translate("CheckBox","Add to recent file list", None))
        self.addtorecentfiles = QCheckBox()
        self.addtorecentfiles.setToolTip(QApplication.translate("Tooltip", "Add auto saved file names to the recent files list",None))
        self.addtorecentfiles.setChecked(self.aw.qmc.autosaveaddtorecentfilesflag)

        autopdflabel = QLabel(QApplication.translate("CheckBox","Save also", None))
        self.autopdfcheckbox = QCheckBox()
        self.autopdfcheckbox.setToolTip(QApplication.translate("Tooltip", "Save image alongside .alog profiles",None))
        self.autopdfcheckbox.setChecked(self.aw.qmc.autosaveimage)
        imageTypes = ["PDF", "SVG", "PNG", "JPEG", "BMP", "CSV", "JSON"]
        self.imageTypesComboBox = QComboBox()
        self.imageTypesComboBox.addItems(imageTypes)
        self.imageTypesComboBox.setCurrentIndex(imageTypes.index(self.aw.qmc.autosaveimageformat))
        prefixlabel = QLabel()
        prefixlabel.setAlignment(Qt.Alignment(Qt.AlignBottom | Qt.AlignRight))
        prefixlabel.setText(QApplication.translate("Label", "File Name Prefix",None))

        # connect the ArtisanDialog standard OK/Cancel buttons
        self.dialogbuttons.accepted.connect(self.autoChanged)
        self.dialogbuttons.rejected.connect(self.close)
        self.helpButton = self.dialogbuttons.addButton(QDialogButtonBox.Help)
        self.setButtonTranslations(self.helpButton,"Help",QApplication.translate("Button","Help", None))
        self.dialogbuttons.button(QDialogButtonBox.Help).clicked.connect(self.showautosavehelp)
        
        pathButton = QPushButton(QApplication.translate("Button","Path", None))
        pathButton.setFocusPolicy(Qt.NoFocus)
        self.pathEdit = QLineEdit(self.aw.qmc.autosavepath)
        self.pathEdit.setToolTip(QApplication.translate("Tooltip", "Sets the directory to store batch profiles when using the letter [a]",None))
        pathButton.clicked.connect(self.getpath)
        
        pathAlsoButton = QPushButton(QApplication.translate("Button","Path", None))
        pathAlsoButton.setFocusPolicy(Qt.NoFocus)
        self.pathAlsoEdit = QLineEdit(self.aw.qmc.autosavealsopath)
        self.pathAlsoEdit.setToolTip(QApplication.translate("Tooltip", "Sets the directory to store the save also files",None))
        pathAlsoButton.clicked.connect(self.getalsopath)
        
        # this intermediate layout is needed to add the 'addtorecentfiles' checkbox into the existing grid layout.
        autochecklabelplus = QHBoxLayout()
        autochecklabelplus.addWidget(autochecklabel)
        autochecklabelplus.addWidget(self.addtorecentfiles)
        autochecklabelplus.addWidget(addtorecentfileslabel)
        autochecklabelplus.addStretch()

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.dialogbuttons)
        autolayout = QGridLayout()
        autolayout.addWidget(self.autocheckbox,0,0,Qt.AlignRight)
        autolayout.addLayout(autochecklabelplus,0,1)
        autolayout.addWidget(prefixlabel,1,0)
        autolayout.addWidget(self.prefixEdit,1,1,1,2)
        autolayout.addWidget(prefixpreviewLabel,2,0)
        autolayout.addWidget(self.prefixPreview,2,1)
        autolayout.addWidget(self.prefixpreviewrecordingLabel,3,0)
        autolayout.addWidget(self.prefixPreviewrecording,3,1)
        autolayout.addWidget(pathButton,4,0)
        autolayout.addWidget(self.pathEdit,4,1,1,2)
        autolayout.addWidget(self.autopdfcheckbox,5,0,Qt.AlignRight)
        autolayout.addWidget(autopdflabel,5,1)
        autolayout.addWidget(self.imageTypesComboBox,5,2)
        autolayout.addWidget(pathAlsoButton,6,0)
        autolayout.addWidget(self.pathAlsoEdit,6,1,1,2)
        autolayout.setColumnStretch(0,0)
        autolayout.setColumnStretch(1,10)
        autolayout.setColumnStretch(2,0)
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(autolayout)
        mainLayout.addStretch()
        mainLayout.addSpacing(10)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)
        self.dialogbuttons.button(QDialogButtonBox.Ok).setFocus()
        self.setFixedHeight(self.sizeHint().height())

    @pyqtSlot(bool)
    def showautosavehelp(self,_=False):
        self.helpdialog = self.aw.showHelpDialog(
                self,            # this dialog as parent
                self.helpdialog, # the existing help dialog
                QApplication.translate("Form Caption","Autosave Fields Help",None),
                autosave_help.content())

    def closeHelp(self):
        self.aw.closeHelpDialog(self.helpdialog)

    @pyqtSlot()
    def prefixChanged(self):
        preview = self.aw.generateFilename(self.prefixEdit.text(),previewmode=2)
        self.prefixPreview.setText(preview)
        previewrecording = self.aw.generateFilename(self.prefixEdit.text(),previewmode=1)
        if previewrecording == preview:
            self.prefixpreviewrecordingLabel.setText("")
            self.prefixPreviewrecording.setText("")
        else:
            self.prefixpreviewrecordingLabel.setText(QApplication.translate("Label", "While recording:",None))
            self.prefixPreviewrecording.setText(previewrecording)

    @pyqtSlot(bool)
    def getpath(self,_):
        filename = self.aw.ArtisanExistingDirectoryDialog(msg=QApplication.translate("Form Caption","AutoSave Path", None))
        self.pathEdit.setText(filename)

    @pyqtSlot(bool)
    def getalsopath(self,_):
        filename = self.aw.ArtisanExistingDirectoryDialog(msg=QApplication.translate("Form Caption","AutoSave Save Also Path", None))
        self.pathAlsoEdit.setText(filename)

    @pyqtSlot()
    def autoChanged(self):
        self.aw.qmc.autosavepath = self.pathEdit.text()
        self.aw.qmc.autosavealsopath = self.pathAlsoEdit.text()
        if self.autocheckbox.isChecked():
            self.aw.qmc.autosaveflag = 1
            self.aw.qmc.autosaveprefix = self.prefixEdit.text()
            message = QApplication.translate("Message","Autosave ON. Prefix: {0}").format(self.prefixEdit.text())
            self.aw.sendmessage(message)
        else:
            self.aw.qmc.autosaveflag = 0
            self.aw.qmc.autosaveprefix = self.prefixEdit.text()
            message = QApplication.translate("Message","Autosave OFF. Prefix: {0}").format(self.prefixEdit.text())
            self.aw.sendmessage(message)
        self.aw.qmc.autosaveimage = self.autopdfcheckbox.isChecked()
        self.aw.qmc.autosaveimageformat = self.imageTypesComboBox.currentText()
        self.aw.qmc.autosaveaddtorecentfilesflag = self.addtorecentfiles.isChecked()
        self.aw.closeEventSettings()
        self.close()

    @pyqtSlot()
    def closeEvent(self, _):
        self.closeHelp()
        settings = QSettings()
        #save window geometry
        settings.setValue("autosaveGeometry",self.saveGeometry())


