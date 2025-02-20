#!/usr/bin/env python3

# ABOUT
# Artisan Curves Dialog

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

##########################################################################
#####################     EXTRAS/HUD  EDIT DLG     #######################
##########################################################################

import sys
import platform
import numpy
import prettytable

from artisanlib.util import (deltaLabelBigPrefix, deltaLabelPrefix, deltaLabelUTF8, 
                             stringtoseconds, stringfromseconds, toFloat)
from artisanlib.dialogs import ArtisanDialog
from artisanlib.widgets import MyQDoubleSpinBox
from help import symbolic_help

from PyQt5.QtCore import (Qt, pyqtSlot, QSettings, QCoreApplication, QRegularExpression)
from PyQt5.QtGui import (QColor, QIntValidator, QRegularExpressionValidator, QPixmap)
from PyQt5.QtWidgets import (QApplication, QWidget, QCheckBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QSpinBox, QTabWidget, QComboBox, QDialogButtonBox, QGridLayout,
                             QGroupBox, QLayout, QMessageBox, QRadioButton, QStyleFactory, QHeaderView,
                             QTableWidget, QTableWidgetItem)


########################################################################################
#####################  PLOTTER DATA DLG  ###############################################
########################################################################################

        
class equDataDlg(ArtisanDialog):
    def __init__(self, parent = None, aw = None):
        super(equDataDlg,self).__init__(parent, aw)
        self.setWindowTitle(QApplication.translate("Form Caption","Plotter Data",None))
        self.setModal(True)

        self.datalabel = QLabel("")
        self.dataprecisionlabel = QLabel(QApplication.translate("Label", "Data precision",None))
        
        #DATA Table
        self.datatable = QTableWidget()
        self.datatable.setTabKeyNavigation(True)
        header = self.datatable.horizontalHeader()
        header.setStretchLastSection(True)
        self.datatable.setMinimumSize(self.datatable.minimumSizeHint())

        self.copydataTableButton = QPushButton(QApplication.translate("Button", "Copy Table",None))
        self.copydataTableButton.setToolTip(QApplication.translate("Tooltip","Copy table to clipboard, OPTION or ALT click for tabular text",None))
        self.copydataTableButton.setFocusPolicy(Qt.NoFocus)
        self.copydataTableButton.setMaximumSize(self.copydataTableButton.sizeHint())
        self.copydataTableButton.setMinimumSize(self.copydataTableButton.minimumSizeHint())
        self.copydataTableButton.clicked.connect(self.copyDataTabletoClipboard)

        self.dataprecision = ["%.1f","%.2f","%.3f","%.4f","%.5f","%.6f"]
        self.dataprecisionval = 1
        self.precisionSpinBox = QSpinBox()
        self.precisionSpinBox.setRange(1,6)
        self.precisionSpinBox.setSingleStep(1)
        self.precisionSpinBox.setValue(self.dataprecisionval)
        self.precisionSpinBox.setAlignment(Qt.AlignLeft)
        self.precisionSpinBox.setMaximumWidth(50)
        self.precisionSpinBox.valueChanged.connect(self.changeprecision)

        self.changeprecision()
        self.createDataTable()

        #layout
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.copydataTableButton)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.dataprecisionlabel)
        buttonLayout.addWidget(self.precisionSpinBox)

        dataplotterLayout = QVBoxLayout()
        dataplotterLayout.addWidget(self.datalabel)
        dataplotterLayout.addWidget(self.datatable)
        dataplotterLayout.addLayout(buttonLayout)
        
        self.setLayout(dataplotterLayout)

    def changeprecision(self):
        self.dataprecisionval = int(self.precisionSpinBox.value())-1
        self.createDataTable()

    def createDataTable(self):
        try:
            self.datatable.clear()
            ndata = len(self.aw.qmc.timex)
            self.datatable.setRowCount(ndata)
            
            mm = "" 
            for i in range(len(self.aw.qmc.plotterequationresults)):
                if len(self.aw.qmc.plotterequationresults[i]):
                    mm += "P"+str(i+1)+" "
                    #ite = len(self.aw.qmc.plotterequationresults[i])
            if not mm:
                self.datalabel.setText(QApplication.translate("Label","No plotter data found.",None))
            else:
                self.datalabel.setText(mm)

            columns = [ QApplication.translate("Table", "t",None),
                        QApplication.translate("Table", "Time",None),
                        QApplication.translate("Table", "P1",None),
                        QApplication.translate("Table", "P2",None),
                        QApplication.translate("Table", "P3",None),
                        QApplication.translate("Table", "P4",None),
                        QApplication.translate("Table", "P5",None),
                        QApplication.translate("Table", "P6",None),
                        QApplication.translate("Table", "P7",None),
                        QApplication.translate("Table", "P8",None),
                        QApplication.translate("Table", "P9",None),
                        ""]
    
            self.datatable.setColumnCount(len(columns))
            self.datatable.setHorizontalHeaderLabels(columns)
            self.datatable.setAlternatingRowColors(True)
            self.datatable.setEditTriggers(QTableWidget.NoEditTriggers)
            self.datatable.setSelectionBehavior(QTableWidget.SelectRows)
            self.datatable.setSelectionMode(QTableWidget.SingleSelection)
            self.datatable.setShowGrid(True)
            self.datatable.verticalHeader().setSectionResizeMode(2)
            
            for i in range(ndata):
    
                t = QTableWidgetItem(self.dataprecision[self.dataprecisionval]%self.aw.qmc.timex[i])
                t.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                
                time = QTableWidgetItem(stringfromseconds(self.aw.qmc.timex[i]-self.aw.qmc.timex[self.aw.qmc.timeindex[0]]))
                time.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
    
                if len(self.aw.qmc.plotterequationresults[0]) and len(self.aw.qmc.plotterequationresults[0]) > i:
                    P1 = QTableWidgetItem(self.dataprecision[self.dataprecisionval]%self.aw.qmc.plotterequationresults[0][i])
                else:
                    P1 = QTableWidgetItem("NA")
                    P1.setBackground(QColor('lightgrey'))
                if len(self.aw.qmc.plotterequationresults[1]) and len(self.aw.qmc.plotterequationresults[1]) > i:
                    P2 = QTableWidgetItem(self.dataprecision[self.dataprecisionval]%self.aw.qmc.plotterequationresults[1][i])
                else:
                    P2 = QTableWidgetItem("NA")
                    P2.setBackground(QColor('lightgrey'))
                if len(self.aw.qmc.plotterequationresults[2]) and len(self.aw.qmc.plotterequationresults[2]) > i:
                    P3 = QTableWidgetItem(self.dataprecision[self.dataprecisionval]%self.aw.qmc.plotterequationresults[2][i])
                else:
                    P3 = QTableWidgetItem("NA")
                    P3.setBackground(QColor('lightgrey'))
                if len(self.aw.qmc.plotterequationresults[3]) and len(self.aw.qmc.plotterequationresults[3]) > i:
                    P4 = QTableWidgetItem(self.dataprecision[self.dataprecisionval]%self.aw.qmc.plotterequationresults[3][i])
                else:
                    P4 = QTableWidgetItem("NA")
                    P4.setBackground(QColor('lightgrey'))
                if len(self.aw.qmc.plotterequationresults[4]) and len(self.aw.qmc.plotterequationresults[4]) > i:
                    P5 = QTableWidgetItem(self.dataprecision[self.dataprecisionval]%self.aw.qmc.plotterequationresults[4][i])
                else:
                    P5 = QTableWidgetItem("NA")
                    P5.setBackground(QColor('lightgrey'))
                if len(self.aw.qmc.plotterequationresults[5]) and len(self.aw.qmc.plotterequationresults[5]) > i:
                    P6 = QTableWidgetItem(self.dataprecision[self.dataprecisionval]%self.aw.qmc.plotterequationresults[5][i])
                else:
                    P6 = QTableWidgetItem("NA")
                    P6.setBackground(QColor('lightgrey'))
                if len(self.aw.qmc.plotterequationresults[6]) and len(self.aw.qmc.plotterequationresults[6]) > i:
                    P7 = QTableWidgetItem(self.dataprecision[self.dataprecisionval]%self.aw.qmc.plotterequationresults[6][i])
                else:
                    P7 = QTableWidgetItem("NA")
                    P7.setBackground(QColor('lightgrey'))
                if len(self.aw.qmc.plotterequationresults[7]) and len(self.aw.qmc.plotterequationresults[7]) > i:
                    P8 = QTableWidgetItem(self.dataprecision[self.dataprecisionval]%self.aw.qmc.plotterequationresults[7][i])
                else:
                    P8 = QTableWidgetItem("NA")
                    P8.setBackground(QColor('lightgrey'))
                if len(self.aw.qmc.plotterequationresults[8]) and len(self.aw.qmc.plotterequationresults[8]) > i:
                    P9 = QTableWidgetItem(self.dataprecision[self.dataprecisionval]%self.aw.qmc.plotterequationresults[8][i])
                else:
                    P9 = QTableWidgetItem("NA")
                    P9.setBackground(QColor('lightgrey'))
                                    
                P1.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                P2.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                P3.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                P4.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                P5.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                P6.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                P7.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                P8.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                P9.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
    
                self.datatable.setItem(i,0,t)
                self.datatable.setItem(i,1,time)
                self.datatable.setItem(i,2,P1)
                self.datatable.setItem(i,3,P2)
                self.datatable.setItem(i,4,P3)
                self.datatable.setItem(i,5,P4)
                self.datatable.setItem(i,6,P5)
                self.datatable.setItem(i,7,P6)
                self.datatable.setItem(i,8,P7)
                self.datatable.setItem(i,9,P8)
                self.datatable.setItem(i,10,P9)
    
            header = self.datatable.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Fixed)
            header.setSectionResizeMode(1, QHeaderView.Fixed)
            header.setSectionResizeMode(2, QHeaderView.Fixed)
            header.setSectionResizeMode(3, QHeaderView.Fixed)
            header.setSectionResizeMode(4, QHeaderView.Fixed)
            header.setSectionResizeMode(len(columns) - 1, QHeaderView.Stretch)
            self.datatable.resizeColumnsToContents()
        except:
#            import traceback
#            traceback.print_exc(file=sys.stdout)
            pass
            
    @pyqtSlot(bool)
    def copyDataTabletoClipboard(self,_=False):
        nrows = self.datatable.rowCount() 
        ncols = self.datatable.columnCount() - 1 #there is a dummy column at the end on the right
        clipboard = ""
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.AltModifier:  #alt click
            tbl = prettytable.PrettyTable()
            fields = []
            for c in range(ncols):
                fields.append(self.datatable.horizontalHeaderItem(c).text())
            tbl.field_names = fields
            for r in range(nrows):
                rows = []
                for c in range(ncols):
                    rows.append(self.datatable.item(r,c).text())
                tbl.add_row(rows)
            clipboard = tbl.get_string()
        else:
            for c in range(ncols):
                clipboard += self.datatable.horizontalHeaderItem(c).text()
                if c != (ncols-1):
                    clipboard += '\t'
            clipboard += '\n'
            for r in range(nrows):
                for c in range(ncols):
                    clipboard += self.datatable.item(r,c).text()
                    if c != (ncols-1):
                        clipboard += '\t'
                clipboard += '\n'
        # copy to the system clipboard
        sys_clip = QApplication.clipboard()
        sys_clip.setText(clipboard)
        self.aw.sendmessage(QApplication.translate("Message","Data table copied to clipboard",None))



