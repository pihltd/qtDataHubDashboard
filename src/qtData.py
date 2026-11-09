# https://medium.com/@jasonyang.algo/getting-started-with-pyqt6-a-beginner-friendly-guide-to-modern-gui-development-79924151440f

import pandas as pd
import src.DH_Queries as dhq
import src.qtDHFunctions as dhf
from PyQt6.QtCore import QObject, pyqtSignal
import json


class DataSignals(QObject):
    sub_updated = pyqtSignal()  # Submission datafram is updated

class SubmissionData(QObject):
    
    
    def __init__(self):
        self.study_df = pd.DataFrame()
        self.submission_df = pd.DataFrame()
        self.errordetail_df = pd.DataFrame()
        self.errorlist = []
        self.warningdetail_df = pd.DataFrame()
        self.warninglist = []
        self.datadetail_df = pd.DataFrame()
        self.datalist = []

        
    
    def getStudyInfo(self, url, apitoken, variables=None):
        studyinfojson = dhf.dhApiQuery(url=url, apitoken=apitoken, query=dhq.org_query2, variables=variables)
        if studyinfojson is not None:
            loading = []
            for entry in studyinfojson['data']['listSubmissions']['submissions']:
                loading.append({"_id": entry['study']['_id'], 'studyAbbreviation': entry['study']['studyAbbreviation']})
            self.study_df = pd.DataFrame(loading)

       
    def getStudyList(self):
        return self.study_df['studyAbbreviation'].unique().tolist()
    
    
    def getSubmissionInfo(self, url, apitoken, abbrev, variables=None):
        
        submissioninfojson = dhf.dhApiQuery(url=url, apitoken=apitoken, query=dhq.list_sub_query, variables=variables)
        fullsubmission_df = pd.DataFrame(submissioninfojson['data']['listSubmissions']['submissions'])
        fullsubmission_df = fullsubmission_df.query("studyAbbreviation == @abbrev")
        self.submission_df = dhf.elapsedTime(fullsubmission_df)
        
        
        
    def getSubmissionDataFrame(self):
        return self.submission_df
    
    def getSubmissionList(self):
        return self.submission_df['name'].unique().tolist()
    
    
    def getModelNameVersion(self, submissionname):
        if len(submissionname) > 0:
            handlelist = self.submission_df.query('name == @submissionname')['dataCommons'].tolist()
            versionlist = self.submission_df.query('name == @submissionname')['modelVersion'].tolist()
            return {'handle': handlelist[0], 'version': versionlist[0]}
            
        
    
    #def getErrorPieChartInfo(self, url, apitoken, submissionname, variables=None):
    #    #Not sure if this is used anywhere
    #    if len(submissionname) > 0:
    #        sub_df = self.submission_df.query('name == @submissionname')
    #        subid = sub_df.at[0, "_id"]
    #        
    #        vars = {"submissionID":subid, "severity":"Error", "first":-1, "offset":0, "sortDirection": "desc", "orderBy": "displayID"}
    #        errorjson = dhf.dhApiQuery(url=url, apitoken=apitoken, query=dhq.list_sub_query, variables=vars)
        
        
    def barChartCountData2(self,url, apitoken, submissionname, variables=None, percentage=False):
        categories = ['new', 'error', 'warning', 'passed']
        columns = ['nodeName', 'total', 'new', 'error', 'warning', 'passed']
        
        if len(submissionname) > 0:
            idlist = self.submission_df.query("name == @submissionname")["_id"].tolist()
            if len(idlist) >= 1 :
                variables = {'id': idlist[0]}
                countjson = dhf.dhApiQuery(url=url, apitoken=apitoken, query= dhq.submission_stats_query, variables=variables)
                substats_df = pd.DataFrame(columns=columns)
                for entry in countjson['data']['submissionStats']['stats']:
                    substats_df.loc[len(substats_df)] = entry
                    
                if percentage:
                    newlist = []
                    for index, row in substats_df.iterrows():
                        newrow = {}
                        newrow['nodeName'] = row['nodeName']
                        for category in categories:
                            if row[category] > 0:
                                newrow[category] = int((row[category]/row['total'])*100)
                            else:
                                newrow[category] = 0
                        newlist.append(newrow)
                    percentage_df = pd.DataFrame(newlist)
                    return percentage_df
                else:
                    return substats_df
            else:
                return None
        else:
            return None
        
    
    def validationErrorData(self, url, apitoken, submissionname, variables=None):
        if len(submissionname) > 0:
            idlist = self.submission_df.query("name == @submissionname")["_id"].tolist()
            if len(idlist)>=1:
                variables = {"submissionID":idlist[0], "severity":"Error", "first":-1, "offset":0, "sortDirection": "desc", "orderBy": "displayID"}
                val_res = dhf.dhApiQuery(url=url, apitoken=apitoken, query=dhq.summaryQuery, variables=variables)
                errorsummarylist = []
                if val_res['data']['aggregatedSubmissionQCResults']['total'] == 0:
                    return  None
                else:
                    val_df = pd.DataFrame(val_res['data']['aggregatedSubmissionQCResults']['results'])
                    self.errorlist = val_df['title'].unique().tolist()
                    errorlist = val_df['title'].unique().tolist()
                    for error in errorlist:
                        error_df = val_df.query('title == @error')
                        errorsummarylist.append({'Error': error, 'Count': error_df['count'].sum()})
                    errorcount_df = pd.DataFrame(errorsummarylist)
                    return errorcount_df
            else:
                return None
        else:
            return None



    
    def validationWarningData(self, url, apitoken, submissionname, variables=None):
        if len(submissionname) > 0:
            idlist = self.submission_df.query("name == @submissionname")["_id"].tolist()
            if len(idlist)>=1:
                variables = {"submissionID":idlist[0], "severity":"Warning", "first":-1, "offset":0, "sortDirection": "desc", "orderBy": "displayID"}
                val_res = dhf.dhApiQuery(url=url, apitoken=apitoken, query=dhq.summaryQuery, variables=variables)
                
                warningsummarylist = []
                if val_res['data']['aggregatedSubmissionQCResults']['total'] == 0:
                    return  None
                else:
                    val_df = pd.DataFrame(val_res['data']['aggregatedSubmissionQCResults']['results'])
                    self.warninglist = val_df['title'].unique().tolist()
                    warninglist = val_df['title'].unique().tolist()
                    for warning in warninglist:
                        warning_df = val_df.query('title == @warning')
                        warningsummarylist.append({'Warning': warning, 'Count': warning_df['count'].sum()})
                    warningsummary_df = pd.DataFrame(warningsummarylist)
                    return warningsummary_df
            else:
                return None
        else:
            return None



    
    def fullValidationErrorData(self, url, apitoken, submissionname, variables=None):
        if len(submissionname) > 0:
            idlist = self.submission_df.query("name == @submissionname")["_id"].tolist()
            if len(idlist)>=1:
                # TODO  Need to warn about very large error sets
                firstcount = 1000
                offsetcount = 0
                jsonlength = 1000
                #self.errordetail_df = pd.DataFrame()
                while jsonlength == firstcount:
                    variables = {"id": idlist[0], "severities":"Error", "first": firstcount, "offset": offsetcount, "orderBy":"displayID", "sortDirection":"desc"}
                    error_detail_res = dhf.dhApiQuery(url=url, apitoken=apitoken, query=dhq.detailedQCQuery, variables=variables)
                    jsonlength = len(error_detail_res['data']['submissionQCResults']['results'])
                    temp_df = pd.json_normalize(error_detail_res['data']['submissionQCResults']['results'])
                    self.errordetail_df = pd.concat([self.errordetail_df, temp_df], ignore_index=True)
                    #self.errordetail_df = pd.json_normalize(error_detail_res['data']['submissionQCResults']['results'])
        else:
            self.errordetail_df = pd.DataFrame()
            
            
    def fullValidationErrorTableData(self, errorname):
        if len(errorname) > 0:
            tableinfo = []
            for index, row in self.errordetail_df.iterrows():
                for error in row['errors']:
                    tableinfo.append({'ErrorTitle': error['title'], 'Description': error['description']})
            table_df = pd.DataFrame(tableinfo)
            return table_df.query('ErrorTitle ==@errorname')
        else:
            return pd.DataFrame()
  
  
    
    def fullValidationWarningData(self, url, apitoken, submissionname, variables=None):
        if len(submissionname) > 0:
            idlist = self.submission_df.query("name == @submissionname")["_id"].tolist()
            if len(idlist)>=1:
                variables = {"id": idlist[0], "severities":"Warning", "first": -1, "offset": 0, "orderBy":"displayID", "sortDirection":"desc"}
                warning_detail_res = dhf.dhApiQuery(url=url, apitoken=apitoken, query=dhq.detailedQCQuery, variables=variables)
                self.warningdetail_df = pd.json_normalize(warning_detail_res['data']['submissionQCResults']['results'])
        else:
            self.warningdetail_df = pd.DataFrame()



            
    def fullValidationWarningTableData(self, warningname):
        if len(warningname) > 0:
            tableinfo = []
            for index, row in self.warningdetail_df.iterrows():
                for warning in row['warnings']:
                    tableinfo.append({'WarningTitle': warning['title'], 'Description': warning['description']})
            table_df = pd.DataFrame(tableinfo)
            return table_df.query('WarningTitle == @warningname')
        else:
            return pd.DataFrame()



    
    def errorDropDownValues(self):
        return self.errorlist
    
    def warningDropDownValues(self):
        return self.warninglist
    
    def dataNodeDropDown(self, url, apitoken, submissionname, variables=None):
        if len(submissionname) > 0:
            idlist = self.submission_df.query("name == @submissionname")["_id"].tolist()
            if len(idlist)>=1:
                variables = {'id':idlist[0]}
                data_res = dhf.dhApiQuery(url=url, apitoken=apitoken, query=dhq.submission_stats_query, variables=variables)
                for entry in data_res['data']['submissionStats']['stats']:
                    self.datalist.append(entry['nodeName'])
            return self.datalist
        else:
            self.datalist = []
            return self.datalist



    
    def fullDataNodeTableData(self, url, apitoken, submissionname, nodename, variables=None):
        if len(submissionname) > 0:
            idlist = self.submission_df.query("name == @submissionname")["_id"].tolist()
            if len(idlist) >= 1:
                variables = {'_id':idlist[0], 'nodeType':nodename, 'status':'All', 'first':-1, 'offset':0, 'orderBy':'studyID', 'sortDirection':'desc'}
                data_res = dhf.dhApiQuery(url=url, apitoken=apitoken, query=dhq.submission_nodes_query, variables=variables)
                data_df = pd.DataFrame(columns=data_res['data']['getSubmissionNodes']['properties'])
                for entry in data_res['data']['getSubmissionNodes']['nodes']:
                    data_df.loc[len(data_df)] = json.loads(entry['props'])
                return data_df
        else:
            return pd.DataFrame()
            
    def fullReset(self):
        self.study_df = pd.DataFrame()
        self.submission_df = pd.DataFrame()
        self.errordetail_df = pd.DataFrame()
        self.errorlist = []
        self.warningdetail_df = pd.DataFrame()
        self.warninglist = []
        self.datadetail_df = pd.DataFrame()
        self.datalist = []
        
    def studyReset(self):
        self.submission_df = pd.DataFrame()
        self.errordetail_df = pd.DataFrame()
        self.errorlist = []
        self.warningdetail_df = pd.DataFrame()
        self.warninglist = []
        self.datadetail_df = pd.DataFrame()
        self.datalist = []
    
    def submissionReset(self):
        self.errordetail_df = pd.DataFrame()
        self.errorlist = []
        self.warningdetail_df = pd.DataFrame()
        self.warninglist = []
        self.datadetail_df = pd.DataFrame()
        self.datalist = []