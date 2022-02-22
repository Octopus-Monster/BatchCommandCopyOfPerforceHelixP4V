import os
import configparser
import sys

VersionName = sys.argv[1]
JenkinsVersionURL = sys.argv[2]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.sections()
config.read(os.path.join(BASE_DIR, 'ConfigBatchCopyCSV.ini'),encoding= 'utf-8')

P4port = config.get(VersionName,'P4port')
P4user = config.get(VersionName,'P4user')
P4password = config.get(VersionName,'P4password')
P4workspace = config.get(VersionName,'P4workspace')
P4root = config.get(VersionName,'P4root')
ServerAddr = config.get(VersionName,'P4ServerAddr')
ClientAddr = config.get(VersionName,'P4ClientAddr')
CurUpdateListAddr = config.get(VersionName,'CurUpdateListAddr')

def LoadFilesList(Param_FilesListaddr):
    size = os.path.getsize(CurUpdateListAddr)
    if size == 0:
        print('[BatchCopyLOG]'+'未做更改，无需进行Copy操作！！！(No change,no Copy operation required!!!)\n')
        sys.exit()
    Fileslist = open(Param_FilesListaddr, "r")
    List_FileList = Fileslist.readlines()
    Fileslist.close()
    return analysisCurUpdateList(List_FileList)

def analysisCurUpdateList(Param_List_FileList):
    Make_FileList = []
    for item in range(len(Param_List_FileList)):
        if str(Param_List_FileList[item]).split(' ')[2] == 'updating':
            addr,FileName = os.path.split(str(Param_List_FileList[item]).split(' ')[3])
        elif str(Param_List_FileList[item]).split(' ')[2] == 'added':
            addr,FileName = os.path.split(str(Param_List_FileList[item]).split(' ')[4])
            
        Make_FileList.append(FileName)
        print('[BatchCopyLOG]'+str(Param_List_FileList[item]).split(' ')[1])
    return Make_FileList    

def CopyP4Files (Param_CSVFileName):

    p4_msg = os.popen("p4 -p " + P4port + " -u " + P4user + " -p " + P4password + " -c " + P4workspace + " changes -m 1 "+' '+ str(ServerAddr) + str(Param_CSVFileName)).read()
    print('[BatchCopyLOG]'+"p4 -p " + P4port + " -u " + P4user + " -p " + P4password + " -c " + P4workspace + " changes -m 1 "+' '+ str(ServerAddr) + str(Param_CSVFileName))
    if p4_msg != '':
        p4_Copy_Command_msg = os.popen("p4 -p " + P4port + " -u " + P4user + " -p " + P4password + " -c  " + P4workspace + " copy" + ' ' + str(ClientAddr)+str(Param_CSVFileName) + ' ' + str(ServerAddr) + str(Param_CSVFileName)).read()
        if p4_Copy_Command_msg in 'File(s) up-to-date.':
            print('[BatchCopyLOG]'+'[复制命令返回]'+Param_CSVFileName+' 已经被同步(File(s) up-to-date.)\n')
        elif p4_Copy_Command_msg in 'Can\'t copy to target path with files already open.':
            print('[BatchCopyLOG]'+'[复制命令返回]'+Param_CSVFileName+' 文件已被打开无法同步(Can\'t copy to target path with files already open.)\n')
        else: 
            p4_Submit_Command_msg = os.popen("p4 -p " + P4port + " -u " + P4user + " -p " + P4password + " -c  " + P4workspace + " submit -d \"Auto copy\" " + str(ServerAddr) + str(Param_CSVFileName)).read()
            print('[BatchCopyLOG]'+'[上传命令返回]'+p4_Submit_Command_msg)
    elif p4_msg == '':
        print('[BatchCopyLOG]'+'不在目标目录不复制(This file does not exist in the destination directory and will not be copied.)\n')
        

if __name__=='__main__':
    FileLists = LoadFilesList(CurUpdateListAddr)
    for item in range(len(FileLists)):
        print('[BatchCopyLOG]'+'开始Copy(Begin)' + FileLists[item]+'\n')
        CopyP4Files(str(FileLists[item]).rstrip('\n'))