class HUDDlg(ArtisanDialog):
    def __init__(self, parent = None, aw = None, activeTab = 0):
        super(HUDDlg,self).__init__(parent, aw)
        
        self.app = QCoreApplication.instance()
        
        self.setWindowTitle(QApplication.translate("Form Caption","Curves", None))
        self.setModal(True)

        self.helpdialog = None

        # keep old values to be restored on Cancel
        self.org_DeltaET = self.aw.qmc.DeltaETflag
        self.org_DeltaBT = self.aw.qmc.DeltaBTflag
        self.org_DeltaETlcd = self.aw.qmc.DeltaETlcdflag
        self.org_DeltaBTlcd = self.aw.qmc.DeltaBTlcdflag
        self.org_Projection = self.aw.qmc.projectFlag
        self.org_patheffects = self.aw.qmc.patheffects
        self.org_graphstyle = self.aw.qmc.graphstyle
        self.org_graphfont = self.aw.qmc.graphfont
        self.org_HUDbuttonflag = self.aw.qmc.HUDbuttonflag
        self.org_filterDropOuts = self.aw.qmc.filterDropOuts
        self.org_dropSpikes = self.aw.qmc.dropSpikes
        self.org_dropDuplicates = self.aw.qmc.dropDuplicates
        self.org_dropDuplicatesLimit = self.aw.qmc.dropDuplicatesLimit
        self.org_swapETBT = self.aw.qmc.swapETBT
        self.org_optimalSmoothing = self.aw.qmc.optimalSmoothing
        self.org_polyfitRoRcalc = self.aw.qmc.polyfitRoRcalc
        self.org_soundflag = self.aw.soundflag
        self.org_logoimgflag = self.aw.logoimgflag
        self.org_logoimgalpha = self.aw.logoimgalpha
        self.org_curvefilter = self.aw.qmc.curvefilter
        self.org_deltaETfilter = self.aw.qmc.deltaETfilter
        self.org_deltaBTfilter = self.aw.qmc.deltaBTfilter
        self.org_deltaBTspan = self.aw.qmc.deltaBTspan
        self.org_deltaETspan = self.aw.qmc.deltaETspan
        self.org_graphstyle = self.aw.qmc.graphstyle
        self.org_ETname = self.aw.ETname
        self.org_BTname = self.aw.BTname
        self.org_foregroundShowFullflag = self.aw.qmc.foregroundShowFullflag
        
        self.showHUDbutton = QCheckBox(QApplication.translate("Label", "HUD Button", None))
        self.showHUDbutton.setChecked(self.aw.qmc.HUDbuttonflag)
        self.showHUDbutton.setFocusPolicy(Qt.NoFocus)
        self.showHUDbutton.stateChanged.connect(self.showHUDbuttonToggle)
        ETLabel = QLabel(QApplication.translate("Label", "ET Target 1",None))
        ETLabel.setAlignment(Qt.AlignRight)
        BTLabel = QLabel(QApplication.translate("Label", "BT Target 1",None))
        BTLabel.setAlignment(Qt.AlignRight)        
        ET2Label = QLabel(QApplication.translate("Label", "ET Target 2",None))
        ET2Label.setAlignment(Qt.AlignRight)
        BT2Label = QLabel(QApplication.translate("Label", "BT Target 2",None))
        BT2Label.setAlignment(Qt.AlignRight)        
        modeLabel = QLabel(QApplication.translate("Label", "Mode",None))
        modeLabel.setAlignment(Qt.AlignRight)
        ETPIDLabel = QLabel(QApplication.translate("Label", "ET p-i-d 1",None))
        #delta ET
        self.DeltaET = QCheckBox()
        self.DeltaET.setFocusPolicy(Qt.NoFocus)
        self.DeltaET.setChecked(self.aw.qmc.DeltaETflag)
        DeltaETlabel = QLabel(deltaLabelUTF8 + QApplication.translate("Label", "ET",None))
        #delta BT
        self.DeltaBT = QCheckBox()
        self.DeltaBT.setFocusPolicy(Qt.NoFocus)
        self.DeltaBT.setChecked(self.aw.qmc.DeltaBTflag)
        DeltaBTlabel = QLabel(deltaLabelUTF8 + QApplication.translate("Label", "BT",None))
        filterlabel = QLabel(QApplication.translate("Label", "Smoothing",None))
        #DeltaFilter holds the number of pads in filter
        self.DeltaETfilter = QSpinBox()
        self.DeltaETfilter.setSingleStep(1)
        self.DeltaETfilter.setRange(0,40)
        self.DeltaETfilter.setAlignment(Qt.AlignRight)
        self.DeltaETfilter.setValue(self.aw.qmc.deltaETfilter/2)
        self.DeltaETfilter.editingFinished.connect(self.changeDeltaETfilter)
        self.DeltaBTfilter = QSpinBox()
        self.DeltaBTfilter.setSingleStep(1)
        self.DeltaBTfilter.setRange(0,40)
        self.DeltaBTfilter.setAlignment(Qt.AlignRight)
        self.DeltaBTfilter.setValue(self.aw.qmc.deltaBTfilter/2)
        self.DeltaBTfilter.editingFinished.connect(self.changeDeltaBTfilter)

        self.OptimalSmoothingFlag = QCheckBox(QApplication.translate("CheckBox", "Optimal Smoothing Post Roast",None))
        self.OptimalSmoothingFlag.setToolTip(QApplication.translate("Tooltip", "Use an optimal smoothing algorithm (only applicable offline, after recording)", None))        
        self.OptimalSmoothingFlag.setChecked(self.aw.qmc.polyfitRoRcalc and self.aw.qmc.optimalSmoothing)
        self.OptimalSmoothingFlag.stateChanged.connect(self.changeOptimalSmoothingFlag)
        self.OptimalSmoothingFlag.setEnabled(self.aw.qmc.polyfitRoRcalc)

        self.PolyFitFlag = QCheckBox(QApplication.translate("CheckBox", "Polyfit computation",None))
        self.PolyFitFlag.setToolTip(QApplication.translate("Tooltip", "Compute the rate-of-rise over the delta span interval by a linear polyfit", None))        
        self.PolyFitFlag.setChecked(self.aw.qmc.polyfitRoRcalc)
        self.PolyFitFlag.stateChanged.connect(self.changePolyFitFlagFlag)
        
        curvefilterlabel = QLabel(QApplication.translate("Label", "Smooth Curves",None))
        #Filter holds the number of pads in filter
        self.Filter = QSpinBox()
        self.Filter.setSingleStep(1)
        self.Filter.setRange(0,40)
        self.Filter.setAlignment(Qt.AlignRight)
        self.Filter.setValue(self.aw.qmc.curvefilter/2)
        self.Filter.editingFinished.connect(self.changeFilter)
        #filterspikes
        self.FilterSpikes = QCheckBox(QApplication.translate("CheckBox", "Smooth Spikes",None))
        self.FilterSpikes.setChecked(self.aw.qmc.filterDropOuts)
        self.FilterSpikes.stateChanged.connect(self.changeDropFilter)
        self.FilterSpikes.setFocusPolicy(Qt.NoFocus)
        #dropduplicates
        self.DropDuplicates = QCheckBox(QApplication.translate("CheckBox", "Interpolate Duplicates",None))
        self.DropDuplicates.setChecked(self.aw.qmc.dropDuplicates)
        self.DropDuplicates.stateChanged.connect(self.changeDuplicatesFilter)
        self.DropDuplicates.setFocusPolicy(Qt.NoFocus)
        self.DropDuplicatesLimit = MyQDoubleSpinBox()
        self.DropDuplicatesLimit.setDecimals(2)
        self.DropDuplicatesLimit.setSingleStep(0.1)
        self.DropDuplicatesLimit.setRange(0.,1.)
        self.DropDuplicatesLimit.setAlignment(Qt.AlignRight)
        self.DropDuplicatesLimit.setMinimumWidth(30)
        self.DropDuplicatesLimit.setValue(self.aw.qmc.dropDuplicatesLimit)
        if self.aw.qmc.mode == "F":
            self.DropDuplicatesLimit.setSuffix(" F")
        elif self.aw.qmc.mode == "C":
            self.DropDuplicatesLimit.setSuffix(" C")

        #show full
        self.ShowFull = QCheckBox(QApplication.translate("CheckBox", "Show Full",None))
        self.ShowFull.setChecked(self.aw.qmc.foregroundShowFullflag)
        self.ShowFull.stateChanged.connect(self.changeShowFullFilter)
        self.ShowFull.setFocusPolicy(Qt.NoFocus)
        
        #dropspikes
        self.DropSpikes = QCheckBox(QApplication.translate("CheckBox", "Drop Spikes",None))
        self.DropSpikes.setChecked(self.aw.qmc.dropSpikes)
        self.DropSpikes.stateChanged.connect(self.changeSpikeFilter)
        self.DropSpikes.setFocusPolicy(Qt.NoFocus)
        #min-max-limits
        self.MinMaxLimits = QCheckBox(QApplication.translate("CheckBox", "Limits",None))
        self.MinMaxLimits.setChecked(self.aw.qmc.minmaxLimits)
        self.MinMaxLimits.stateChanged.connect(self.changeMinMaxLimits)
        self.MinMaxLimits.setFocusPolicy(Qt.NoFocus)
        #swapETBT flag
        self.swapETBT = QCheckBox(QApplication.translate("Label", "ET", None) + " <-> " + QApplication.translate("Label", "BT", None))
        self.swapETBT.setChecked(self.aw.qmc.swapETBT)
        self.swapETBT.setFocusPolicy(Qt.NoFocus)
        self.swapETBT.stateChanged.connect(self.changeSwapETBT)
        #limits
        minlabel = QLabel(QApplication.translate("Label", "min","abbrev of minimum"))
        maxlabel = QLabel(QApplication.translate("Label", "max",None))
        self.minLimit = QSpinBox()
        self.minLimit.setRange(0,1000)    #(min,max)
        self.minLimit.setAlignment(Qt.AlignRight)
        self.minLimit.setMinimumWidth(80)
        self.minLimit.setValue(self.aw.qmc.filterDropOut_tmin)
        self.maxLimit = QSpinBox()
        self.maxLimit.setRange(0,1000)
        self.maxLimit.setAlignment(Qt.AlignRight)
        self.maxLimit.setMinimumWidth(80)
        self.maxLimit.setValue(self.aw.qmc.filterDropOut_tmax)
        #show projection
        self.projectCheck = QCheckBox(QApplication.translate("CheckBox", "Projection",None))
        self.projectionmodeComboBox = QComboBox()
        self.projectionmodeComboBox.addItems([QApplication.translate("ComboBox","linear",None),
                                              QApplication.translate("ComboBox","newton",None)])
        self.projectionmodeComboBox.setCurrentIndex(self.aw.qmc.projectionmode)
        self.projectionmodeComboBox.currentIndexChanged.connect(self.changeProjectionMode)
        self.projectCheck.setChecked(self.aw.qmc.projectFlag)
        self.DeltaET.stateChanged.connect(self.changeDeltaET)         #toggle
        self.DeltaBT.stateChanged.connect(self.changeDeltaBT)         #toggle
        self.projectCheck.stateChanged.connect(self.changeProjection) #toggle
        
        deltaSpanLabel = QLabel(QApplication.translate("Label", "Delta Span",None))
        self.spanitems = range(1,31)
        self.deltaBTspan = QComboBox()
        self.deltaBTspan.addItems([str(i) + "s" for i in self.spanitems])
        try:
            self.deltaBTspan.setCurrentIndex(self.spanitems.index(self.aw.qmc.deltaBTspan))
        except Exception:
            pass
        self.deltaBTspan.currentIndexChanged.connect(self.changeDeltaBTspan)  #toggle
        self.deltaETspan = QComboBox()
        self.deltaETspan.addItems([str(i) + "s" for i in self.spanitems])
        try:
            self.deltaETspan.setCurrentIndex(self.spanitems.index(self.aw.qmc.deltaETspan))
        except Exception:
            pass
        self.deltaETspan.currentIndexChanged.connect(self.changeDeltaETspan)  #toggle

        self.modeComboBox = QComboBox()
        self.modeComboBox.setMaximumWidth(100)
        self.modeComboBox.setMinimumWidth(55)
        self.modeComboBox.addItems([QApplication.translate("ComboBox","metrics",None),
                                    QApplication.translate("ComboBox","thermal",None)])
        self.modeComboBox.setCurrentIndex(self.aw.HUDfunction)
        self.ETlineEdit = QLineEdit(str(self.aw.qmc.ETtarget))
        self.ETlineEdit.setAlignment(Qt.AlignRight)
        self.BTlineEdit = QLineEdit(str(self.aw.qmc.BTtarget))
        self.BTlineEdit.setAlignment(Qt.AlignRight)
        self.ETlineEdit.setValidator(QIntValidator(0, 1000, self.ETlineEdit))
        self.BTlineEdit.setValidator(QIntValidator(0, 1000, self.BTlineEdit))
        self.ETlineEdit.setMaximumWidth(60)
        self.BTlineEdit.setMaximumWidth(60)
        self.ET2lineEdit = QLineEdit(str(self.aw.qmc.ET2target))
        self.ET2lineEdit.setAlignment(Qt.AlignRight)
        self.BT2lineEdit = QLineEdit(str(self.aw.qmc.BT2target))
        self.BT2lineEdit.setAlignment(Qt.AlignRight)
        self.ET2lineEdit.setValidator(QIntValidator(0, 1000, self.ET2lineEdit))
        self.BT2lineEdit.setValidator(QIntValidator(0, 1000, self.BT2lineEdit))
        self.ET2lineEdit.setMaximumWidth(60)
        self.BT2lineEdit.setMaximumWidth(60)
        self.ETpidP = QLineEdit(str(self.aw.qmc.hudETpid[0]))
        self.ETpidP.setAlignment(Qt.AlignRight)
        self.ETpidI = QLineEdit(str(self.aw.qmc.hudETpid[1]))
        self.ETpidI.setAlignment(Qt.AlignRight)
        self.ETpidD = QLineEdit(str(self.aw.qmc.hudETpid[2]))
        self.ETpidD.setAlignment(Qt.AlignRight)
        self.ETpidP.setValidator(QIntValidator(0, 1000, self.ETpidP))
        self.ETpidI.setValidator(QIntValidator(0, 1000, self.ETpidI))
        self.ETpidD.setValidator(QIntValidator(0, 1000, self.ETpidD))
        self.ETpidP.setMaximumWidth(60)
        self.ETpidI.setMaximumWidth(60)
        self.ETpidD.setMaximumWidth(60)

        # connect the ArtisanDialog standard OK/Cancel buttons
        self.dialogbuttons.accepted.connect(self.updatetargets)
        self.dialogbuttons.rejected.connect(self.close)

        hudLayout = QGridLayout()
        hudLayout.addWidget(BTLabel,0,0)
        hudLayout.addWidget(self.BTlineEdit,0,1)
        hudLayout.addWidget(BT2Label,0,2)
        hudLayout.addWidget(self.BT2lineEdit,0,3)
        hudLayout.addWidget(ETLabel,1,0)
        hudLayout.addWidget(self.ETlineEdit,1,1)
        hudLayout.addWidget(ET2Label,1,2)
        hudLayout.addWidget(self.ET2lineEdit,1,3)
        hudLayout.addWidget(ETPIDLabel,2,0)
        hudLayout.addWidget(self.ETpidP,2,1)
        hudLayout.addWidget(self.ETpidI,2,2)
        hudLayout.addWidget(self.ETpidD,2,3)
        hudLayout.addWidget(modeLabel,3,0)
        hudLayout.addWidget(self.modeComboBox,3,1)
        hudLayout.addWidget(self.showHUDbutton,3,3)
        rorBoxLayout = QHBoxLayout()
        rorBoxLayout.addWidget(self.DeltaET)
        rorBoxLayout.addWidget(DeltaETlabel)
        rorBoxLayout.addSpacing(15)
        rorBoxLayout.addWidget(self.DeltaBT)
        rorBoxLayout.addWidget(DeltaBTlabel)
        rorBoxLayout.addStretch()
        rorBoxLayout.addWidget(self.projectCheck)
        rorBoxLayout.addWidget(self.projectionmodeComboBox)
        self.DeltaETlcd = QCheckBox()
        self.DeltaETlcd.setFocusPolicy(Qt.NoFocus)
        self.DeltaETlcd.setChecked(self.aw.qmc.DeltaETlcdflag)
        DeltaETlcdLabel = QLabel(deltaLabelPrefix + QApplication.translate("Label", "ET",None))
        self.DeltaBTlcd = QCheckBox()
        self.DeltaBTlcd.setFocusPolicy(Qt.NoFocus)
        self.DeltaBTlcd.setChecked(self.aw.qmc.DeltaBTlcdflag)
        self.swapdeltalcds = QCheckBox(QApplication.translate("CheckBox", "Swap",None))
        self.swapdeltalcds.setChecked(self.aw.qmc.swapdeltalcds)
        DeltaBTlcdLabel = QLabel(deltaLabelPrefix + QApplication.translate("Label", "BT",None))
        self.DecimalPlaceslcd = QCheckBox(QApplication.translate("CheckBox", "Decimal Places",None))
        self.DecimalPlaceslcd.setChecked(self.aw.qmc.LCDdecimalplaces)
        self.DeltaETlcd.stateChanged.connect(self.changeDeltaETlcd)         #toggle
        self.DeltaBTlcd.stateChanged.connect(self.changeDeltaBTlcd)         #toggle
        lcdsLayout = QHBoxLayout()
        lcdsLayout.addWidget(self.DeltaETlcd)
        lcdsLayout.addWidget(DeltaETlcdLabel)
        lcdsLayout.addSpacing(15)
        lcdsLayout.addWidget(self.DeltaBTlcd)
        lcdsLayout.addWidget(DeltaBTlcdLabel)
        lcdsLayout.addStretch()
        lcdsLayout.addWidget(self.swapdeltalcds)
        DeltaETfilterLabel = QLabel(deltaLabelUTF8 + QApplication.translate("Label", "ET",None))
        DeltaBTfilterLabel = QLabel(deltaLabelUTF8 + QApplication.translate("Label", "BT",None))
        sensitivityGrid = QGridLayout()
        sensitivityGrid.addWidget(DeltaETfilterLabel,0,1,Qt.AlignHCenter)
        sensitivityGrid.addWidget(DeltaBTfilterLabel,0,2,Qt.AlignHCenter)
        sensitivityGrid.addWidget(deltaSpanLabel,1,0)
        sensitivityGrid.addWidget(self.deltaETspan,1,1)
        sensitivityGrid.addWidget(self.deltaBTspan,1,2)
        sensitivityGrid.addWidget(filterlabel,2,0)
        sensitivityGrid.addWidget(self.DeltaETfilter,2,1)
        sensitivityGrid.addWidget(self.DeltaBTfilter,2,2)
        sensitivityLayout = QHBoxLayout()
        sensitivityLayout.addStretch()
        sensitivityLayout.addLayout(sensitivityGrid)
        sensitivityLayout.addStretch()
        
        spikesLayout = QHBoxLayout()
        spikesLayout.addWidget(curvefilterlabel)
        spikesLayout.addWidget(self.Filter)
        spikesLayout.addStretch()
        spikesLayout2 = QVBoxLayout()
        spikesLayout2.addLayout(spikesLayout)
        spikesLayout2.addWidget(self.FilterSpikes)
        rorGroupLayout = QGroupBox(QApplication.translate("GroupBox","Rate of Rise Curves",None))
        rorGroupLayout.setLayout(rorBoxLayout)
        rorLCDGroupLayout = QGroupBox(QApplication.translate("GroupBox","Rate of Rise LCDs",None))
        rorLCDGroupLayout.setLayout(lcdsLayout)
        
        
        labelETDeltaFormula = QLabel(deltaLabelUTF8 + QApplication.translate("Label", "ET Y(x)",None))
        labelBTDeltaFormula = QLabel(deltaLabelUTF8 + QApplication.translate("Label", "BT Y(x)",None))
        self.DeltaETfunctionedit = QLineEdit(str(self.aw.qmc.DeltaETfunction))
        self.DeltaBTfunctionedit = QLineEdit(str(self.aw.qmc.DeltaBTfunction))
        
        rorSymbolicFormulaLabelsLayout = QHBoxLayout()
        rorSymbolicFormulaLabelsLayout.addWidget(labelETDeltaFormula)
        rorSymbolicFormulaLabelsLayout.addWidget(labelBTDeltaFormula)
        rorSymbolicFormulaLayout = QHBoxLayout()
        rorSymbolicFormulaLayout.addWidget(self.DeltaETfunctionedit)
        rorSymbolicFormulaLayout.addWidget(self.DeltaBTfunctionedit)
        rorSymbolicFormulas = QVBoxLayout()
        rorSymbolicFormulas.addLayout(rorSymbolicFormulaLabelsLayout)
        rorSymbolicFormulas.addLayout(rorSymbolicFormulaLayout)
        
        rorSymbolicFormulaGroupLayout = QGroupBox(QApplication.translate("GroupBox","Rate of Rise Symbolic Assignments",None))
        rorSymbolicFormulaGroupLayout.setLayout(rorSymbolicFormulas)
        
        hudHBox = QHBoxLayout()
        hudHBox.addStretch()
        hudHBox.addLayout(hudLayout)
        hudHBox.addStretch()
        hudGroupLayout = QGroupBox(QApplication.translate("GroupBox","Head Up Display",None))
        hudGroupLayout.setLayout(hudHBox)  
        if self.app.artisanviewerMode:
            hudGroupLayout.setEnabled(False)
        rorRoRAlgo = QHBoxLayout()
        rorRoRAlgo.addWidget(self.PolyFitFlag) 
        rorRoRAlgo.addSpacing(20)
        rorRoRAlgo.addWidget(self.OptimalSmoothingFlag)
        rorRoRAlgo.addStretch()   
        inputFilter0 = QHBoxLayout()
        inputFilter0.addWidget(self.DropDuplicates)
        inputFilter0.addWidget(self.DropDuplicatesLimit)
        inputFilter0.addStretch()
        inputFilter1 = QHBoxLayout()
        inputFilter1.addWidget(self.DropSpikes)
        inputFilter1.addStretch()
        inputFilter1.addWidget(self.swapETBT)
        inputFilter2 = QHBoxLayout()
        inputFilter2.addWidget(self.MinMaxLimits)
        inputFilter2.addStretch()
        inputFilter2.addWidget(minlabel)
        inputFilter2.addWidget(self.minLimit)
        inputFilter2.addSpacing(20)
        inputFilter2.addWidget(maxlabel)
        inputFilter2.addWidget(self.maxLimit)
        
        inputFilterVBox = QVBoxLayout()
        inputFilterVBox.addLayout(inputFilter0)
        inputFilterVBox.addLayout(inputFilter1)
        inputFilterVBox.addLayout(inputFilter2) 
        inputFilterGroupLayout = QGroupBox(QApplication.translate("GroupBox","Input Filter",None))
        inputFilterGroupLayout.setLayout(inputFilterVBox)
        # Post Roast Group
        postRoastVBox = QVBoxLayout()
        postRoastVBox.addLayout(spikesLayout2)
        postRoastGroupLayout = QGroupBox(QApplication.translate("GroupBox","Curve Filter",None))
        postRoastGroupLayout.setLayout(postRoastVBox)
        
        # Render xGroup
        renderVBox = QVBoxLayout()
        renderVBox.addWidget(self.ShowFull)
        renderGroupLayout = QGroupBox(QApplication.translate("GroupBox","Display Filter",None))
        renderGroupLayout.setLayout(renderVBox)    
        
        #swapETBT flag
        self.rorFilter = QCheckBox(QApplication.translate("CheckBox", "Limits",None))
        self.rorFilter.setChecked(self.aw.qmc.RoRlimitFlag)
        self.rorFilter.setFocusPolicy(Qt.NoFocus)
        rorminlabel = QLabel(QApplication.translate("Label", "min","abbrev of minimum"))
        rormaxlabel = QLabel(QApplication.translate("Label", "max",None))
        self.rorminLimit = QSpinBox()
        self.rorminLimit.setRange(-999,999)    #(min,max)
        self.rorminLimit.setAlignment(Qt.AlignRight)
        self.rorminLimit.setMinimumWidth(80)
        self.rorminLimit.setValue(self.aw.qmc.RoRlimitm)
        self.rormaxLimit = QSpinBox()
        self.rormaxLimit.setRange(-999,999)
        self.rormaxLimit.setAlignment(Qt.AlignRight)
        self.rormaxLimit.setMinimumWidth(80)
        self.rormaxLimit.setValue(self.aw.qmc.RoRlimit)
        if self.aw.qmc.mode == "F":
            self.rorminLimit.setSuffix(" F/min")
            self.rormaxLimit.setSuffix(" F/min")
        elif self.aw.qmc.mode == "C":
            self.rorminLimit.setSuffix(" C/min")
            self.rormaxLimit.setSuffix(" C/min")
        rorFilterHBox = QHBoxLayout()
        rorFilterHBox.addWidget(self.rorFilter)
        rorFilterHBox.addStretch()
        rorFilterHBox.addWidget(rorminlabel)
        rorFilterHBox.addWidget(self.rorminLimit)
        rorFilterHBox.addSpacing(20)
        rorFilterHBox.addWidget(rormaxlabel)
        rorFilterHBox.addWidget(self.rormaxLimit)
        rorFilterVBox = QVBoxLayout()
        rorFilterVBox.addLayout(sensitivityLayout)
        rorFilterVBox.addLayout(rorRoRAlgo)  
        rorFilterVBox.addLayout(rorFilterHBox)
        rorFilterGroupLayout = QGroupBox(QApplication.translate("GroupBox","Rate of Rise Filter",None))
        rorFilterGroupLayout.setLayout(rorFilterVBox)
        # path effects
        effectslabel = QLabel(QApplication.translate("Label", "Path Effects",None))
        self.PathEffects = QSpinBox()
        self.PathEffects.setSingleStep(1)
        self.PathEffects.setRange(0,5)
        self.PathEffects.setAlignment(Qt.AlignRight)
        self.PathEffects.setValue(self.aw.qmc.patheffects)
        self.PathEffects.editingFinished.connect(self.changePathEffects)
        pathEffectsLayout = QHBoxLayout()
        pathEffectsLayout.addWidget(effectslabel)
        pathEffectsLayout.addWidget(self.PathEffects)
        pathEffectsLayout.addStretch()
        # graph style
        stylelabel = QLabel(QApplication.translate("Label", "Style",None))
        self.GraphStyle = QComboBox()
        self.GraphStyle.addItems([QApplication.translate("ComboBox","classic",None),
                                  QApplication.translate("ComboBox","xkcd",None)])
        self.GraphStyle.setCurrentIndex(self.aw.qmc.graphstyle)
        self.GraphStyle.currentIndexChanged.connect(self.changeGraphStyle)
        # graph font
        fontlabel = QLabel(QApplication.translate("Label", "Font",None))
        self.GraphFont = QComboBox()
        # no Comic on Linux!
        self.GraphFont.addItems([QApplication.translate("ComboBox","Default",None),
                                      "Humor",
                                      "Comic",
                                      "WenQuanYi Zen Hei",
                                      "Source Han Sans CN",
                                      "Source Han Sans TW",
                                      "Source Han Sans HK",
                                      "Source Han Sans KR",
                                      "Source Han Sans JP",
                                      "Dijkstra"])
        self.GraphFont.setCurrentIndex(self.aw.qmc.graphfont)
        self.GraphFont.currentIndexChanged.connect(self.changeGraphFont)
        graphLayout = QHBoxLayout()
        graphLayout.addWidget(stylelabel)
        graphLayout.addWidget(self.GraphStyle)
        #tab0
        tab0Layout = QVBoxLayout()
        tab0Layout.addWidget(rorGroupLayout)
        tab0Layout.addWidget(rorLCDGroupLayout)
        tab0Layout.addWidget(rorSymbolicFormulaGroupLayout)
        tab0Layout.addStretch()
        #tab1
        tab1UpperRightLayout = QVBoxLayout()
        tab1UpperRightLayout.addWidget(postRoastGroupLayout)
        tab1UpperRightLayout.addWidget(renderGroupLayout)
        
        tab1UpperLayout = QHBoxLayout()
        tab1UpperLayout.addWidget(inputFilterGroupLayout)
        tab1UpperLayout.addLayout(tab1UpperRightLayout)
        
        tab1Layout = QVBoxLayout()
        tab1Layout.addLayout(tab1UpperLayout)
        tab1Layout.addWidget(rorFilterGroupLayout)
        tab1Layout.addStretch()
        #tab11
        tab11Layout = QVBoxLayout()
        tab11Layout.addWidget(hudGroupLayout)
        tab11Layout.addStretch()
        #tab2
        #Equation plotter
