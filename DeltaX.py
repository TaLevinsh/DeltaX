from _winreg import *
from datetime import *
import re
import sys


MOUNTED_DEVICES = 'System\MountedDevices'
USB = 'System\CurrentControlSet\Enum\USB'
CONFIG = 'C:\Users\Owner\PycharmProjects\Git\DeltaX\Config.txt'     # What keys to scan


def Read_Config():
    F = open(CONFIG, 'r')
    KeyNames = F.read().split('\n')
    return KeyNames


def Translate_Reg_Time(Handle):
    RegTime = QueryInfoKey(Handle)[2]
    Epoch = datetime(1601, 1, 1)
    Calculated = Epoch + timedelta(microseconds=RegTime / 10)
    return Calculated


def Read_Key(Key):
    Results = {}
    Count = 0
    Handle = OpenKey(HKEY_LOCAL_MACHINE, Key)
    try:
        I = 0
        while True:
            Value = EnumValue(Handle, I)
            Results[Value[0]] = Value[1]
            I = I + 1
    except WindowsError:
        pass
    Change_Time = Translate_Reg_Time(Handle)
    return Results, Change_Time


def Update_File(Current_State, FileName):
    Current_Values = Current_State.values()
    F = open(FileName, 'w')
    for V in Current_Values:
        F.write(V + '\n')
    F.close()


def Read_File(FileName):
    F = open(FileName, 'r')
    Results = F.read().split('\n')
    F.close()
    return Results


def Show_Key_Delta():
    KeyNames = Read_Config()
    KeyName = KeyNames[0]
    print 'Found', len(KeyNames), 'keys to scan, type "Y" to apply.'
    for I, K in enumerate(KeyNames):
        Ans = raw_input('[{}] '.format(I + 1) + K + ' >  ')
        if Ans == 'Y':
            KeyName = K
            break
    FileName = 'C:\\Users\\Owner\\PycharmProjects\\Git\\DeltaX\\' + raw_input('Insert baseline file name > ')   # BaseLine.txt
    Baseline = Read_File(FileName)
    Current, ChangeTime = Read_Key(KeyName)
    New = 0
    print
    for C in Current.values():
        if C in Baseline:
            print '(Exists)', C
        else:
            New += 1
            print '@ NEW VALUE @', C
    if New > 0:
        print '\n', New, 'New values have been added.'
        A = raw_input('Would you like to update the baseline file? [Y | N]'
                      '\n> ')
        if A == 'Y':
            Update_File(Current, FileName)
            print 'Baseline updated with', New, 'new entries.'
            print 'Change time:', ChangeTime
    else:
        print '\nNo new entries were found - Current data matches baseline.'
        print 'Change time:', ChangeTime


def Key_Delta_Quick():
    KeyName = 'SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
    FileName = 'C:\\DeltaX\\Registry\\Run.txt'
    Baseline = Read_File(FileName)
    Current, ChangeTime = Read_Key(KeyName)
    New = 0
    print
    for C in Current.values():
        if C in Baseline:
            print '(exists)', C
        else:
            New += 1
            print '@ NEW VALUE @', C
    if New > 0:
        print '\n', New, 'New values have been added.'

        A = raw_input('Would you like to update the baseline file? [Y | N]'
                      '\n> ')
        if A == 'Y':
            Update_File(Current, FileName)
            print 'Baseline updated with', New, 'new entries.'
            print 'Change time:', ChangeTime
    else:
        print '\nNo new entries were found - Current data matches baseline.'
        print 'Change time:', ChangeTime


def Analyze_Key():
    Temp = "VID_(.+)&PID_(.+)"
    Results = []
    Devices = 0
    Vendors = {}
    Handle = OpenKey(HKEY_LOCAL_MACHINE, USB)
    try:
        I = 0
        while True:
            KeyName = EnumKey(Handle, I)
            Results.append(KeyName)
            if re.match('VID*', KeyName):
                Devices += 1
                VidPid = re.search(Temp, KeyName)
                Vid, Pid = VidPid.group(1), VidPid.group(2)
                if Vid in Vendors.keys():
                    Vendors[Vid] += 1
                else:
                    Vendors[Vid] = 1
            I += 1
    except WindowsError:
        pass
    print 'List'
    for i in Results:
        print i
    print '\nTotal of', Devices, 'devices were connected to this host.'
    print '\n\nVendors list'

    for V in Vendors:
        print V, ':', Vendors[V], 'devices'

    whole_keytime = Translate_Reg_Time(Handle)
    print 'Last device connection time:', whole_keytime
    print datetime.now() - whole_keytime, 'ago'
    for R in Results:
        K = OpenKey(HKEY_LOCAL_MACHINE, USB + "\\" + R)
        Keytime = Translate_Reg_Time(K)
        print R, '\nchanged at', Keytime


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == 'Quickscan':
            Key_Delta_Quick()
    else:
        print '- - - Delta X - - -'

        print 'Please select action:'

        Opt = input('[1] Analyze Connected Devices\n'
                    '[2] Show Key Delta\n'
                    '>\t')

        if Opt == 1:
            Analyze_Key()
        if Opt == 2:
            Show_Key_Delta()
        else:
            print 'Invalid Selection!'


if __name__ == '__main__':
    main()
