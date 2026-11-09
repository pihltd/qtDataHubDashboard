from PyQt6.QtWidgets import QApplication,  QMainWindow, QTabWidget, QVBoxLayout, QComboBox, QHBoxLayout, QWidget, QTableView, QLabel, QHeaderView, QPushButton, QGridLayout, QCheckBox, QButtonGroup, QFileDialog
from PyQt6.QtCore import QSize, Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import pyqtgraph as pg

import pandas as pd
import numpy as np

from src.qtDHFunctions import dhAPICreds, modelFilesByTag, loadSheetOMizer
from src.qtSubclasses import CustomDialog, SubmissionTableModel, NullTableModel
from src.qtData import SubmissionData

# https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html
import sys
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.kernel32.SetDllDirectoryW(None)
    
class MainWindow(QMainWindow):
    
    #TODO Spinners

    
    def __init__(self):
        super().__init__()
        
        self.submission_df = pd.DataFrame()
        self.theDataThing = SubmissionData()
        
        self.creds = None
        
        self.sub_blue = '#3498DB' 
        self.sub_red =  '#E74C3C'
        self.sub_yellow = '#F4D03F'
        self.sub_green =  '#16A085'
        self.tab_color = '#05ABED'
        self.grey = '#e0e0eb'
        
        
        self.setWindowTitle("CRDC Dashboard")
        
        #
        #  Layouts
        #
        summarylayout = QGridLayout()
        dropdownlayout = QHBoxLayout()
        self.barlayout = QGridLayout()
        self.pielayout = QGridLayout()
        errorlayout = QVBoxLayout()
        warninglayout = QVBoxLayout()
        errorwarninglayout = QHBoxLayout()
        self.loadsheetlayout = QGridLayout()
        self.checkboxlayout = QVBoxLayout()
        self.checkboxgroup = QButtonGroup()
        self.checkboxgroup.setExclusive(False)
        #
        # Combo boxes
        #
        self.tiercombowidget = QComboBox()
        self.tiercombowidget.addItems([ "Prod", "Stage", "QA", "QA2", "Dev", "Dev2"])
        self.tiercombowidget.setPlaceholderText("Select a tier")
        self.tiercombowidget.setCurrentIndex(-1)
        self.tiercombowidget.currentTextChanged.connect(self.tier_changed)
        
        self.studycombowidget = QComboBox()
        self.studycombowidget.setPlaceholderText("Select a Study to see submissions")
        self.studycombowidget.setCurrentIndex(-1)
        self.studycombowidget.currentTextChanged.connect(self.study_changed)
        
        self.submissioncombowidget = QComboBox()
        self.submissioncombowidget.setPlaceholderText("Select a Submission to see details")
        self.submissioncombowidget.setCurrentIndex(-1)
        self.submissioncombowidget.currentTextChanged.connect(self.submission_reset)
        self.submissioncombowidget.currentTextChanged.connect(self.submission_raw_changed)
        self.submissioncombowidget.currentTextChanged.connect(self.submission_percentage_changed)
        self.submissioncombowidget.currentTextChanged.connect(self.error_warning_tables)
        self.submissioncombowidget.currentTextChanged.connect(self.full_error_tab)
        self.submissioncombowidget.currentTextChanged.connect(self.full_warning_tab)
        self.submissioncombowidget.currentTextChanged.connect(self.full_data_tab)
        
        #
        # Submission Table
        #
        self.submissiontablelabel = QLabel("Submissions")
        self.submissiontable = QTableView()
        self.submissiontable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.submissiontable.setAlternatingRowColors(True)
        #
        # Node Count bar charts
        #
        self.node_raw_widget = pg.PlotWidget()
        self.node_raw_widget.setBackground(background=None)
        self.node_percentage_widget = pg.PlotWidget()
        self.node_percentage_widget.setBackground(background=None)
        
        self.barlayout.addWidget(self.node_raw_widget, 0,0)
        self.barlayout.addWidget(self.node_percentage_widget, 0,1)
        barwidget = QWidget()
        barwidget.setLayout(self.barlayout)
        
        #
        #  Error and warning tables
        #
        self.errorsummarylabel = QLabel("Error Summary")
        self.errorsummarytable = QTableView()
        self.errorsummarytable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.errorsummarytable.setAlternatingRowColors(True)
        self.warningsummarylabel = QLabel("Warning Summary")
        self.warningsummarytable = QTableView()
        self.warningsummarytable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.warningsummarytable.setAlternatingRowColors(True)
        errorlayout.addWidget(self.errorsummarylabel)
        errorlayout.addWidget(self.errorsummarytable)
        errorwidget = QWidget()
        errorwidget.setLayout(errorlayout)
   
        warninglayout.addWidget(self.warningsummarylabel)
        warninglayout.addWidget(self.warningsummarytable)
        warningwidget = QWidget()
        warningwidget.setLayout(warninglayout)
        
        errorwarninglayout.addWidget(errorwidget)
        errorwarninglayout.addWidget(warningwidget)
        errorwarningwidget = QWidget()
        errorwarningwidget.setLayout(errorwarninglayout)
        
        #
        # Full Error, warning, and submitted data tables
        #
        
        self.fullerrorlabel = QLabel("Error Details")
        self.fullerrortable = QTableView()
        self.fullerrortable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.fullerrortable.setAlternatingRowColors(True)
        self.errordropdown = QComboBox()
        self.errordropdown.setPlaceholderText("Select an error for full details")
        self.errordropdown.setCurrentIndex(-1)
        self.errordropdown.currentTextChanged.connect(self.full_error_table)
        self.errorheaderlayout = QHBoxLayout()
        self.errorheaderlayout.addWidget(self.fullerrorlabel)
        self.errorheaderlayout.addWidget(self.errordropdown)
        self.errorheaderwidget = QWidget()
        self.errorheaderwidget.setLayout(self.errorheaderlayout)
        self.fullerrorlayout = QVBoxLayout()
        self.fullerrorlayout.addWidget(self.errorheaderwidget)
        self.fullerrorlayout.addWidget(self.fullerrortable)
        self.fullerrorwidget = QWidget()
        self.fullerrorwidget.setLayout(self.fullerrorlayout)
        
        
        self.fullwarninglabel = QLabel("Warning Details")
        self.fullwarningtable = QTableView()
        self.fullwarningtable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.fullwarningtable.setAlternatingRowColors(True)
        self.warningdropdown = QComboBox()
        self.warningdropdown.setPlaceholderText("Select a warning for full details")
        self.warningdropdown.setCurrentIndex(-1)
        self.warningdropdown.currentTextChanged.connect(self.full_warning_table)
        self.warningheaderlayout = QHBoxLayout()
        self.warningheaderlayout.addWidget(self.fullwarninglabel)
        self.warningheaderlayout.addWidget(self.warningdropdown)
        self.warningheaderwidget = QWidget()
        self.warningheaderwidget.setLayout(self.warningheaderlayout)
        self.fullwarninglayout = QVBoxLayout()
        self.fullwarninglayout.addWidget(self.warningheaderwidget)
        self.fullwarninglayout.addWidget(self.fullwarningtable)
        self.fullwarningwidget = QWidget()
        self.fullwarningwidget.setLayout(self.fullwarninglayout)
        
        self.fulldatalabel = QLabel("Submitted Data Details")
        self.fulldatatable = QTableView()
        self.fulldatatable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.fulldatatable.setAlternatingRowColors(True)
        self.datadropdown = QComboBox()
        self.datadropdown.setPlaceholderText("Select a node to see data")
        self.datadropdown.setCurrentIndex(-1)
        self.datadropdown.currentTextChanged.connect(self.full_data_table)
        self.dataheaderlayout = QHBoxLayout()
        self.dataheaderlayout.addWidget(self.fulldatalabel)
        self.dataheaderlayout.addWidget(self.datadropdown)
        self.dataheaderwidget = QWidget()
        self.dataheaderwidget.setLayout(self.dataheaderlayout)
        self.fulldatalayout = QVBoxLayout()
        self.fulldatalayout.addWidget(self.dataheaderwidget)
        self.fulldatalayout.addWidget(self.fulldatatable)
        self.fulldatawidget = QWidget()
        self.fulldatawidget.setLayout(self.fulldatalayout)

        
        
        # Dropdown layouts
        dropdownlayout.addWidget(self.tiercombowidget)
        dropdownlayout.addWidget(self.studycombowidget)
        dropdownlayout.addWidget(self.submissioncombowidget)
        dropdownwidget = QWidget()
        dropdownwidget.setLayout(dropdownlayout)
        
        #
        # Pie Charts
        #
        self.errorpielayout = QHBoxLayout()
        self.warningpielayout = QHBoxLayout()
        self.errorpiewidget = QWidget()
        self.warningpiewidget = QWidget()
        self.errorpiewidget.setLayout(self.errorpielayout)
        self.warningpiewidget.setLayout(self.warningpielayout)
        self.errorpiefig = Figure()
        self.warningpiefig = Figure()
        self.rawbar = Figure()
        self.errorpielabel = QLabel("Submission Errors Pie Chart")
        self.warningpielabel = QLabel("Submission Warnings Pie Chart")
        self.pielayout.addWidget(self.errorpielabel, 0,0)
        self.pielayout.addWidget(self.errorpiewidget, 1,0)
        self.pielayout.addWidget(self.warningpielabel, 0,1)
        self.pielayout.addWidget(self.warningpiewidget, 1,1)
        
        piewidget = QWidget()
        piewidget.setLayout(self.pielayout)
        
        #Overall Summary Tab layouy
        summarylayout.addWidget(dropdownwidget, 0,0)
        summarylayout.addWidget(self.submissiontablelabel, 1,0)
        summarylayout.addWidget(self.submissiontable, 2,0)
        summarylayout.addWidget(barwidget, 3,0)
        summarylayout.addWidget(piewidget, 4,0)
        summarylayout.addWidget(errorwarningwidget, 5,0)
        summarywidget = QWidget()
        summarywidget.setLayout(summarylayout)
        
        #
        # Load Sheet Tab
        #
        self.loadsheetheader = QLabel("Available Load Sheets for Submisison")
        self.loadsheetlayout.addWidget(self.loadsheetheader, 0,0)
        self.loadsheetbutton = QPushButton("List available load sheets")
        self.loadsheetbutton.setStyleSheet(f"background-color:{self.grey}")
        self.loadsheetbutton.pressed.connect(self.getModelInfo)
        self.loadsheetlayout.addWidget(self.loadsheetbutton, 0, 1)
        self.getsheetheader = QLabel("Select load sheets to create")
        self.getsheetbutton = QPushButton("Download selected Load sheets")
        self.getsheetbutton.setStyleSheet(f"background-color:{self.grey}")
        self.getsheetbutton.pressed.connect(self.getSelectedNodes)
        self.loadsheetlayout.addWidget(self.getsheetheader, 2,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.loadsheetlayout.addWidget(self.getsheetbutton, 2,1, alignment=Qt.AlignmentFlag.AlignTop)
        self.loadsheetwidget = QWidget()
        self.loadsheetwidget.setLayout(self.loadsheetlayout)
        self.checkboxes = QWidget()
        
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        tabs.setTabShape(QTabWidget.TabShape.Triangular)
        tabs.addTab(summarywidget, "Summary")
        tabs.addTab(self.fullerrorwidget, "Errors")
        tabs.addTab(self.fullwarningwidget, "Warnings")
        tabs.addTab(self.fulldatawidget, "Data")
        tabs.addTab(self.loadsheetwidget, "Load Sheets")
        
        
        
            
        self.setCentralWidget(tabs)
        
        
    def tier_changed(self, t):
        #Reset everything
        self.theDataThing.fullReset()
        # Now go get stuff
        self.creds = dhAPICreds(t.lower())
        if self.creds['token'] is None and self.creds['url'] is not None:
            bummer = CustomDialog("Login Error", f"No API key for {t}")
            bummer.exec()
            self.tiercombowidget.setCurrentIndex(-1)
        elif self.creds['token'] is None and self.creds['url'] is None:
            bummer2 = CustomDialog("Login Error", f"No API key or URL for {t}")
            bummer2.exec
            self.tiercombowidget.setCurrentIndex(-1)
        else:
            #vars = {"status":["New", "In Progress", "Submitted", "Rejected", "Withdrawn", "Released"]}
            self.theDataThing.getStudyInfo(url=self.creds['url'], apitoken=self.creds['token'])
            self.studycombowidget.clear()
            self.studycombowidget.addItems(self.theDataThing.getStudyList())
            self.studycombowidget.setCurrentIndex(-1)


       
    def study_changed(self, abbrev):
        # Study level reset
        self.theDataThing.studyReset()
        self.submissioncombowidget.clear()
        self.model = NullTableModel()
        self.submissiontable.setModel(self.model)
        self.fullTableReset()
        self.fullPieReset()
        self.fullLoadSheetReset()
        # Get new data
        vars = {"status": "All"}
        self.theDataThing.getSubmissionInfo(url=self.creds['url'], apitoken=self.creds['token'], variables=vars, abbrev=abbrev)
        df = self.theDataThing.getSubmissionDataFrame()
        self.model = SubmissionTableModel(df)
        self.submissiontable.setModel(self.model)
        
        self.submissiontablelabel.clear()
        self.submissiontablelabel.setText(f"Submission for {abbrev}")
        self.submissioncombowidget.clear()
        self.submissioncombowidget.addItems(self.theDataThing.getSubmissionList())
        self.submissioncombowidget.setCurrentIndex(-1)


    def submission_reset(self, name):
        self.theDataThing.submissionReset()
        self.fullTableReset()
        self.fullPieReset()
        self.fullLoadSheetReset()
    
    
    def submission_raw_changed(self, name):
        self.node_raw_widget.clear()
        self.node_raw_widget.setTitle(f"Raw node counts for {name}")
        self.node_raw_widget.setLabel("left", "Count")
        self.node_raw_widget.setLabel("bottom", "Node")
        
        
        
        graphdata_df = self.theDataThing.barChartCountData2(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name)
        
        if graphdata_df is not None:
            # This builds the array used to change the lables
            nodecount = 1
            categorydata = {}
            for node in graphdata_df['nodeName'].tolist():
                categorydata[nodecount] = node
                nodecount = nodecount + 1
            
            nodes = np.array(list(categorydata.keys()), dtype=float)
            newstate = np.array(graphdata_df['new'].tolist())
            errorstate = np.array(graphdata_df['error'].tolist())
            warnstate = np.array(graphdata_df['warning'].tolist())
            passstate = np.array(graphdata_df['passed'].tolist())
            
            width = .5
            newbar = pg.BarGraphItem(x=nodes, height=newstate, width=width, brush=self.sub_blue, name="New")
            errorbar = pg.BarGraphItem(x=nodes, height=errorstate, width= width, brush=self.sub_red, name="Error")
            warnbar = pg.BarGraphItem(x=nodes, height=warnstate, width= width, brush=self.sub_yellow, name="Warning")
            passbar = pg.BarGraphItem(x=nodes, height=passstate, width= width, brush=self.sub_green, name="Passed")
            
            self.node_raw_widget.addItem(newbar)
            self.node_raw_widget.addItem(errorbar)
            self.node_raw_widget.addItem(warnbar)
            self.node_raw_widget.addItem(passbar)
            
            ax = self.node_raw_widget.getAxis("bottom")
            ax.setTicks([list(categorydata.items())])
        
    
    def submission_percentage_changed(self, name):
        self.node_percentage_widget.clear()
        self.node_percentage_widget.setTitle(f"Percentage counts for {name}")
        self.node_percentage_widget.setLabel("left", "Count")
        self.node_percentage_widget.setLabel("bottom", "Node")
        
        graphdata_df = self.theDataThing.barChartCountData2(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name, percentage=True)
        
        if graphdata_df is not None:  
            if not graphdata_df.empty:      
            #if graphdata_df is not None:
                nodecount = 1
                categorydata = {}
                for node in graphdata_df['nodeName'].tolist():
                    categorydata[nodecount] = node
                    nodecount = nodecount + 1
                
                nodes = np.array(list(categorydata.keys()), dtype=float)
                newstate = np.array(graphdata_df['new'].tolist())
                errorstate = np.array(graphdata_df['error'].tolist())
                warnstate = np.array(graphdata_df['warning'].tolist())
                passstate = np.array(graphdata_df['passed'].tolist())
                
                width = .5
                newbar = pg.BarGraphItem(x=nodes, height=newstate, width=width, brush=self.sub_blue, name="New")
                errorbar = pg.BarGraphItem(x=nodes, height=errorstate, width= width, brush=self.sub_red, name="Error")
                warnbar = pg.BarGraphItem(x=nodes, height=warnstate, width= width, brush=self.sub_yellow, name="Warning")
                passbar = pg.BarGraphItem(x=nodes, height=passstate, width= width, brush=self.sub_green, name="Passed")
                
                self.node_percentage_widget.addItem(newbar)
                self.node_percentage_widget.addItem(errorbar)
                self.node_percentage_widget.addItem(warnbar)
                self.node_percentage_widget.addItem(passbar)
                
                ax = self.node_percentage_widget.getAxis("bottom")
                ax.setTicks([list(categorydata.items())])


    def error_warning_tables(self, name):
        #Delete all the old stuff
        self.errormodel = SubmissionTableModel(pd.DataFrame())
        self.warningmodel = SubmissionTableModel(pd.DataFrame())
        self.errorsummarytable.setModel(self.errormodel)
        self.warningsummarytable.setModel(self.warningmodel)
        #Add new data
        error_df = self.theDataThing.validationErrorData(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name)
        warning_df = self.theDataThing.validationWarningData(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name)
        if error_df is not None:
            #Populate the tables
            self.errormodel = SubmissionTableModel(error_df)
            self.errorsummarytable.setModel(self.errormodel)
            # Populate the pie charts
            errorlabels = error_df['Error'].tolist()
            errorcounts = error_df['Count'].tolist()
            errorpie = self.errorpiefig.add_subplot()
            errorpie.pie(errorcounts, labels=errorlabels, labeldistance=2, autopct='%1.1f%%')
            errorpieplate = FigureCanvasQTAgg(self.errorpiefig)
            self.errorpielayout.addWidget(errorpieplate)
            
        if warning_df is not None:
            #populate the tables
            self.warningmodel = SubmissionTableModel(warning_df)
            self.warningsummarytable.setModel(self.warningmodel)
            #Populate the pie chart
            warninglables = warning_df['Warning'].tolist()
            warningcounts = warning_df['Count'].tolist()
            warningpie = self.warningpiefig.add_subplot()
            warningpie.pie(warningcounts, labels=warninglables, labeldistance=2, autopct='%1.1f%%')
            warningpieplate = FigureCanvasQTAgg(self.warningpiefig)
            self.warningpielayout.addWidget(warningpieplate)
    
    def full_error_tab(self, name):
        #self.theDataThing.fullValidationErrorData(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name)
        #self.errordropdown.addItems(self.theDataThing.errorDropDownValues())
        error_df = self.theDataThing.validationErrorData(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name)
        if error_df is not None:
            self.errordropdown.addItems(error_df['Error'].tolist())
        
    def full_warning_tab(self,name):
        #self.theDataThing.fullValidationWarningData(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name)
        #self.warningdropdown.addItems(self.theDataThing.warningDropDownValues())
        warning_df = self.theDataThing.validationWarningData(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name)
        if warning_df is not None:
            self.warningdropdown.addItems(warning_df['Warning'].tolist())
        
    def full_error_table(self, name):
        fullerror_df = self.theDataThing.fullValidationErrorTableData(name)
        self.fullerrormodel = SubmissionTableModel(fullerror_df)
        self.fullerrortable.setModel(self.fullerrormodel)
    
    def full_warning_table(self, name):
        fullwarning_df = self.theDataThing.fullValidationWarningTableData(name)
        self.fullwarningmodel = SubmissionTableModel(fullwarning_df)
        self.fullwarningtable.setModel(self.fullwarningmodel)
        
    def full_data_tab(self, name):
        self.datadropdown.addItems(self.theDataThing.dataNodeDropDown(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name))
    
    
    def full_data_table(self, name):
        data_df = self.theDataThing.fullDataNodeTableData(url=self.creds['url'], apitoken=self.creds['token'], submissionname=self.submissioncombowidget.currentText(), nodename=name)
        if data_df is not None:
            self.fulldatamodel = SubmissionTableModel(data_df)
            self.fulldatatable.setModel(self.fulldatamodel)
            
    
    def fullTableReset(self):
        #Reset Data Table
        self.fulldatamodel = NullTableModel()
        self.fulldatatable.setModel(self.fulldatamodel)
        for i in reversed(range(self.datadropdown.count())):
            self.datadropdown.removeItem(i)
            
        #Reset Warning table
        self.warningmodel = NullTableModel()
        self.fullwarningtable.setModel(self.warningmodel)
        for i in reversed(range(self.warningdropdown.count())):
                self.warningdropdown.removeItem(i)
        
        #Reset Error table
        self.fullerrormodel = NullTableModel()
        self.fullerrortable.setModel(self.fullerrormodel)
        for i in reversed(range(self.errordropdown.count())):
            self.errordropdown.removeItem(i)
            
            
    def fullPieReset(self):
        for i in reversed(range(self.errorpielayout.count())):
            self.errorpielayout.itemAt(i).widget().deleteLater()
        for i in reversed(range(self.warningpielayout.count())):
            self.warningpielayout.itemAt(i).widget().deleteLater()
            
    def fullLoadSheetReset(self):
        for button in self.checkboxgroup.buttons():
            button.deleteLater()

    def getModelInfo(self):
        modelinfo = self.theDataThing.getModelNameVersion(self.submissioncombowidget.currentText())
        nodelist = self.theDataThing.dataNodeDropDown(url=self.creds['url'], apitoken=self.creds['token'], submissionname=self.submissioncombowidget.currentText())
        self.loadsheetheader.setText(f"Sheets available for {self.submissioncombowidget.currentText()} Model: {modelinfo['handle']} Version: {modelinfo['version']}")
        for node in nodelist:
            checkboxthing = QCheckBox(node)
            self.checkboxlayout.addWidget(checkboxthing)
            self.checkboxgroup.addButton(checkboxthing)
        self.checkboxes.setLayout(self.checkboxlayout)
        self.loadsheetlayout.addWidget(self.checkboxes, 1,0)
        
    
    def getSelectedNodes(self):
        modelinfo = self.theDataThing.getModelNameVersion(self.submissioncombowidget.currentText())
        checked = []
        for checkbox in self.checkboxgroup.buttons():
            if checkbox.isChecked():
                checked.append(checkbox.text())
       
        saveFileDialog = QFileDialog(self)
        saveFileDialog.setWindowTitle("Select a directory for the manifests")
        saveFileDialog.setFileMode(QFileDialog.FileMode.Directory)
        saveFileDialog.setViewMode(QFileDialog.ViewMode.List)
        
        if saveFileDialog.exec():
            savedir = saveFileDialog.selectedFiles()[0]            
        #For each node
        mdf = modelFilesByTag(modelName=modelinfo['handle'], modelVersion=modelinfo['version'], mdfonly=True)
        for node in checked:
            data_df = self.theDataThing.fullDataNodeTableData(url=self.creds['url'], apitoken=self.creds['token'],submissionname=self.submissioncombowidget.currentText(), nodename=node)
            data_df = loadSheetOMizer(df=data_df, nodename=node, mdf=mdf)
            
            filename = f"{savedir}\\{mdf.handle}_{mdf.version}_{node}_loadsheet.tsv"
            data_df.to_csv(filename, sep="\t", index=False)
            
       

app = QApplication([])
window = MainWindow()
window.resize(QSize(1500,700))
window.show()
app.exec()