#        self.equlabel = QLabel(QApplication.translate("Label", "Y(x)",None))
        self.equc1label = QLabel(QApplication.translate("Label", "P1",None))
        self.equc2label = QLabel(QApplication.translate("Label", "P2",None))
        self.equc3label = QLabel(QApplication.translate("Label", "P3",None))
        self.equc4label = QLabel(QApplication.translate("Label", "P4",None))
        self.equc5label = QLabel(QApplication.translate("Label", "P5",None))
        self.equc6label = QLabel(QApplication.translate("Label", "P6",None))
        self.equc7label = QLabel(QApplication.translate("Label", "P7",None))
        self.equc8label = QLabel(QApplication.translate("Label", "P8",None))
        self.equc9label = QLabel(QApplication.translate("Label", "P9",None))
        self.equedit1 = QLineEdit(self.aw.qmc.plotcurves[0])
        self.equedit2 = QLineEdit(self.aw.qmc.plotcurves[1])
        self.equedit3 = QLineEdit(self.aw.qmc.plotcurves[2])
        self.equedit4 = QLineEdit(self.aw.qmc.plotcurves[3])
        self.equedit5 = QLineEdit(self.aw.qmc.plotcurves[4])
        self.equedit6 = QLineEdit(self.aw.qmc.plotcurves[5])
        self.equedit7 = QLineEdit(self.aw.qmc.plotcurves[6])
        self.equedit8 = QLineEdit(self.aw.qmc.plotcurves[7])
        self.equedit9 = QLineEdit(self.aw.qmc.plotcurves[8])
        self.equedit1.setSelection (0,0)
        self.equedit2.setSelection (0,0)
        self.equedit3.setSelection (0,0)
        self.equedit4.setSelection (0,0)
        self.equedit5.setSelection (0,0)
        self.equedit6.setSelection (0,0)
        self.equedit7.setSelection (0,0)
        self.equedit8.setSelection (0,0)
        self.equedit9.setSelection (0,0)

        color1Button = QPushButton(QApplication.translate("Button","Color",None))
        color1Button.setFocusPolicy(Qt.NoFocus)
        color1Button.clicked.connect(self.setcurvecolor0)
        color2Button = QPushButton(QApplication.translate("Button","Color",None))
        color2Button.setFocusPolicy(Qt.NoFocus)
        color2Button.clicked.connect(self.setcurvecolor1)
        color3Button = QPushButton(QApplication.translate("Button","Color",None))
        color3Button.setFocusPolicy(Qt.NoFocus)
        color3Button.clicked.connect(self.setcurvecolor2)
        color4Button = QPushButton(QApplication.translate("Button","Color",None))
        color4Button.setFocusPolicy(Qt.NoFocus)
        color4Button.clicked.connect(self.setcurvecolor3)
        color5Button = QPushButton(QApplication.translate("Button","Color",None))
        color5Button.setFocusPolicy(Qt.NoFocus)
        color5Button.clicked.connect(self.setcurvecolor4)
        color6Button = QPushButton(QApplication.translate("Button","Color",None))
        color6Button.setFocusPolicy(Qt.NoFocus)
        color6Button.clicked.connect(self.setcurvecolor5)
        color7Button = QPushButton(QApplication.translate("Button","Color",None))
        color7Button.setFocusPolicy(Qt.NoFocus)
        color7Button.clicked.connect(self.setcurvecolor6)
        color8Button = QPushButton(QApplication.translate("Button","Color",None))
        color8Button.setFocusPolicy(Qt.NoFocus)
        color8Button.clicked.connect(self.setcurvecolor7)
        color9Button = QPushButton(QApplication.translate("Button","Color",None))
        color9Button.setFocusPolicy(Qt.NoFocus)
        color9Button.clicked.connect(self.setcurvecolor8)
        self.equc1colorlabel = QLabel("  ")
        self.equc2colorlabel = QLabel("  ")
        self.equc3colorlabel = QLabel("  ")
        self.equc4colorlabel = QLabel("  ")
        self.equc5colorlabel = QLabel("  ")
        self.equc6colorlabel = QLabel("  ")
        self.equc7colorlabel = QLabel("  ")
        self.equc8colorlabel = QLabel("  ")
        self.equc9colorlabel = QLabel("  ")
        self.equc1colorlabel.setStyleSheet("background-color:'%s';"%self.aw.qmc.plotcurvecolor[0])
        self.equc2colorlabel.setStyleSheet("background-color:'%s';"%self.aw.qmc.plotcurvecolor[1])
        self.equc3colorlabel.setStyleSheet("background-color:'%s';"%self.aw.qmc.plotcurvecolor[2])
        self.equc4colorlabel.setStyleSheet("background-color:'%s';"%self.aw.qmc.plotcurvecolor[3])
        self.equc5colorlabel.setStyleSheet("background-color:'%s';"%self.aw.qmc.plotcurvecolor[4])
        self.equc6colorlabel.setStyleSheet("background-color:'%s';"%self.aw.qmc.plotcurvecolor[5])
        self.equc7colorlabel.setStyleSheet("background-color:'%s';"%self.aw.qmc.plotcurvecolor[6])
        self.equc8colorlabel.setStyleSheet("background-color:'%s';"%self.aw.qmc.plotcurvecolor[7])
        self.equc9colorlabel.setStyleSheet("background-color:'%s';"%self.aw.qmc.plotcurvecolor[8])

        equdrawbutton = QPushButton(QApplication.translate("Button","Plot",None))
        equdrawbutton.setFocusPolicy(Qt.NoFocus)
        equdrawbutton.clicked.connect(self.plotequ)
        equshowtablebutton = QPushButton(QApplication.translate("Button","Data",None))
        equshowtablebutton.setFocusPolicy(Qt.NoFocus)
        equshowtablebutton.setToolTip(QApplication.translate("Tooltip","Shows data table of plots",None))
        equshowtablebutton.clicked.connect(self.equshowtable)
        self.equbackgroundbutton = QPushButton(QApplication.translate("Button","Background",None))
        self.equbackgroundbutton.setFocusPolicy(Qt.NoFocus)
        self.equbackgroundbutton.clicked.connect(self.setbackgroundequ1_slot)
        self.equvdevicebutton = QPushButton()       
        self.update_equbuttons()
        saveImgButton = QPushButton(QApplication.translate("Button","Save Image",None))
        saveImgButton.setFocusPolicy(Qt.NoFocus)
        saveImgButton.setToolTip(QApplication.translate("Tooltip","Save image using current graph size to a png format",None))
        saveImgButton.clicked.connect(self.aw.resizeImg_0_1)
        helpcurveDialogButton = QDialogButtonBox()
        helpcurveButton = helpcurveDialogButton.addButton(QDialogButtonBox.Help)
        helpcurveButton.setFocusPolicy(Qt.NoFocus)
        self.setButtonTranslations(helpcurveButton,"Help",QApplication.translate("Button","Help", None))
        helpcurveButton.clicked.connect(self.showSymbolicHelp)
        curve1Layout = QGridLayout()
        curve1Layout.setSpacing(5)
        curve1Layout.addWidget(self.equc1label,0,0)
        curve1Layout.addWidget(self.equedit1,0,1)
        curve1Layout.addWidget(self.equbackgroundbutton,0,2)
        curve1Layout.addWidget(color1Button,0,3)
        curve1Layout.addWidget(self.equc1colorlabel,0,4)
        curve1Layout.addWidget(self.equc2label,1,0)
        curve1Layout.addWidget(self.equedit2,1,1)
        curve1Layout.addWidget(self.equvdevicebutton,1,2)
        curve1Layout.addWidget(color2Button,1,3)
        curve1Layout.addWidget(self.equc2colorlabel,1,4)
        plot1GroupBox = QGroupBox()
        plot1GroupBox.setLayout(curve1Layout)
        curveLayout = QGridLayout()
        curveLayout.setSpacing(5)
        curveLayout.addWidget(self.equc3label,0,0)
        curveLayout.addWidget(self.equedit3,0,1)
        curveLayout.addWidget(color3Button,0,2)
        curveLayout.addWidget(self.equc3colorlabel,0,3)
        curveLayout.addWidget(self.equc4label,1,0)
        curveLayout.addWidget(self.equedit4,1,1)
        curveLayout.addWidget(color4Button,1,2)
        curveLayout.addWidget(self.equc4colorlabel,1,3)
        curveLayout.addWidget(self.equc5label,2,0)
        curveLayout.addWidget(self.equedit5,2,1)
        curveLayout.addWidget(color5Button,2,2)
        curveLayout.addWidget(self.equc5colorlabel,2,3)
        curveLayout.addWidget(self.equc6label,3,0)
        curveLayout.addWidget(self.equedit6,3,1)
        curveLayout.addWidget(color6Button,3,2)
        curveLayout.addWidget(self.equc6colorlabel,3,3)
        curveLayout.addWidget(self.equc7label,4,0)
        curveLayout.addWidget(self.equedit7,4,1)
        curveLayout.addWidget(color7Button,4,2)
        curveLayout.addWidget(self.equc7colorlabel,4,3)
        curveLayout.addWidget(self.equc8label,5,0)
        curveLayout.addWidget(self.equedit8,5,1)
        curveLayout.addWidget(color8Button,5,2)
        curveLayout.addWidget(self.equc8colorlabel,5,3)
        curveLayout.addWidget(self.equc9label,6,0)
        curveLayout.addWidget(self.equedit9,6,1)
        curveLayout.addWidget(color9Button,6,2)
        curveLayout.addWidget(self.equc9colorlabel,6,3)
        curvebuttonlayout = QHBoxLayout()
        curvebuttonlayout.addWidget(equdrawbutton)
        curvebuttonlayout.addStretch()
        curvebuttonlayout.addWidget(saveImgButton)
        curvebuttonlayout.addStretch()
        curvebuttonlayout.addWidget(equshowtablebutton)
        curvebuttonlayout.addStretch()
        curvebuttonlayout.addWidget(helpcurveDialogButton)
        tab2Layout = QVBoxLayout()
#        tab2Layout.addWidget(self.equlabel)
        tab2Layout.addWidget(plot1GroupBox)
        tab2Layout.addLayout(curveLayout)
        tab2Layout.addLayout(curvebuttonlayout)
        tab2Layout.addStretch()
        ##### TAB 3
        self.interpCheck = QCheckBox(QApplication.translate("CheckBox","Show",None))
        self.interpCheck.setFocusPolicy(Qt.NoFocus)
        self.interpCheck.stateChanged.connect(self.interpolation) #toggle
        self.interpComboBox = QComboBox()
        self.interpComboBox.setMaximumWidth(100)
        self.interpComboBox.setMinimumWidth(55)
        self.interpComboBox.addItems([QApplication.translate("ComboBox","linear",None),
                                      QApplication.translate("ComboBox","cubic",None),
                                      QApplication.translate("ComboBox","nearest",None)])
        self.interpComboBox.setToolTip(QApplication.translate("Tooltip", "linear: linear interpolation\ncubic: 3rd order spline interpolation\nnearest: y value of the nearest point", None))
        self.interpComboBox.setFocusPolicy(Qt.NoFocus)
        self.interpComboBox.currentIndexChanged.connect(self.changeInterpolationMode)
#         'linear'  : linear interpolation
#         'cubic'   : 3rd order spline interpolation
#         'nearest' : take the y value of the nearest point
        self.univarCheck = QCheckBox(QApplication.translate("CheckBox", "Show",None))
        self.univarCheck.setFocusPolicy(Qt.NoFocus)
        self.univarCheck.stateChanged.connect(self.univar) #toggle
        univarButton = QPushButton(QApplication.translate("Button","Info",None))
        univarButton.setFocusPolicy(Qt.NoFocus)
        univarButton.setMaximumSize(univarButton.sizeHint())
        univarButton.setMinimumSize(univarButton.minimumSizeHint())
        self.lnvarCheck = QCheckBox(QApplication.translate("CheckBox", "Show",None))
        self.lnvarCheck.setFocusPolicy(Qt.NoFocus)
        self.lnvarCheck.stateChanged.connect(self.lnvar) #toggle
        self.lnresult = QLineEdit()
        self.lnresult.setReadOnly(True)
        self.lnresult.setStyleSheet("background-color:'lightgrey';")
        self.expvarCheck = QCheckBox(QApplication.translate("CheckBox", "Show",None))
        self.expvarCheck.setFocusPolicy(Qt.NoFocus)
        self.expvarCheck.stateChanged.connect(self.expvar) #toggle
        self.expresult = QLineEdit()
        self.expresult.setReadOnly(True)
        self.expresult.setStyleSheet("background-color:'lightgrey';")
        self.expradiobutton1 = QRadioButton(u"x\xb2")
        self.expradiobutton1.setChecked(True)
        self.expradiobutton1.power = self.exppower = 2
        self.expradiobutton1.toggled.connect(self.expradiobuttonClicked)
        self.expradiobutton2 = QRadioButton(u"x\xb3")
        self.expradiobutton2.power = 3
        self.expradiobutton2.toggled.connect(self.expradiobuttonClicked)
        self.exptimeoffsetLabel = QLabel(QApplication.translate("Label", "Offset seconds from CHARGE", None))
        self.exptimeoffset = QLineEdit("180")   #default to 180 seconds past CHARGE
        self.exptimeoffset.editingFinished.connect(self.exptimeoffsetChanged) 
        
        self.analyzecombobox = QComboBox()
        self.analyzecomboboxLabel = QLabel(QApplication.translate("Label", "Start of Analyze interval of interest", None))
        self.analyzecombobox.addItems([QApplication.translate("ComboBox","DRY END",None),
                                       QApplication.translate("ComboBox","120 secs before FCs",None),
                                       QApplication.translate("ComboBox","Custom",None)])
        width = self.analyzecombobox.minimumSizeHint().width()
        self.analyzecombobox.setMinimumWidth(width)
        self.analyzecombobox.setToolTip(QApplication.translate("Tooltip", "Choose the start point of analysis interval of interest", None))
        self.analyzecombobox.setFocusPolicy(Qt.NoFocus)
        self.analyzecombobox.setCurrentIndex(self.aw.qmc.analysisstartchoice)
        self.analyzecombobox.currentIndexChanged.connect(self.changeAnalyzecombobox)
        self.analyzetimeoffsetLabel = QLabel(QApplication.translate("Label", "Custom offset seconds from CHARGE", None))
        self.analyzetimeoffset = QLineEdit(str(self.aw.qmc.analysisoffset))   #default to 180 seconds past CHARGE
        self.analyzetimeoffset.setMaximumWidth(100)
        self.analyzetimeoffset.setMinimumWidth(55)
        self.analyzetimeoffset.editingFinished.connect(self.analyzetimeoffsetChanged)
        if self.analyzecombobox.currentIndex() in [0,1]:
            self.analyzetimeoffset.setEnabled(False)
        else:
            self.analyzetimeoffset.setEnabled(True)
        self.segmentsamplesthresholdLabel = QLabel(QApplication.translate("Label", "Number of samples considered significant", None))
        self.segmentsamplesthreshold = QLineEdit(str(int(round(self.aw.qmc.segmentsamplesthreshold))))   #default
        self.segmentsamplesthreshold.setMaximumWidth(100)
        self.segmentsamplesthreshold.setMinimumWidth(55)
        self.segmentsamplesthreshold.editingFinished.connect(self.segmentsamplesthresholdChanged)
        self.segmentsamplesthreshold.setValidator(QIntValidator(0,50,self.segmentsamplesthreshold))
        self.segmentdeltathresholdLabel = QLabel(QApplication.translate("Label", "Delta RoR Actual-to-Fit considered significant", None))
        self.segmentdeltathreshold = QLineEdit(str(self.aw.qmc.segmentdeltathreshold))   #default
        self.segmentdeltathreshold.setMaximumWidth(100)
        self.segmentdeltathreshold.setMinimumWidth(55)
        self.segmentdeltathreshold.editingFinished.connect(self.segmentdeltathresholdChanged)

        self.curvefitcombobox = QComboBox()
        self.curvefitcomboboxLabel = QLabel(QApplication.translate("Label", "Start of Curve Fit window", None))
        self.curvefitcombobox.addItems([QApplication.translate("ComboBox","DRY END",None),
                                       QApplication.translate("ComboBox","120 secs before FCs",None),
                                       QApplication.translate("ComboBox","Custom",None)])
        width = self.curvefitcombobox.minimumSizeHint().width()
        self.curvefitcombobox.setMinimumWidth(width)
        self.curvefitcombobox.setToolTip(QApplication.translate("Tooltip", "Choose the start point of curve fitting", None))
        self.curvefitcombobox.setFocusPolicy(Qt.NoFocus)
        self.curvefitcombobox.setCurrentIndex(self.aw.qmc.curvefitstartchoice)
        self.curvefitcombobox.currentIndexChanged.connect(self.changeCurvefitcombobox)
        self.curvefittimeoffsetLabel = QLabel(QApplication.translate("Label", "Custom offset seconds from CHARGE", None))
        self.curvefittimeoffset = QLineEdit(str(self.aw.qmc.curvefitoffset))   #default to 180 seconds past CHARGE
        self.curvefittimeoffset.setMaximumWidth(100)
#        self.curvefittimeoffset.setMaximumWidth(50)
        self.curvefittimeoffset.setMinimumWidth(55)
        self.curvefittimeoffset.editingFinished.connect(self.curvefittimeoffsetChanged)
        if self.curvefitcombobox.currentIndex() in [0,1]:
            self.curvefittimeoffset.setEnabled(False)
        else:
            self.curvefittimeoffset.setEnabled(True)
        self.bkgndButton = QPushButton(QApplication.translate("Button","Create Background Curve",None))
        self.bkgndButton.setFocusPolicy(Qt.NoFocus)
        self.bkgndButton.setMaximumSize(self.bkgndButton.sizeHint())
        self.bkgndButton.setMinimumSize(self.bkgndButton.minimumSizeHint())
        self.bkgndButton.clicked.connect(self.fittoBackground)
        self.bkgndButton.setEnabled(False)
        polyfitdeglabel = QLabel(QApplication.translate("Label","deg",None))
        self.polyfitdeg = QSpinBox()
        self.polyfitdeg.setFocusPolicy(Qt.NoFocus)
        self.polyfitdeg.setRange(1,4)
        self.polyfitdeg.setAlignment(Qt.AlignRight)
        self.polyfitdeg.setMinimumWidth(20)
        # build list of available curves
        self.curves = []
        self.curvenames = []
        self.c1ComboBox = QComboBox()
        self.c2ComboBox = QComboBox()
        univarButton.clicked.connect(self.showunivarinfo)
        self.polyfitCheck = QCheckBox(QApplication.translate("CheckBox", "Show",None))
        self.polyfitCheck.setFocusPolicy(Qt.NoFocus)
        self.polyfitCheck.clicked.connect(self.polyfit) #toggle
        self.result = QLineEdit()
        self.result.setReadOnly(True)
        self.result.setStyleSheet("background-color:'lightgrey';")
        startlabel = QLabel(QApplication.translate("Label", "Start",None))
        endlabel = QLabel(QApplication.translate("Label", "End",None))
        self.startEdit = QLineEdit()
        self.startEdit.setMaximumWidth(60)
        self.startEdit.setAlignment(Qt.AlignRight)
        self.endEdit = QLineEdit()
        self.endEdit.setMaximumWidth(60)
        self.endEdit.setAlignment(Qt.AlignRight)
        self.polyfitRoR = False
        self.polyfitRoRflag = QCheckBox(deltaLabelUTF8 + " " + QApplication.translate("GroupBox","Axis",None))
        self.polyfitRoRflag.setChecked(self.polyfitRoR)
        self.polyfitRoRflag.setFocusPolicy(Qt.NoFocus)
        self.polyfitRoRflag.stateChanged.connect(self.polyfitRoRflagChanged)
        regextime = QRegularExpression(r"^[0-5][0-9]:[0-5][0-9]$")
        self.startEdit.setValidator(QRegularExpressionValidator(regextime,self))
        self.startEdit.setText("00:00")
        self.endEdit.setValidator(QRegularExpressionValidator(regextime,self))
        if len(self.aw.qmc.timex) > 0:
            self.endEdit.setText(stringfromseconds(self.aw.qmc.timex[-1]))
        else:
            self.endEdit.setText("00:00")
        # calculate event list
        self.events = self.eventlist()
        self.eventAComboBox = QComboBox()
        self.eventAComboBox.addItems([""] + [i[0] for i in self.events])
        self.eventAComboBox.setCurrentIndex(0)
        self.eventAComboBox.currentIndexChanged.connect(self.calcEventRC)
        self.eventBComboBox = QComboBox()
        self.eventBComboBox.addItems([""] + [i[0] for i in self.events])
        self.eventBComboBox.setCurrentIndex(0)
        self.eventBComboBox.currentIndexChanged.connect(self.calcEventRC)
        tab3Layout = QVBoxLayout()
        interLayout = QHBoxLayout()
        interLayout.addWidget(self.interpCheck)
        interLayout.addStretch()
        interLayout.addWidget(self.interpComboBox)
        interGroupLayout = QGroupBox(QApplication.translate("GroupBox","Interpolate",None))
        interGroupLayout.setLayout(interLayout)
        uniLayout = QHBoxLayout()
        uniLayout.addWidget(self.univarCheck)
        uniLayout.addStretch()
        uniLayout.addWidget(univarButton)
        univarGroupLayout = QGroupBox(QApplication.translate("GroupBox","Univariate",None))
        univarGroupLayout.setLayout(uniLayout)
        lnLayout = QVBoxLayout()
        lnLayout.addWidget(self.lnvarCheck)
        lnLayout.addWidget(self.lnresult)
        lnVLayout = QVBoxLayout()
        lnVLayout.addLayout(lnLayout)
        lnVLayout.addStretch()
        lnvarGroupLayout = QGroupBox(QApplication.translate("GroupBox","ln()",None))
        lnvarGroupLayout.setLayout(lnVLayout)
        expVLayout1 = QHBoxLayout()        
        expVLayout1.addWidget(self.expvarCheck)
        expVLayout1.addWidget(self.expresult)
        expVLayout1.addWidget(self.bkgndButton)      
        expHLayout2 = QHBoxLayout()        
        expHLayout2.addWidget(self.expradiobutton1)
        expHLayout2.addWidget(self.expradiobutton2)
        expHLayout2.addWidget(self.exptimeoffsetLabel)
        expHLayout2.addWidget(self.exptimeoffset)
        expHLayout2.addStretch()
        expLayout = QVBoxLayout()
        expLayout.addLayout(expHLayout2)
        expLayout.addLayout(expVLayout1)
        expvarGroupLayout = QGroupBox(QApplication.translate("GroupBox","Exponent",None))
        expvarGroupLayout.setLayout(expLayout)
        polytimes = QHBoxLayout()
        polytimes.addWidget(startlabel)
        polytimes.addWidget(self.startEdit)
        polytimes.addWidget(self.eventAComboBox)
        polytimes.addStretch()
        polytimes.addWidget(self.eventBComboBox)
        polytimes.addWidget(self.endEdit)
        polytimes.addWidget(endlabel)
        polyCurves = QHBoxLayout()
        polyCurves.addWidget(self.polyfitRoRflag)
        polyCurves.addWidget(self.c1ComboBox)
        polyCurves.addWidget(self.result)
        polyCurves.addWidget(self.c2ComboBox)
        polyLayout = QHBoxLayout()
        polyLayout.addWidget(self.polyfitCheck)
        polyLayout.addStretch()
        polyLayout.addWidget(startlabel)
        polyLayout.addWidget(self.startEdit)
        polyLayout.addWidget(self.eventAComboBox)
        polyLayout.addStretch()
        polyLayout.addWidget(self.eventBComboBox)
        polyLayout.addWidget(self.endEdit)
        polyLayout.addWidget(endlabel)
        polyLayout.addStretch()
        polyLayout.addWidget(polyfitdeglabel)
        polyLayout.addWidget(self.polyfitdeg)
        polyVLayout = QVBoxLayout()
        polyVLayout.addLayout(polyLayout)
#        polyVLayout.addLayout(polytimes)
        polyVLayout.addLayout(polyCurves)
        polyfitGroupLayout = QGroupBox(QApplication.translate("GroupBox","Polyfit",None))
        polyfitGroupLayout.setLayout(polyVLayout)
        interUniLayout = QHBoxLayout()
        interUniLayout.addWidget(interGroupLayout)
        interUniLayout.addWidget(univarGroupLayout)
        lnvarexpvarLayout = QHBoxLayout()
        lnvarexpvarLayout.addWidget(lnvarGroupLayout)
        lnvarexpvarLayout.addWidget(expvarGroupLayout)
        tab3Layout.addLayout(interUniLayout)
        tab3Layout.addLayout(lnvarexpvarLayout)
        tab3Layout.addWidget(polyfitGroupLayout)
        tab3Layout.addStretch()
        ##### TAB 4
        analyzeVLayout1a = QVBoxLayout()
        analyzeVLayout1a.addWidget(self.curvefitcomboboxLabel)
        analyzeVLayout1a.addWidget(self.curvefitcombobox)
#        analyzeHLayout1.addStretch()
        analyzeVLayout1b = QVBoxLayout()
        analyzeVLayout1b.addWidget(self.curvefittimeoffsetLabel)
        analyzeVLayout1b.addWidget(self.curvefittimeoffset)
        analyzeHLayout1 = QHBoxLayout()
        analyzeHLayout1.addLayout(analyzeVLayout1a)
        analyzeHLayout1.addStretch()
        analyzeHLayout1.addLayout(analyzeVLayout1b)
        analyzeGroupLayout1 = QGroupBox(QApplication.translate("GroupBox","Curve Fit Options",None))
        analyzeGroupLayout1.setLayout(analyzeHLayout1)

        analyzeHLayout2a = QVBoxLayout()
        analyzeHLayout2a.addWidget(self.analyzecomboboxLabel)
        analyzeHLayout2a.addWidget(self.analyzecombobox)
        analyzeHLayout2b = QVBoxLayout()
        analyzeHLayout2b.addWidget(self.analyzetimeoffsetLabel)
        analyzeHLayout2b.addWidget(self.analyzetimeoffset)
        analyzeHLayout2 = QHBoxLayout()
        analyzeHLayout2.addLayout(analyzeHLayout2a)
        analyzeHLayout2.addStretch()
        analyzeHLayout2.addLayout(analyzeHLayout2b)
        analyzeGroupLayout2 = QGroupBox(QApplication.translate("GroupBox","Interval of Interest Options",None))
        analyzeGroupLayout2.setLayout(analyzeHLayout2)

        flcrVLayout1 = QVBoxLayout()
        flcrVLayout1.addWidget(self.segmentsamplesthresholdLabel)
        flcrVLayout1.addWidget(self.segmentsamplesthreshold)
        flcrVLayout2 = QVBoxLayout()
        flcrVLayout2.addWidget(self.segmentdeltathresholdLabel)
        flcrVLayout2.addWidget(self.segmentdeltathreshold)
        
        flcrHLayout = QHBoxLayout()
        flcrHLayout.addLayout(flcrVLayout1)
        flcrHLayout.addStretch()
        flcrHLayout.addLayout(flcrVLayout2)
        flcrGroupLayout = QGroupBox(QApplication.translate("GroupBox","Analyze Options",None))
        flcrGroupLayout.setLayout(flcrHLayout)
        tab4Layout = QVBoxLayout()
        tab4Layout.addWidget(analyzeGroupLayout1)
        tab4Layout.addWidget(analyzeGroupLayout2)
        tab4Layout.addWidget(flcrGroupLayout)
        tab4Layout.addStretch()
        ##### TAB 5
        self.styleComboBox = QComboBox()
        available = list(map(str, list(QStyleFactory.keys())))
        self.styleComboBox.addItems(available)
        self.styleComboBox.setFocusPolicy(Qt.NoFocus)
        try:
            #pylint: disable=E1102
            self.styleComboBox.setCurrentIndex(list(map(lambda x:x.lower(),available)).index(self.aw.appearance.lower()))
        except Exception:
            pass
        self.styleComboBox.currentIndexChanged.connect(self.setappearance)
        self.resolutionSpinBox = QSpinBox()
        self.resolutionSpinBox.setRange(40,300)
        self.resolutionSpinBox.setSingleStep(5)
        self.resolutionSpinBox.setValue(self.aw.dpi)
        self.resolutionSpinBox.setFocusPolicy(Qt.NoFocus)
        resButton = QPushButton(QApplication.translate("Button","Set",None))
        resButton.setFocusPolicy(Qt.NoFocus)
        resButton.clicked.connect(lambda _:self.changedpi())
        self.soundCheck = QCheckBox(QApplication.translate("CheckBox", "Beep",None))
        self.soundCheck.setChecked(self.aw.soundflag) 
        self.soundCheck.setFocusPolicy(Qt.NoFocus)
        self.soundCheck.stateChanged.connect(self.soundset) #toggle
        appLayout1 = QHBoxLayout()
        appLayout1.addLayout(pathEffectsLayout)
        appLayout1.addStretch()
        appLayout1.addWidget(self.soundCheck)
        appLayout1.addStretch()
        appLayout1.addWidget(self.styleComboBox)
        appLayout2 = QHBoxLayout()
        appLayout2.addLayout(graphLayout)
        appLayout2.addStretch()
        appLayout2.addWidget(fontlabel)
        appLayout2.addWidget(self.GraphFont)
        appLayout = QVBoxLayout()
        appLayout.addLayout(appLayout1)
        appLayout.addLayout(appLayout2)
        appLayout.addStretch()
        appearanceGroupWidget = QGroupBox(QApplication.translate("GroupBox","Appearance",None))
        appearanceGroupWidget.setLayout(appLayout)
        graphLabel = QLabel(QApplication.translate("Tab","Graph",None))
        setresLayout = QHBoxLayout()
        setresLayout.addWidget(graphLabel)
        setresLayout.addWidget(self.resolutionSpinBox)
        setresLayout.addWidget(resButton)
        setresVLayout = QVBoxLayout()
        setresVLayout.addWidget(self.DecimalPlaceslcd)
        setresVLayout.addLayout(setresLayout)
        setresVLayout.addStretch()
        resolutionGroupWidget = QGroupBox(QApplication.translate("GroupBox","Resolution",None))
        resolutionGroupWidget.setLayout(setresVLayout)
        appresLayout = QHBoxLayout()
        appresLayout.addWidget(appearanceGroupWidget)
        appresLayout.addWidget(resolutionGroupWidget)
        
        # tick
        # port
        self.WebLCDsURL = QLabel()
        self.WebLCDsURL.setOpenExternalLinks(True)
        self.WebLCDsFlag = QCheckBox()
        self.WebLCDsFlag.setChecked(self.aw.WebLCDs)
        self.WebLCDsFlag.setFocusPolicy(Qt.NoFocus)
        self.WebLCDsPortLabel = QLabel(QApplication.translate("Label", "Port", None))
        self.WebLCDsPort = QLineEdit(str(self.aw.WebLCDsPort))
        self.WebLCDsPort.setAlignment(Qt.AlignRight)
        self.WebLCDsPort.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[0-9]{1,4}$"),self))
        self.WebLCDsPort.setMaximumWidth(45)
        self.QRpic = QLabel() # the QLabel holding the QR code image
        if self.aw.WebLCDs:
            try:
                self.setWebLCDsURL()
            except:
                self.WebLCDsURL.setText("")
                self.QRpic.setPixmap(QPixmap())
                self.aw.WebLCDs = False
        else:
            self.WebLCDsURL.setText("")
            self.QRpic.setPixmap(QPixmap())
        self.WebLCDsAlerts = QCheckBox(QApplication.translate("CheckBox", "Alarm Popups",None))
        self.WebLCDsAlerts.setChecked(self.aw.WebLCDsAlerts)
        self.WebLCDsAlerts.setFocusPolicy(Qt.NoFocus)
        if not self.aw.WebLCDs:
            self.WebLCDsAlerts.setDisabled(True)
        self.WebLCDsAlerts.stateChanged.connect(self.toggleWebLCDsAlerts) #toggle
        self.WebLCDsPort.editingFinished.connect(self.changeWebLCDsPort)
        self.WebLCDsFlag.clicked.connect(self.toggleWebLCDs)
        WebLCDsLayout = QHBoxLayout()
        WebLCDsLayout.addWidget(self.WebLCDsFlag)
        WebLCDsLayout.addWidget(self.WebLCDsPortLabel)
        WebLCDsLayout.addWidget(self.WebLCDsPort)
        WebLCDsLayout.addStretch()
        WebLCDsAlertsLayout = QHBoxLayout()
        WebLCDsAlertsLayout.addWidget(self.WebLCDsAlerts)
        WebLCDsVLayout = QVBoxLayout()
        if not self.app.artisanviewerMode:
            WebLCDsVLayout.addLayout(WebLCDsLayout)
            WebLCDsVLayout.addLayout(WebLCDsAlertsLayout)
            WebLCDsVLayout.addWidget(self.WebLCDsURL)
            WebLCDsVLayout.addWidget(self.QRpic)
        else:
            naLayout = QHBoxLayout()
            notavailLable = QLabel(QApplication.translate("Label", "Not available in ArtisanViewer", None))
            naLayout.addWidget(notavailLable)
            naLayout.addStretch()
            WebLCDsVLayout.addLayout(naLayout)
        WebLCDsVLayout.addStretch()
        WebLCDsGroupWidget = QGroupBox(QApplication.translate("GroupBox","WebLCDs",None))
        WebLCDsGroupWidget.setLayout(WebLCDsVLayout)

        # Renaming BT and ET
        self.renameETLabel = QLabel(QApplication.translate("Label", "ET", None))
        self.renameETLine = QLineEdit(self.aw.ETname)
        self.renameETLine.editingFinished.connect(self.renameET)
        self.renameBTLabel = QLabel(QApplication.translate("Label", "BT", None))
        self.renameBTLine = QLineEdit(self.aw.BTname)
        self.renameBTLine.editingFinished.connect(self.renameBT)
        renameLayout = QHBoxLayout()
        renameLayout.addWidget(self.renameETLabel)
        renameLayout.addWidget(self.renameETLine)
        renameLayout.addWidget(self.renameBTLabel)
        renameLayout.addWidget(self.renameBTLine)
        renameGroupWidget = QGroupBox(QApplication.translate("GroupBox", "Rename ET and BT",None))
        renameGroupWidget.setLayout(renameLayout)
        #watermark image
        self.logopathedit = QLineEdit(self.aw.qmc.backgroundpath)
        self.logopathedit.setStyleSheet("background-color:'lightgrey';")
        self.logopathedit.setReadOnly(True)
        self.logopathedit.setFocusPolicy(Qt.NoFocus)
        self.logopathedit.setText(self.aw.logofilename)
        logoalphalabel = QLabel(QApplication.translate("Label","Opacity", None))
        self.logoalpha = MyQDoubleSpinBox()
        self.logoalpha.setDecimals(1)
        self.logoalpha.setSingleStep(0.5)
        self.logoalpha.setRange(0.,10.)
        self.logoalpha.setValue(self.aw.logoimgalpha)
        self.logoalpha.setMinimumWidth(50)
        self.logoalpha.setAlignment(Qt.AlignRight)
        self.logoalpha.editingFinished.connect(self.changelogoalpha)
        logoshowCheck = QCheckBox(QApplication.translate("CheckBox", "Hide Image During Roast",None))
        logoshowCheck.setChecked(self.aw.logoimgflag)
        logoshowCheck.setFocusPolicy(Qt.NoFocus)
        logoshowCheck.stateChanged.connect(self.changelogoshowCheck)
        loadButton = QPushButton(QApplication.translate("Button","Load", None))
        loadButton.setFocusPolicy(Qt.NoFocus)
        delButton = QPushButton(QApplication.translate("Button","Delete", None))
        delButton.setFocusPolicy(Qt.NoFocus)
        loadButton.clicked.connect(self.logofileload)
        delButton.clicked.connect(self.logofiledelete)
        logofileLayout = QHBoxLayout()
        logofileLayout.addWidget(self.logopathedit)
        logofileLayout.addWidget(logoalphalabel)
        logofileLayout.addWidget(self.logoalpha)
        logobuttonsLayout = QHBoxLayout()
        logobuttonsLayout.addWidget(loadButton)
        logobuttonsLayout.addWidget(delButton)
        logobuttonsLayout.addStretch()
        logobuttonsLayout.addWidget(logoshowCheck)
        logoLayout = QVBoxLayout()
        logoLayout.addLayout(logofileLayout)
        logoLayout.addLayout(logobuttonsLayout)
        logofileGroupWidget = QGroupBox(QApplication.translate("GroupBox", "Logo Image File",None))
        logofileGroupWidget.setLayout(logoLayout)

        renlogLayout = QVBoxLayout()
        renlogLayout.addWidget(renameGroupWidget)
        renlogLayout.addWidget(logofileGroupWidget)
        webLayout = QHBoxLayout()
        webLayout.addWidget(WebLCDsGroupWidget)
        webrenlogLayout = QHBoxLayout()
        webrenlogLayout.addLayout(renlogLayout)
        webrenlogLayout.addLayout(webLayout)

        tab5Layout = QVBoxLayout()
        tab5Layout.addLayout(appresLayout)
        tab5Layout.addLayout(webrenlogLayout)

        ############################  TABS LAYOUT
        self.TabWidget = QTabWidget()
        C0Widget = QWidget()
        C0Widget.setLayout(tab0Layout)
        tab0Layout.setContentsMargins(10,10,10,10)
        C0Widget.setContentsMargins(0,10,0,10)
        self.TabWidget.addTab(C0Widget,QApplication.translate("Tab","RoR",None))
        C1Widget = QWidget()
        C1Widget.setLayout(tab1Layout)
        tab1Layout.setContentsMargins(10,10,10,10)
        C1Widget.setContentsMargins(0,10,0,10)
        self.TabWidget.addTab(C1Widget,QApplication.translate("Tab","Filters",None))
        C11Widget = QWidget()
        C11Widget.setLayout(tab11Layout)
        tab11Layout.setContentsMargins(10,10,10,10)
        C11Widget.setContentsMargins(0,10,0,10)
        self.TabWidget.addTab(C11Widget,QApplication.translate("Tab","HUD",None))
        C2Widget = QWidget()
        C2Widget.setLayout(tab2Layout)
        tab2Layout.setContentsMargins(10,10,10,10)
        C2Widget.setContentsMargins(0,0,0,0)
        self.TabWidget.addTab(C2Widget,QApplication.translate("Tab","Plotter",None))
        C3Widget = QWidget()
        C3Widget.setLayout(tab3Layout)
        tab3Layout.setContentsMargins(10,10,10,10)
        C3Widget.setContentsMargins(0,0,0,0)
        self.TabWidget.addTab(C3Widget,QApplication.translate("Tab","Math",None))
        C4Widget = QWidget()
        C4Widget.setLayout(tab4Layout)
        tab4Layout.setContentsMargins(10,10,10,10)
        C3Widget.setContentsMargins(0,0,0,0)
        self.TabWidget.addTab(C4Widget,QApplication.translate("Tab","Analyze",None))
        C5Widget = QWidget()
        C5Widget.setLayout(tab5Layout)
        tab5Layout.setContentsMargins(10,10,10,10)
        C5Widget.setContentsMargins(0,10,0,0)
        self.TabWidget.addTab(C5Widget,QApplication.translate("Tab","UI",None))
        buttonsLayout = QHBoxLayout()
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(self.dialogbuttons)
        #incorporate layouts
        Slayout = QVBoxLayout()
        Slayout.addWidget(self.TabWidget,1)
        Slayout.addStretch()
        Slayout.addLayout(buttonsLayout)
        self.TabWidget.currentChanged.connect(self.tabSwitched)
        self.setLayout(Slayout)
        
        self.TabWidget.setContentsMargins(0,0,0,0)
        Slayout.setContentsMargins(5,15,5,5)
        Slayout.setSpacing(5)

        self.updatePlotterleftlabels()  
         
        self.startEdit.editingFinished.connect(self.startEditChanged)
        self.endEdit.editingFinished.connect(self.endEditChanged)
        self.polyfitdeg.valueChanged.connect(self.polyfitcurveschanged)
        self.c1ComboBox.currentIndexChanged.connect(self.polyfitcurveschanged)
        self.c2ComboBox.currentIndexChanged.connect(self.polyfitcurveschanged)
        if platform.system() != 'Windows':
            self.dialogbuttons.button(QDialogButtonBox.Ok).setFocus()
            
        settings = QSettings()
        if settings.contains("CurvesPosition"):
            self.move(settings.value("CurvesPosition"))
        
        self.TabWidget.setCurrentIndex(activeTab)
        
        Slayout.setSizeConstraint(QLayout.SetFixedSize)

    @pyqtSlot(bool)
    def fittoBackground(self,_):
        if len(self.expresult.text()) > 0:
            self.aw.deleteBackground
            self.setbackgroundequ1(mathequ=True)
            QApplication.processEvents()  #occasionally the fit curve remains showing.
            self.aw.qmc.redraw(recomputeAllDeltas=True)
            #self.updatetargets()  #accept and close dialog
        else:
            return
    
    @pyqtSlot(int)
    def changeAnalyzecombobox(self,i):
        self.aw.qmc.analysisstartchoice = i
        if i == 2:  # Custom
            self.analyzetimeoffset.setEnabled(True)
        else:
            self.analyzetimeoffset.setEnabled(False)
        return
        
    @pyqtSlot()
    def analyzetimeoffsetChanged(self):
        try:
            self.aw.qmc.analysisoffset = int(self.analyzetimeoffset.text())
        except:
            pass
        return
        
    @pyqtSlot(int)
    def changeCurvefitcombobox(self,i):
        self.aw.qmc.curvefitstartchoice = i
        if i == 2:  # Custom
            self.curvefittimeoffset.setEnabled(True)
        else:
            self.curvefittimeoffset.setEnabled(False)
        return
        
    @pyqtSlot()
    def segmentsamplesthresholdChanged(self):
        self.aw.qmc.segmentsamplesthreshold = int(self.segmentsamplesthreshold.text())
        return
        
    @pyqtSlot()
    def segmentdeltathresholdChanged(self):
        self.aw.qmc.segmentdeltathreshold = self.aw.float2float(toFloat(self.segmentdeltathreshold.text(),),4)
        return
        
    @pyqtSlot()
    def curvefittimeoffsetChanged(self):
        try:
            self.aw.qmc.curvefitoffset = int(self.curvefittimeoffset.text())
        except:
            pass
        return
        
    @pyqtSlot()
    def exptimeoffsetChanged(self):
        self.expvarCheck.setChecked(False)
        self.expvar(0)
        self.expvarCheck.setChecked(True)
        self.expvar(0)
    
    @pyqtSlot(bool)
    def expradiobuttonClicked(self,_=False):
        self.expradioButton = self.sender()
        if self.expradioButton.isChecked():
            self.exppower = self.expradioButton.power
            self.expvarCheck.setChecked(False)
            self.expvar(0)
            self.expvarCheck.setChecked(True)
            self.expvar(0)

    #watermark image
    @pyqtSlot(bool)
    def logofileload(self,_):
        self.aw.qmc.logoloadfile()
        self.logopathedit.setText(str(self.aw.logofilename))
        # note the logo is only visible after a full redraw
    
    @pyqtSlot(bool)
    def logofiledelete(self,_):
        self.logopathedit.setText("")
        self.aw.logofilename = ""
        self.aw.qmc.redraw(recomputeAllDeltas=False)
    
    @pyqtSlot()
    def changelogoalpha(self):
        self.aw.logoimgalpha = self.logoalpha.value()
        self.aw.qmc.redraw(recomputeAllDeltas=False)
    
    @pyqtSlot(int)
    def changelogoshowCheck(self,_):
        self.aw.logoimgflag = not self.aw.logoimgflag

    @pyqtSlot()
    def renameBT(self):
        self.aw.BTname = str(self.renameBTLine.text()).strip()
        if self.aw.BTname == "":
            self.aw.BTname = QApplication.translate("Label", "BT")
        self.aw.label3.setText("<big><b>" + self.aw.BTname + "</b></big>")
        self.aw.label5.setText(deltaLabelBigPrefix + self.aw.BTname + "</b></big>")

    @pyqtSlot()
    def renameET(self):
        self.aw.ETname = str(self.renameETLine.text()).strip()
        if self.aw.ETname == "":
            self.aw.ETname = QApplication.translate("Label", "ET")
        self.aw.label2.setText("<big><b>" + self.aw.ETname + "</b></big>")
        self.aw.label4.setText(deltaLabelBigPrefix + self.aw.ETname + "</b></big>")

    @pyqtSlot(int)
    def toggleWebLCDsAlerts(self,_):
        self.aw.WebLCDsAlerts = not self.aw.WebLCDsAlerts
    
    @pyqtSlot()
    def changeWebLCDsPort(self):
        self.aw.WebLCDsPort = int(str(self.WebLCDsPort.text()))
        
    def setWebLCDsURL(self):
        url_str = self.getWebLCDsURL()
        # set URL label
        self.WebLCDsURL.setText('<a href="' + url_str + '">' + url_str + '</a>')
        # set QR label 
        from artisanlib.qrcode import QRlabel
        qr = QRlabel(url_str)
        self.QRpic.setPixmap(qr.make_image().pixmap())
        
    def getWebLCDsURL(self):
        import socket
        localIP = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
        return 'http://' + str(localIP) + ':' + str(self.aw.WebLCDsPort) + '/artisan'

    @pyqtSlot(bool)
    def toggleWebLCDs(self,b):
        if b:
            try:
                res = self.aw.startWebLCDs()
                if not res:
                    self.WebLCDsPort.setDisabled(False)
                    self.WebLCDsURL.setText("")
                    self.QRpic.setPixmap(QPixmap())
                    self.WebLCDsFlag.setChecked(False)
                    self.WebLCDsAlerts.setDisabled(True)
                else:
                    self.setWebLCDsURL() # this might fail if socket cannot be established
                    self.WebLCDsAlerts.setDisabled(False)
                    self.WebLCDsPort.setDisabled(True)
                    self.WebLCDsFlag.setChecked(True)
            except Exception as e:
                self.aw.sendmessage(str(e))
                self.WebLCDsAlerts.setDisabled(True)
                self.WebLCDsFlag.setChecked(False)
                self.WebLCDsPort.setDisabled(False)
                self.WebLCDsURL.setText("")
                self.QRpic.setPixmap(QPixmap())
                self.aw.WebLCDs = False
        else:   
            self.WebLCDsAlerts.setDisabled(True)
            self.WebLCDsFlag.setChecked(False)
            self.WebLCDsPort.setDisabled(False)
            self.WebLCDsURL.setText("")
            self.QRpic.setPixmap(QPixmap())
            self.aw.stopWebLCDs()
    
    @pyqtSlot(int)
    def showHUDbuttonToggle(self,i):
        if i:
            self.aw.qmc.HUDbuttonflag = True
            if not self.app.artisanviewerMode:
                self.aw.button_18.setVisible(True)
        else:
            self.aw.qmc.HUDbuttonflag = False
            self.aw.button_18.setVisible(False)

    def changedpi(self):
        try:
            value = self.resolutionSpinBox.value()
            self.aw.setdpi(value)
            self.aw.qmc.redraw(recomputeAllDeltas=False)
        except Exception as e:
            _, _, exc_tb = sys.exc_info()
            self.aw.qmc.adderror((QApplication.translate("Error Message", "Exception:",None) + " changedpi(): {0}").format(str(e)),exc_tb.tb_lineno)

    @pyqtSlot(bool)
    def setcurvecolor0(self,_=False):
        self.setcurvecolor(0)
    @pyqtSlot(bool)
    def setcurvecolor1(self,_=False):
        self.setcurvecolor(1)
    @pyqtSlot(bool)
    def setcurvecolor2(self,_=False):
        self.setcurvecolor(2)
    @pyqtSlot(bool)
    def setcurvecolor3(self,_=False):
        self.setcurvecolor(3)
    @pyqtSlot(bool)
    def setcurvecolor4(self,_=False):
        self.setcurvecolor(4)
    @pyqtSlot(bool)
    def setcurvecolor5(self,_=False):
        self.setcurvecolor(5)
    @pyqtSlot(bool)
    def setcurvecolor6(self,_=False):
        self.setcurvecolor(6)
    @pyqtSlot(bool)
    def setcurvecolor7(self,_=False):
        self.setcurvecolor(7)
    @pyqtSlot(bool)
    def setcurvecolor8(self,_=False):
        self.setcurvecolor(8)
        
    def setcurvecolor(self,x):
        try:
            colorf = self.aw.colordialog(QColor(self.aw.qmc.plotcurvecolor[x]))
            if colorf.isValid():
                colorname = str(colorf.name())
                self.aw.qmc.plotcurvecolor[x] = colorname
                #refresh right color labels
                self.equc1colorlabel.setStyleSheet("background-color:'%s';"%self.aw.qmc.plotcurvecolor[0])
                self.equc2colorlabel.setStyleSheet("background-color:'%s';"%self.aw.qmc.plotcurvecolor[1])
                self.equc3colorlabel.setStyleSheet("background-color:'%s';"%self.aw.qmc.plotcurvecolor[2])
                self.equc4colorlabel.setStyleSheet("background-color:'%s';"%self.aw.qmc.plotcurvecolor[3])
                self.equc5colorlabel.setStyleSheet("background-color:'%s';"%self.aw.qmc.plotcurvecolor[4])
                self.equc6colorlabel.setStyleSheet("background-color:'%s';"%self.aw.qmc.plotcurvecolor[5])
                self.equc7colorlabel.setStyleSheet("background-color:'%s';"%self.aw.qmc.plotcurvecolor[6])
                self.equc8colorlabel.setStyleSheet("background-color:'%s';"%self.aw.qmc.plotcurvecolor[7])
                self.equc9colorlabel.setStyleSheet("background-color:'%s';"%self.aw.qmc.plotcurvecolor[8])

            self.plotequ()
        except Exception as e:
            _, _, exc_tb = sys.exc_info()
            self.aw.qmc.adderror((QApplication.translate("Error Message", "Exception:",None) + " setcurvecolor(): {0}").format(str(e)),exc_tb.tb_lineno)

    def update_equbuttons(self):
        self.equvdevicebutton.setFocusPolicy(Qt.NoFocus)
        if len(self.aw.qmc.timex) < 2: # empty profile
            self.equvdevicebutton.setEnabled(True)
            self.equvdevicebutton.setText(QApplication.translate("Button","ET/BT",None))
            self.equvdevicebutton.setToolTip(QApplication.translate("Tooltip","Add P1 and P2 as ET and BT",None))
        else:
            self.equvdevicebutton.setText(QApplication.translate("Button","Create Virtual\nExtra Device",None))
            if len(self.aw.qmc.extradevices) < self.aw.nLCDS:  #not at maximimum of virtual devices
                self.equvdevicebutton.setEnabled(True)
                self.equvdevicebutton.setToolTip(QApplication.translate("Tooltip","Add P1 and P2 as:\n\n1 an Extra virtual device if a profile is loaded\n2 or ET and BT if profile is not loaded\n",None))
            else:
                self.equvdevicebutton.setEnabled(False)
                self.equvdevicebutton.setToolTip(QApplication.translate("Tooltip","No more Virtual Extra Devices available",None))
        if self.aw.qmc.flagon:
            self.equvdevicebutton.setEnabled(False)
            self.equvdevicebutton.setToolTip(QApplication.translate("Tooltip","Not available during recording",None))
            self.equbackgroundbutton.setEnabled(False)
            self.equbackgroundbutton.setToolTip(QApplication.translate("Tooltip","Not available during recording",None))
        else:
            self.equbackgroundbutton.setEnabled(True)
            self.equbackgroundbutton.setToolTip(QApplication.translate("Tooltip","Set P1 as ET background B1\nSet P2 as BT background B2\nNote: Erases all existing background curves.",None))                

        if self.equvdevicebutton.isEnabled():
            self.equvdevicebutton.clicked.connect(self.setvdevice)
        else:
            try:
                self.equvdevicebutton.disconnect()
            except:
                pass
   
    @pyqtSlot(bool)
    def setvdevice(self,_):
        # compute values
        if len(self.aw.qmc.timex) < 2: # empty profile
            # we use the background function to set it to ET/BT
            self.setbackgroundequ1(foreground=True)
        else:
            # Check for incompatible vars from in the equations
            EQU = [str(self.equedit1.text()),str(self.equedit2.text())]
            incompatiblevars = ["P","F","$","#"]
            error = ""
            for i in range(len(incompatiblevars)):
                if incompatiblevars[i] in EQU[0]:
                    error = "P1: \n-%s\n\n[%s]"%(incompatiblevars[i],EQU[0])
                elif incompatiblevars[i] in EQU[1]:
                    error = "P2: \n%-s\n\n[%s]"%(incompatiblevars[i],EQU[1])
                    
            if error:
                string = QApplication.translate("Message","Incompatible variables found in %s"%error, None)
                QMessageBox.warning(self,QApplication.translate("Message","Assignment problem", None),string,
                                    QMessageBox.Discard)
                
            else:
                for e in range(2):
                    #create y range
                    y_range = []
                    if self.aw.qmc.timeindex[0] > -1:
                        toff = self.aw.qmc.timex[self.aw.qmc.timeindex[0]]
                    else:
                        toff = 0
                    for i in range(len(self.aw.qmc.timex)):
                        y_range.append(self.aw.qmc.eval_math_expression(EQU[e],self.aw.qmc.timex[i],t_offset=toff))
                    if e:
                        extratemp2 = y_range
                    else:
                        extratemp1 = y_range
                # add device
                self.aw.addDevice() 
                self.aw.qmc.extradevices[-1] = 25
                
                # set colors
                self.aw.qmc.extradevicecolor1[-1] = self.aw.qmc.plotcurvecolor[0]
                self.aw.qmc.extradevicecolor2[-1] = self.aw.qmc.plotcurvecolor[1]
                # set expressions
                self.aw.qmc.extramathexpression1[-1] = str(self.equedit1.text())
                self.aw.qmc.extramathexpression2[-1] = str(self.equedit2.text())
                # set values
                self.aw.qmc.extratemp1[-1] = extratemp1
                self.aw.qmc.extratemp2[-1] = extratemp2
                self.aw.qmc.extratimex[-1] = self.aw.qmc.timex[:]
                # redraw
                self.aw.qmc.redraw(recomputeAllDeltas=False)

                self.aw.sendmessage(QApplication.translate("Message","New Extra Device: virtual: y1(x) =[%s]; y2(x)=[%s]"%(EQU[0],EQU[1]), None))

        self.aw.calcVirtualdevices()
        self.update_equbuttons()

    @pyqtSlot(bool)
    def equshowtable(self,_=False):
        equdataDlg = equDataDlg(self,self.aw)
        equdataDlg.resize(500, 500)
        equdataDlg.show()
        equdataDlg.activateWindow()

    @pyqtSlot(bool)
    def setbackgroundequ1_slot(self,_):
        self.setbackgroundequ1()
        
    def setbackgroundequ1(self,foreground=False, mathequ=False):
        EQU = [str(self.equedit1.text()),str(self.equedit2.text())]
        if mathequ:
            EQU = [str(""),str(self.expresult.text())]
        self.aw.qmc.analysisresultsstr = ""
        self.aw.setbackgroundequ(foreground=foreground, EQU=EQU)

    def updatePlotterleftlabels(self):
        if len(self.aw.qmc.plotterequationresults[0]):
            self.equc1label.setStyleSheet("background-color:'lightgrey';")
        else:
            self.equc1label.setStyleSheet("background-color:'transparent';")
        if len(self.aw.qmc.plotterequationresults[1]):
            self.equc2label.setStyleSheet("background-color:'lightgrey';")
        else:
            self.equc2label.setStyleSheet("background-color:'transparent';")
        if len(self.aw.qmc.plotterequationresults[2]):
            self.equc3label.setStyleSheet("background-color:'lightgrey';")
        else:
            self.equc3label.setStyleSheet("background-color:'transparent';")
        if len(self.aw.qmc.plotterequationresults[3]):
            self.equc4label.setStyleSheet("background-color:'lightgrey';")
        else:
            self.equc4label.setStyleSheet("background-color:'transparent';")
        if len(self.aw.qmc.plotterequationresults[4]):
            self.equc5label.setStyleSheet("background-color:'lightgrey';")
        else:
            self.equc5label.setStyleSheet("background-color:'transparent';")
        if len(self.aw.qmc.plotterequationresults[5]):
            self.equc6label.setStyleSheet("background-color:'lightgrey';")
        else:
            self.equc6label.setStyleSheet("background-color:'transparent';")
        if len(self.aw.qmc.plotterequationresults[6]):
            self.equc7label.setStyleSheet("background-color:'lightgrey';")
        else:
            self.equc7label.setStyleSheet("background-color:'transparent';")
        if len(self.aw.qmc.plotterequationresults[7]):
            self.equc8label.setStyleSheet("background-color:'lightgrey';")
        else:
            self.equc8label.setStyleSheet("background-color:'transparent';")
        if len(self.aw.qmc.plotterequationresults[8]):
            self.equc9label.setStyleSheet("background-color:'lightgrey';")
        else:
            self.equc9label.setStyleSheet("background-color:'transparent';")


    # format = annotate(text,time,temp,size)
    # eg annotation = 'annotate(H,03:00,200,10)'
    def plotterannotation(self,annotation,cindex):
        try:
            annotation = annotation.strip()
            if len(annotation) > 20:
                annotation = annotation[9:]                # annotate(
                annotation = annotation[:len(annotation)-1] # )
                annvars = [e.strip() for e in annotation.split(',')]
                text = annvars[0]
                if self.aw.qmc.timeindex[0] != -1 and len(self.aw.qmc.timex):
                    time = float(stringtoseconds(annvars[1])+ self.aw.qmc.timex[self.aw.qmc.timeindex[0]])
                else:
                    time = float(stringtoseconds(annvars[1]))
                temp = float(annvars[2])
                fsize = 12
                try:
                    fsize = int(annvars[3])
                except:
                    pass
                anno = self.aw.qmc.ax.annotate(text, xy=(time,temp),xytext=(time,temp),alpha=5.,color=self.aw.qmc.plotcurvecolor[cindex],fontsize=fsize)
                try:
                    anno.set_in_layout(False)  # remove text annotations from tight_layout calculation
                except: # mpl before v3.0 do not have this set_in_layout() function
                    pass
#            else:
#                self.aw.qmc.plottermessage = QApplication.translate("Error Message","Plotter: incorrect syntax: annotate(text,time,temperature,fontsize)", None)
        except Exception as e:
            _, _, exc_tb = sys.exc_info()
            self.aw.qmc.adderror((QApplication.translate("Error Message", "Exception:",None) + " annotate() syntax: {0}").format(str(e)),exc_tb.tb_lineno)

    def plotterb(self):
        try:
            self.aw.sendmessage("Dropping beans...")
            colorb = ["#996633","#4d2600","#4b4219","black","#4b3219","#996633","#281a0d"]
            for _ in range(3): # number of bean layers (each a randomly different color)
                x = self.aw.qmc.endofx*numpy.random.rand(self.aw.qmc.endofx/6)
                y = self.aw.qmc.ylimit*numpy.random.rand(self.aw.qmc.endofx/6)
                self.aw.qmc.ax.plot(x,y,'o',color=colorb[int(round(6*numpy.random.rand(1)[0]))])
        except Exception as e:
            _, _, exc_tb = sys.exc_info()
            self.aw.qmc.adderror((QApplication.translate("Error Message", "Exception:",None) + " plotterb() syntax: {0}").format(str(e)),exc_tb.tb_lineno)

    def plotterprogram(self,program,e):
        try:
            #remove enclosing brackets {}
            program = program[1:len(program)-1]
            
            #"if 2 > 1: a = \"OXXX\"; print a"
            p = compile(program,"a","exec")
            exec(p)
        except Exception as e:
            _, _, exc_tb = sys.exc_info()
            self.aw.qmc.adderror((QApplication.translate("Error Message", "Exception:",None) + " plotterprogram(): {0}").format(str(e)),exc_tb.tb_lineno)

    @pyqtSlot(bool)
    def plotequ(self,_=False):
        try:
            self.aw.qmc.plotterstack = [0]*10
#            self.aw.qmc.plottermessage = ""
            self.aw.clearMessageLine()

            self.aw.qmc.plotterequationresults = [[],[],[],[],[],[],[],[],[]]
            EQU = [str(self.equedit1.text()),str(self.equedit2.text()),
                   str(self.equedit3.text()),str(self.equedit4.text()),
                   str(self.equedit5.text()),str(self.equedit6.text()),
                   str(self.equedit7.text()),str(self.equedit8.text()),
                   str(self.equedit9.text())]
            self.aw.qmc.resetlines()

            commentoutplot = [0]*9      # "#" as first char does not evaluate plot nor show it. Allows to keep formula on window without eval (ie. long filters)
            hideplot = [0]*9            # "$" as first char evaluates plot but does not show it. Useful to hide intermediate results

            # 9 plots
            for e in range(9):
                eqs = EQU[e].strip()
                if eqs:
                    if eqs[0] == "$":
                        hideplot[e] = 1
                        eqs = eqs[1:] #removes "$"
                    if eqs[0] == "#":
                        commentoutplot[e] = 1
                    #commands
                    if len(eqs) > 10 and eqs[:9] == "annotate(":
                        commentoutplot[e] = 1
                        self.plotterannotation(eqs,e)
                    if len(eqs) > 4 and eqs[:5] == "beans":
                        commentoutplot[e] = 1
                        self.plotterb()
                    if eqs[0] == "{" and eqs[len(eqs)-1] == "}":
                        self.plotterprogram(eqs,e)

                    toff = 0
                    #create x range and set the time offset generated by CHARGE
                    if len(self.aw.qmc.timex):
                        x_range = self.aw.qmc.timex
                        if self.aw.qmc.timeindex[0] > -1:
                            toff = self.aw.qmc.timex[self.aw.qmc.timeindex[0]]
                    elif len(self.aw.qmc.timeB):
                        x_range = self.aw.qmc.timeB
                        if self.aw.qmc.timeindexB[0] > -1:
                            toff = self.aw.qmc.timeB[self.aw.qmc.timeindexB[0]]
                    else:
                        x_range = list(range(int(self.aw.qmc.startofx),int(self.aw.qmc.endofx)))
                    #create y range
                    y_range = []

                    if not commentoutplot[e]:
                        for i in range(len(x_range)):
                            y_range.append(self.aw.qmc.eval_math_expression(eqs,x_range[i],equeditnumber=e+1,t_offset=toff)) #pass e+1 = equeditnumber(1-9)
                        if not hideplot[e]:
                            self.aw.qmc.ax.plot(x_range, y_range, color=self.aw.qmc.plotcurvecolor[e], linestyle = '-', linewidth=1)
                    
            self.aw.qmc.fig.canvas.draw()
            self.updatePlotterleftlabels()
#            self.equlabel.setText(self.aw.qmc.plottermessage)

        except Exception as e:
            _, _, exc_tb = sys.exc_info()
            self.aw.qmc.adderror((QApplication.translate("Error Message", "Exception:",None) + " plotequ(): {0}").format(str(e)),exc_tb.tb_lineno)

    @pyqtSlot(int)
    def setappearance(self,_):
        try:
            self.app.setStyle(str(self.styleComboBox.currentText()))
            self.aw.appearance = str(self.styleComboBox.currentText()).lower()
        except Exception as e:
            _, _, exc_tb = sys.exc_info() 
            self.aw.qmc.adderror((QApplication.translate("Error Message", "Exception:",None) + " setappearance(): {0}").format(str(e)),exc_tb.tb_lineno)

    @pyqtSlot(bool)
    def showunivarinfo(self,_):
        if self.aw.qmc.timeindex[0] > -1 and self.aw.qmc.timeindex[6]:
            self.aw.qmc.univariateinfo()
        else:
            self.aw.sendmessage(QApplication.translate("Univariate: no profile data available", None))
    
    @pyqtSlot(int)
    def lnvar(self,_):
        if self.lnvarCheck.isChecked():
            #check for finished roast
            if self.aw.qmc.timeindex[0] > -1:
                try:
                    curvefit_starttime = int(self.exptimeoffset.text()) + self.aw.qmc.timex[self.aw.qmc.timeindex[0]]
                except:
                    curvefit_starttime = 0
                res = self.aw.qmc.lnRegression(curvefit_starttime=curvefit_starttime)
                self.lnresult.setText(res)
            else:
                self.aw.sendmessage(QApplication.translate("Error Message", "ln(): no profile data available", None))
                self.lnvarCheck.setChecked(False)
                self.lnresult.setText("")
        else:
            self.lnresult.setText("")
            self.aw.qmc.resetlines()
            self.redraw_enabled_math_curves()

    @pyqtSlot(int)
    def expvar(self,_):
        if self.expvarCheck.isChecked():
            #check for finished roast
            if self.aw.qmc.timeindex[0] > -1 and self.aw.qmc.timeindex[6]:
                try:
                    curvefit_starttime = int(self.exptimeoffset.text()) + self.aw.qmc.timex[self.aw.qmc.timeindex[0]]
                except:
                    curvefit_starttime = 0
                res = self.aw.qmc.lnRegression(power=self.exppower, curvefit_starttime=curvefit_starttime)
                self.expresult.setText(res)
                self.bkgndButton.setEnabled(True)
            else:
                self.aw.sendmessage(QApplication.translate("Error Message", "expvar(): no profile data available", None))
                self.expvarCheck.setChecked(False)
                self.expresult.setText("")
                self.bkgndButton.setEnabled(False)
        else:
            self.expresult.setText("")
            self.aw.qmc.resetlines()
            self.redraw_enabled_math_curves()
            self.bkgndButton.setEnabled(False)
    
    @pyqtSlot(int)
    def univar(self,_):
        if self.univarCheck.isChecked():
            #check for finished roast
            if self.aw.qmc.timeindex[0] > -1 and self.aw.qmc.timeindex[6]:
                self.aw.qmc.univariate()
            else:
                self.aw.sendmessage(QApplication.translate("Error Message", "Univariate: no profile data available", None))
                self.univarCheck.setChecked(False)
        else:
            self.aw.qmc.resetlines()
            self.redraw_enabled_math_curves()

    def redraw_enabled_math_curves(self):
        if self.interpCheck.isChecked():
            self.aw.qmc.drawinterp(str(self.interpComboBox.currentText()))
        if self.univarCheck.isChecked():
            self.aw.qmc.univariate()
        if self.lnvarCheck.isChecked():
            self.lnvar(0)
        if self.expvarCheck.isChecked():
            self.expvar(0)
        if self.polyfitCheck.isChecked():
            self.doPolyfit()
        if not self.polyfitCheck.isChecked() and not self.expvarCheck.isChecked() and not self.lnvarCheck.isChecked() and not self.univarCheck.isChecked() and not self.interpCheck.isChecked():
            self.aw.qmc.resetlines()
            self.aw.qmc.redraw(recomputeAllDeltas=False)
    
    @pyqtSlot()
    def startEditChanged(self):
        self.eventAComboBox.blockSignals(True)
        self.eventAComboBox.setDisabled(True)
        self.eventAComboBox.setCurrentIndex(0)
        self.eventAComboBox.setDisabled(False)
        self.eventAComboBox.blockSignals(False)
        self.polyfitcurveschanged(0)

    @pyqtSlot()
    def endEditChanged(self):
        self.eventBComboBox.blockSignals(True)
        self.eventBComboBox.setDisabled(True)
        self.eventBComboBox.setCurrentIndex(0)
        self.eventBComboBox.setDisabled(False)
        self.eventBComboBox.blockSignals(False)
        self.polyfitcurveschanged(0)

    @pyqtSlot(int)
    def polyfitRoRflagChanged(self,_):
        self.polyfitRoR = self.polyfitRoRflag.isChecked()
        self.polyfitcurveschanged(0)

    @pyqtSlot(int)
    def calcEventRC(self,_):
        if self.aw.qmc.timeindex[0] != -1:
            start = self.aw.qmc.timex[self.aw.qmc.timeindex[0]]
        else:
            start = 0
        
        Aevent = int(self.eventAComboBox.currentIndex())
        if Aevent != 0:
            a = self.events[Aevent-1][1]
            self.startEdit.blockSignals(True)
            self.startEdit.setDisabled(True)
            self.startEdit.setText(stringfromseconds(self.aw.qmc.timex[a] - start))
            self.startEdit.setDisabled(False)
            self.startEdit.blockSignals(False)
                        
        Bevent = int(self.eventBComboBox.currentIndex())
        if Bevent != 0:
            b = self.events[Bevent-1][1]
            self.endEdit.blockSignals(True)
            self.endEdit.setDisabled(True)
            self.endEdit.setText(stringfromseconds(self.aw.qmc.timex[b] - start))
            self.endEdit.setDisabled(False)
            self.endEdit.blockSignals(False)
        self.polyfitcurveschanged(0)

    def eventlist(self):
        events = []
        if self.aw.qmc.timeindex[0] > -1:
            events.append((QApplication.translate("Table", "CHARGE",None),self.aw.qmc.timeindex[0]))
        names = [
            QApplication.translate("Table", "DRY END",None),
            QApplication.translate("Table", "FC START",None),
            QApplication.translate("Table", "FC END",None),
            QApplication.translate("Table", "SC START",None),
            QApplication.translate("Table", "SC END",None),
            QApplication.translate("Table", "DROP",None),
            QApplication.translate("Table", "COOL",None)]
        for e in range(len(names)):
            if self.aw.qmc.timeindex[e+1]:
                events.append((names[e],self.aw.qmc.timeindex[e+1]))
        for e in range(len(self.aw.qmc.specialevents)):
            events.append(("{} {}".format(QApplication.translate("Label", "EVENT",None),str(e+1)),self.aw.qmc.specialevents[e]))
        return events

    def doPolyfit(self):
        l = min(len(self.aw.qmc.timex),len(self.curves[self.c1ComboBox.currentIndex()]),len(self.curves[self.c2ComboBox.currentIndex()]))
        starttime = stringtoseconds(str(self.startEdit.text()))
        endtime = stringtoseconds(str(self.endEdit.text()))
        if starttime == -1 or endtime == -1:
            self.result.setText("")
            self.result.repaint()
            return
        if  endtime > self.aw.qmc.timex[-1] or endtime < starttime:
            self.result.setText("")
            self.result.repaint()
            return
        if self.aw.qmc.timeindex[0] != -1:
            start = self.aw.qmc.timex[self.aw.qmc.timeindex[0]]
        else:
            start = 0
        startindex = self.aw.qmc.time2index(starttime + start)
        endindex = min(l,self.aw.qmc.time2index(endtime + start))
        c1 = self.curves[self.c1ComboBox.currentIndex()]
        c2 = self.curves[self.c2ComboBox.currentIndex()]
        z = self.aw.qmc.polyfit(c1,c2,
               self.polyfitdeg.value(),startindex,endindex,self.deltacurves[self.c2ComboBox.currentIndex()],onDeltaAxis=self.polyfitRoR)
        res = True
        if z is not None:
            for e in z:
                if numpy.isnan(e):
                    res = False
                    return False
        if res and z is not None:
            s = self.aw.fit2str(z)
            self.result.setText(s)
            self.result.repaint()
            return True
        else:
            self.result.setText("")
            self.result.repaint()
            return False

    @pyqtSlot()
    @pyqtSlot(int)
    def polyfitcurveschanged(self,_=0):
        self.polyfitdeg.blockSignals(True)
        self.polyfitdeg.setDisabled(True)
        self.startEdit.blockSignals(True)
        self.startEdit.setDisabled(True)
        self.endEdit.blockSignals(True)
        self.endEdit.setDisabled(True)
        try:
            if self.polyfitCheck.isChecked() and len(self.aw.qmc.timex) > 2:
                QApplication.processEvents()
                res = self.doPolyfit()
                if not res:
                    self.polyfitCheck.setChecked(False)
                    self.result.setText("")
                    self.result.repaint()
                    self.aw.qmc.resetlines()
                QApplication.processEvents()
            else:
                self.polyfitCheck.setChecked(False)
                self.result.setText("")
                self.result.repaint()
                self.aw.qmc.resetlines()
        except Exception:
            pass
        self.startEdit.setDisabled(False)
        self.startEdit.blockSignals(False)
        self.endEdit.setDisabled(False)
        self.endEdit.blockSignals(False)
        self.polyfitdeg.setDisabled(False)
        self.polyfitdeg.blockSignals(False)
        self.polyfitdeg.setFocus()

    @pyqtSlot(int)
    def tabSwitched(self,i):
        self.closeHelp()
        if i != 4:
            if self.polyfitCheck.isChecked():
                self.polyfitCheck.setChecked(False)
            if self.expvarCheck.isChecked():
                self.expvarCheck.setChecked(False)
            if self.lnvarCheck.isChecked():
                self.lnvarCheck.setChecked(False)
            if self.interpCheck.isChecked():
                self.interpCheck.setChecked(False)
            if self.univarCheck.isChecked():
                self.univarCheck.setChecked(False)
        else:
            self.collectCurves()

    # TODO: add background curves temp1B, temp2B, timeB, delta1B, delta2B (could be of different size!)
    def collectCurves(self):
        idx = 0
        self.curves = []
        self.curvenames = []
        self.deltacurves = [] # list of flags. True if delta curve, False otherwise
        if self.aw.qmc.DeltaETflag:
            self.curvenames.append(deltaLabelUTF8 + QApplication.translate("Label","ET",None))
            self.curves.append(self.aw.qmc.delta1)
            self.deltacurves.append(True)
            idx = idx + 1
        if self.aw.qmc.DeltaBTflag:
            self.curvenames.append(deltaLabelUTF8 + QApplication.translate("Label","BT",None))
            self.curves.append(self.aw.qmc.delta2)
            self.deltacurves.append(True)
            idx = idx + 1
        self.curvenames.append(QApplication.translate("ComboBox","ET",None))
        self.curvenames.append(QApplication.translate("ComboBox","BT",None))
        self.curves.append(self.aw.qmc.temp1)
        self.curves.append(self.aw.qmc.temp2)
        self.deltacurves.append(False)
        self.deltacurves.append(False)
        for i in range(len(self.aw.qmc.extradevices)):
            self.curvenames.append(str(i) + "xT1: " + self.aw.qmc.extraname1[i])
            self.curvenames.append(str(i) + "xT2: " + self.aw.qmc.extraname2[i])
            self.curves.append(self.aw.qmc.extratemp1[i])
            self.curves.append(self.aw.qmc.extratemp2[i])
            self.deltacurves.append(False)
            self.deltacurves.append(False)
        self.c1ComboBox.setDisabled(True) #blockSignals(True)
        self.c2ComboBox.setDisabled(True) #blockSignals(True)
        self.c1ComboBox.clear()
        self.c1ComboBox.addItems(self.curvenames)
        self.c2ComboBox.clear()
        self.c2ComboBox.addItems(self.curvenames)
        self.c1ComboBox.setDisabled(False) #blockSignals(False)
        self.c2ComboBox.setDisabled(False) #blockSignals(False)
        self.c1ComboBox.setCurrentIndex(idx)
        self.c2ComboBox.setCurrentIndex(idx+1)

    @pyqtSlot(bool)
    def polyfit(self,_):
        try:
            if self.polyfitCheck.isChecked():
                #check for finished roast
                if len(self.aw.qmc.timex) > 2:
                    res = self.doPolyfit()
                    if not res:
                        self.polyfitCheck.setChecked(False)
                        self.aw.qmc.resetlines()
                        self.redraw_enabled_math_curves()
                else:
                    self.aw.sendmessage(QApplication.translate("Error Message", "Polyfit: no profile data available", None))
                    self.polyfitCheck.setChecked(False)
            else:
                self.result.setText("")
                self.result.repaint()
                self.aw.qmc.resetlines()
                self.redraw_enabled_math_curves()
        except Exception:
#            import traceback
#            traceback.print_exc(file=sys.stdout)
            pass
    
    @pyqtSlot(int)
    def interpolation(self,_=0):
        mode = str(self.interpComboBox.currentText())
        if self.interpCheck.isChecked():
            #check for finished roast
            if self.aw.qmc.timeindex[6]:
                self.aw.qmc.drawinterp(mode)
            else:
                self.aw.sendmessage(QApplication.translate("Message","Interpolation failed: no profile available", None))
                self.interpCheck.setChecked(False)
        else:
            self.aw.qmc.resetlines()
            self.redraw_enabled_math_curves()

    @pyqtSlot(int)
    def soundset(self,_):
        if self.aw.soundflag == 0:
            self.aw.soundflag = 1
            self.aw.sendmessage(QApplication.translate("Message","Sound turned ON", None))
            self.aw.soundpop()
        else:
            self.aw.soundflag = 0
            self.aw.sendmessage(QApplication.translate("Message","Sound turned OFF", None))

    @pyqtSlot(int)
    def changeDeltaET(self,_=0):
        self.aw.qmc.DeltaETflag = not self.aw.qmc.DeltaETflag
        if self.aw.qmc.crossmarker:
            self.aw.qmc.togglecrosslines() # turn crossmarks off to adjust for new coordinate system
        self.aw.qmc.redraw(recomputeAllDeltas=True)
        
    @pyqtSlot(int)
    def changeDeltaBTspan(self,i):
        if self.aw.qmc.deltaBTspan != self.spanitems[i]:
            self.aw.qmc.deltaBTspan = self.spanitems[i]
            self.aw.qmc.updateDeltaSamples()
            self.aw.qmc.redraw(recomputeAllDeltas=True)
            
    @pyqtSlot(int)
    def changeDeltaETspan(self,i):
        if self.aw.qmc.deltaETspan != self.spanitems[i]:
            self.aw.qmc.deltaETspan = self.spanitems[i]
            self.aw.qmc.updateDeltaSamples()
            self.aw.qmc.redraw(recomputeAllDeltas=True)
        
    def changeDecimalPlaceslcd(self):
        if self.DecimalPlaceslcd.isChecked():
            self.aw.qmc.LCDdecimalplaces = 1
            self.aw.setLCDsDigitCount(5)
        else:
            self.aw.qmc.LCDdecimalplaces = 0
            self.aw.setLCDsDigitCount(3)

    @pyqtSlot(int)
    def changeDeltaBT(self,_=0):
        self.aw.qmc.DeltaBTflag = not self.aw.qmc.DeltaBTflag
        if self.aw.qmc.crossmarker:
            self.aw.qmc.togglecrosslines() # turn crossmarks off to adjust for new coordinate system
        self.aw.qmc.redraw(recomputeAllDeltas=True)

    @pyqtSlot(int)
    def changeDeltaETlcd(self,_=0):
        self.aw.qmc.DeltaETlcdflag = not self.aw.qmc.DeltaETlcdflag

    @pyqtSlot(int)
    def changeDeltaBTlcd(self,_=0):
        self.aw.qmc.DeltaBTlcdflag = not self.aw.qmc.DeltaBTlcdflag
    
    @pyqtSlot()
    def changePathEffects(self):
        try:
            v = self.PathEffects.value()
            if v != self.aw.qmc.patheffects:
                self.PathEffects.blockSignals(True)
                try:
                    self.aw.qmc.patheffects = v
                    self.aw.qmc.redraw(recomputeAllDeltas=False)
                except Exception:
                    pass
                self.PathEffects.blockSignals(False)
        except Exception as e:
            _, _, exc_tb = sys.exc_info()
            self.aw.qmc.adderror((QApplication.translate("Error Message", "Exception:",None) + "changePathEffects(): {0}").format(str(e)),exc_tb.tb_lineno)

    @pyqtSlot(int)
    def changeGraphStyle(self,n):
        self.aw.qmc.graphstyle = n
        self.aw.qmc.redraw(recomputeAllDeltas=False,forceRenewAxis=True)

    @pyqtSlot(int)
    def changeGraphFont(self,n):
        self.aw.qmc.graphfont = n
        self.aw.setFonts()

    @pyqtSlot()
    def changeDeltaBTfilter(self):
        try:
            v = self.DeltaBTfilter.value()*2 + 1
            if v != self.aw.qmc.deltaBTfilter:
                self.DeltaBTfilter.setDisabled(True)
                self.DeltaBTfilter.blockSignals(True)
                try:
                    self.aw.qmc.deltaBTfilter = v
                    self.aw.qmc.redraw(recomputeAllDeltas=True)
                except Exception:
                    pass
                self.DeltaBTfilter.setDisabled(False)
                self.DeltaBTfilter.blockSignals(False)
        except Exception as e:
            _, _, exc_tb = sys.exc_info()
            self.aw.qmc.adderror((QApplication.translate("Error Message", "Exception:",None) + "changeDeltaBTfilter(): {0}").format(str(e)),exc_tb.tb_lineno)

    @pyqtSlot()
    def changeDeltaETfilter(self):
        try:
            v = self.DeltaETfilter.value()*2 + 1
            if v != self.aw.qmc.deltaETfilter:
                self.DeltaETfilter.setDisabled(True)
                self.DeltaETfilter.blockSignals(True)
                try:
                    self.aw.qmc.deltaETfilter = v
                    self.aw.qmc.redraw(recomputeAllDeltas=True)
                except Exception:
                    pass
                self.DeltaETfilter.setDisabled(False)
                self.DeltaETfilter.blockSignals(False)
        except Exception as e:
            _, _, exc_tb = sys.exc_info()
            self.aw.qmc.adderror((QApplication.translate("Error Message", "Exception:",None) + "changeDeltaETfilter(): {0}").format(str(e)),exc_tb.tb_lineno)

    @pyqtSlot(int)
    def changeOptimalSmoothingFlag(self,_=0):
        self.aw.qmc.optimalSmoothing = not self.aw.qmc.optimalSmoothing
        self.aw.qmc.redraw(recomputeAllDeltas=True,smooth=True)
        
    @pyqtSlot(int)
    def changePolyFitFlagFlag(self,_=0):
        self.aw.qmc.polyfitRoRcalc = not self.aw.qmc.polyfitRoRcalc
        self.aw.qmc.optimalSmoothing = self.aw.qmc.optimalSmoothing and self.aw.qmc.polyfitRoRcalc
        self.OptimalSmoothingFlag.blockSignals(True)
        self.OptimalSmoothingFlag.setChecked(self.aw.qmc.optimalSmoothing)
        self.OptimalSmoothingFlag.setEnabled(self.aw.qmc.polyfitRoRcalc)
        self.OptimalSmoothingFlag.blockSignals(False)
        self.aw.qmc.redraw(recomputeAllDeltas=True,smooth=True)
    
    @pyqtSlot(int) 
    def changeDropFilter(self,_=0):
        self.aw.qmc.filterDropOuts = not self.aw.qmc.filterDropOuts
        self.aw.qmc.redraw(recomputeAllDeltas=True,smooth=True)
        
    @pyqtSlot(int) 
    def changeShowFullFilter(self,_=0):
        self.aw.qmc.foregroundShowFullflag = not self.aw.qmc.foregroundShowFullflag
        self.aw.qmc.redraw(recomputeAllDeltas=True,smooth=True)

    @pyqtSlot(int) 
    def changeSpikeFilter(self,_=0):
        self.aw.qmc.dropSpikes = not self.aw.qmc.dropSpikes
    
    @pyqtSlot(int) 
    def changeDuplicatesFilter(self,_=0):
        self.aw.qmc.dropDuplicates = not self.aw.qmc.dropDuplicates

    @pyqtSlot(int) 
    def changeMinMaxLimits(self,_=0):
        self.aw.qmc.minmaxLimits = not self.aw.qmc.minmaxLimits
        
    @pyqtSlot(int) 
    def changeSwapETBT(self,_=0):
        self.aw.qmc.swapETBT = not self.aw.qmc.swapETBT
    
    @pyqtSlot()
    def changeFilter(self):
        try:
            v = self.Filter.value()*2 + 1
            if v != self.aw.qmc.curvefilter:
                self.Filter.setDisabled(True)
                self.aw.qmc.curvefilter = v
                self.aw.qmc.redraw(recomputeAllDeltas=True,smooth=True)
                self.Filter.setDisabled(False)
                self.Filter.setFocus()
        except Exception as e:
            _, _, exc_tb = sys.exc_info()
            self.aw.qmc.adderror((QApplication.translate("Error Message", "Exception:",None) + " changeFilter(): {0}").format(str(e)),exc_tb.tb_lineno)

    @pyqtSlot(int)
    def changeProjection(self,_=0):
        self.aw.qmc.projectFlag = not self.aw.qmc.projectFlag
        if not self.aw.qmc.projectFlag:
            #erase old projections
            self.aw.qmc.resetlines()

    @pyqtSlot(int)
    def changeProjectionMode(self,i):
        self.aw.qmc.projectionmode = i

    @pyqtSlot(int)
    def changeInterpolationMode(self,_=0):
        self.aw.qmc.resetlines()
        self.aw.qmc.redraw(recomputeAllDeltas=False)
        self.interpolation()

    @pyqtSlot(bool)
    def showSymbolicHelp(self,_=False):
        self.helpdialog = self.aw.showHelpDialog(
                self,            # this dialog as parent
                self.helpdialog, # the existing help dialog
                QApplication.translate("Form Caption","Symbolic Formulas Help",None),
                symbolic_help.content())

    def closeHelp(self):
        self.aw.closeHelpDialog(self.helpdialog)

    def closeEvent(self,_):
        self.close()
        
    #cancel button
    @pyqtSlot()
    def close(self):
        self.closeHelp()
        #save window position (only; not size!)
        settings = QSettings()
        settings.setValue("CurvesPosition",self.frameGeometry().topLeft())
        
        self.aw.HUDDlg_activeTab = self.TabWidget.currentIndex()

        #restore settings
        self.aw.qmc.DeltaETflag = self.org_DeltaET
        self.aw.qmc.DeltaBTflag = self.org_DeltaBT
        self.aw.qmc.DeltaETlcdflag = self.org_DeltaETlcd
        self.aw.qmc.DeltaBTlcdflag = self.org_DeltaBTlcd
        self.aw.qmc.projectFlag = self.org_Projection
        self.aw.qmc.patheffects = self.org_patheffects
        self.aw.qmc.graphstyle = self.org_graphstyle
        self.aw.qmc.graphfont = self.org_graphfont
        self.aw.qmc.HUDbuttonflag = self.org_HUDbuttonflag
        self.aw.qmc.filterDropOuts = self.org_filterDropOuts
        self.aw.qmc.dropSpikes = self.org_dropSpikes
        self.aw.qmc.dropDuplicates = self.org_dropDuplicates
        self.aw.qmc.dropDuplicatesLimit = self.org_dropDuplicatesLimit
        self.aw.qmc.swapETBT = self.org_swapETBT
        self.aw.qmc.optimalSmoothing = self.org_optimalSmoothing
        self.aw.qmc.polyfitRoRcalc = self.org_polyfitRoRcalc
        self.aw.soundflag = self.org_soundflag
        self.aw.logoimgflag = self.org_logoimgflag
        self.aw.logoimgalpha = self.org_logoimgalpha
        self.aw.qmc.curvefilter = self.org_curvefilter
        self.aw.qmc.deltaETfilter = self.org_deltaETfilter
        self.aw.qmc.deltaBTfilter = self.org_deltaBTfilter
        self.aw.qmc.deltaBTspan = self.org_deltaBTspan
        self.aw.qmc.deltaETspan = self.org_deltaETspan
        self.aw.qmc.graphstyle = self.org_graphstyle
        self.aw.ETname = self.org_ETname
        self.aw.BTname = self.org_BTname
        self.aw.qmc.foregroundShowFullflag = self.org_foregroundShowFullflag
        
        self.aw.setFonts(False)
        self.aw.qmc.resetlinecountcaches()
        self.aw.qmc.resetdeltalines()
        self.aw.qmc.resetlines()
        self.aw.qmc.updateDeltaSamples()
        self.aw.qmc.redraw(recomputeAllDeltas=True)
        self.aw.clearMessageLine() #clears plotter possible exceptions if Cancel
        
        self.reject()

    #button OK
    @pyqtSlot()
    def updatetargets(self):
        self.closeHelp()
        #save window position (only; not size!)
        settings = QSettings()
        settings.setValue("CurvesPosition",self.frameGeometry().topLeft())
        self.aw.HUDDlg_activeTab = self.TabWidget.currentIndex()

        self.aw.qmc.DeltaETfunction = str(self.DeltaETfunctionedit.text())
        self.aw.qmc.DeltaBTfunction = str(self.DeltaBTfunctionedit.text())
        self.aw.LCD4frame.setVisible((self.aw.qmc.DeltaBTlcdflag if self.aw.qmc.swapdeltalcds else self.aw.qmc.DeltaETlcdflag))
        self.aw.LCD5frame.setVisible((self.aw.qmc.DeltaETlcdflag if self.aw.qmc.swapdeltalcds else self.aw.qmc.DeltaBTlcdflag))
        if self.aw.largeDeltaLCDs_dialog is not None:
            self.aw.largeDeltaLCDs_dialog.updateVisiblitiesDeltaETBT()
        self.changeDecimalPlaceslcd()
        swap = self.swapdeltalcds.isChecked()
        # swap DeltaBT/ET lcds on leaving this dialog
        if self.aw.qmc.swapdeltalcds != swap:
            tmp = QWidget()
            tmp.setLayout(self.aw.LCD4frame.layout())
            self.aw.LCD4frame.setLayout(self.aw.LCD5frame.layout())
            self.aw.LCD5frame.setLayout(tmp.layout())
            self.aw.qmc.swapdeltalcds = swap
        # reflect swap or rename of ET/BT in large LCDs:
        if self.aw.largeLCDs_dialog is not None:
            self.aw.largeLCDs_dialog.reLayout()
        if self.aw.largeDeltaLCDs_dialog is not None:
            self.aw.largeDeltaLCDs_dialog.reLayout()
            
        self.aw.qmc.RoRlimitFlag = self.rorFilter.isChecked()
        self.aw.qmc.RoRlimitm = int(self.rorminLimit.value())
        self.aw.qmc.RoRlimit = int(self.rormaxLimit.value())
        self.aw.qmc.filterDropOuts = self.FilterSpikes.isChecked()
        self.aw.qmc.dropSpikes = self.DropSpikes.isChecked()
        self.aw.qmc.dropDuplicates = self.DropDuplicates.isChecked()
        self.aw.qmc.dropDuplicatesLimit = self.DropDuplicatesLimit.value()
        self.aw.qmc.minmaxLimits = self.MinMaxLimits.isChecked()
        self.aw.qmc.filterDropOut_tmin = int(self.minLimit.value())
        self.aw.qmc.filterDropOut_tmax = int(self.maxLimit.value())
        self.aw.qmc.foregroundShowFullflag = self.ShowFull.isChecked()
        mode = self.modeComboBox.currentText()
        if mode == QApplication.translate("ComboBox","metrics", None):
            self.aw.HUDfunction = 0
        elif mode == QApplication.translate("ComboBox","thermal", None):
            self.aw.HUDfunction = 1
        self.aw.qmc.ETtarget = int(str(self.ETlineEdit.text()))
        self.aw.qmc.BTtarget = int(str(self.BTlineEdit.text()))
        self.aw.qmc.ET2target = int(str(self.ET2lineEdit.text()))
        self.aw.qmc.BT2target = int(str(self.BT2lineEdit.text()))
        if self.aw.qmc.ETtarget > self.aw.qmc.ET2target: # swap such that ETtarget < ET2target
            self.aw.qmc.ETtarget = int(str(self.ET2lineEdit.text()))
            self.aw.qmc.ET2target = int(str(self.ETlineEdit.text()))
        if self.aw.qmc.BTtarget > self.aw.qmc.BT2target: # swap such that BTtarget < BT2target
            self.aw.qmc.BTtarget = int(str(self.BT2lineEdit.text()))
            self.aw.qmc.BT2target = int(str(self.BTlineEdit.text()))
        self.aw.qmc.hudETpid[0] = int(str(self.ETpidP.text()))
        self.aw.qmc.hudETpid[1] = int(str(self.ETpidI.text()))
        self.aw.qmc.hudETpid[2] = int(str(self.ETpidD.text()))
        self.aw.qmc.plotcurves[0] = str(self.equedit1.text())
        self.aw.qmc.plotcurves[1] = str(self.equedit2.text())
        self.aw.qmc.plotcurves[2] = str(self.equedit3.text())
        self.aw.qmc.plotcurves[3] = str(self.equedit4.text())
        self.aw.qmc.plotcurves[4] = str(self.equedit5.text())
        self.aw.qmc.plotcurves[5] = str(self.equedit6.text())
        self.aw.qmc.plotcurves[6] = str(self.equedit7.text())
        self.aw.qmc.plotcurves[7] = str(self.equedit8.text())
        self.aw.qmc.plotcurves[8] = str(self.equedit9.text())
        string = QApplication.translate("Message","[ET target 1 = {0}] [BT target 1 = {1}] [ET target 2 = {2}] [BT target 2 = {3}]", None).format(str(self.aw.qmc.ETtarget),str(self.aw.qmc.BTtarget),str(self.aw.qmc.ET2target),str(self.aw.qmc.BT2target))
        self.aw.sendmessage(string)
        self.aw.qmc.resetlinecountcaches()
        self.aw.qmc.resetdeltalines()
        self.aw.qmc.resetlines()
        self.aw.qmc.redraw(recomputeAllDeltas=True)
        self.aw.closeEventSettings()
        self.accept()