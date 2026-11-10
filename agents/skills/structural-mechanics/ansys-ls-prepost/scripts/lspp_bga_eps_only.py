# -*- coding: utf-8 -*-
import time
import time as _act_time
_ACT_START_TIME = _act_time.time()
import DataCenter as dc

def log_usage(act_name, act_version, elapsed_sec, manual_sec):
    try:
        import clr
        import datetime
        clr.AddReference("System")
        from System import Environment
        from System.IO import FileStream, StreamWriter, FileMode, FileAccess, FileShare, Directory

        user_name = Environment.UserName
        machine_name = Environment.MachineName
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        month = datetime.datetime.now().strftime("%Y_%m")

        log_dir = r"\\Twtrkei017\e\Structure_shared_folder\03. Team member\Ikaros\Test_ACT_usage_rate"

        if not Directory.Exists(log_dir):
            Directory.CreateDirectory(log_dir)

        log_path = log_dir + "\\usage_" + month + ".csv"
        saved_sec = manual_sec - elapsed_sec
        log_line = "{},{},{},{},{},{},{},{}\n".format(
            timestamp, user_name, machine_name,
            act_name, act_version,
            "%.1f" % elapsed_sec,
            manual_sec,
            "%.1f" % saved_sec
        )

        fs = FileStream(log_path, FileMode.Append, FileAccess.Write, FileShare.ReadWrite)
        writer = StreamWriter(fs)
        writer.Write(log_line)
        writer.Flush()
        writer.Close()
        fs.Close()
    except Exception as e:
        pass

import LsPrePost as lspp
import pandas as pd
import time


import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox

from LsPrePost import cmd_result_get_value as crgv, execute_command as exec
import openpyxl
from openpyxl import Workbook
from openpyxl.drawing.image import Image
import numpy as np

#?? ?
start_time = time.time()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~Preparation for part_data.csv~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Export part_data.csv manually 

#command = 'genselect target part'
#lspp.execute_command(command)
#command = 'selectpart select 1'
#lspp.execute_command(command)
#command = 'partsort sort'
#lspp.execute_command(command)
#command = 'partsort done'    #close and open again
#lspp.execute_command(command)
#command = 'selectpart select 0'
#lspp.execute_command(command)
#command = 'genselect target part'
#lspp.execute_command(command)
#command = 'selectpart select 1'
#lspp.execute_command(command)
#command = 'partsort sort'
#lspp.execute_command(command)
#command = 'partsort sort' #open twice
#lspp.execute_command(command)
#command = 'partsort allpart'
#lspp.execute_command(command)
#command = 'partsort fieldset none'
#lspp.execute_command(command)
#command = 'partsort fieldset 1 1'
#lspp.execute_command(command)
#command = 'partsort fieldset 3 1'
#lspp.execute_command(command)
#command = 'partsort fieldset 16 1'
#lspp.execute_command(command)
#command = 'partsort write "part_data.csv"'
#lspp.execute_command(command)
#command = 'partsort done'
#lspp.execute_command(command)
#command = 'selectpart select 0'
#lspp.execute_command(command)


#Catch all Parts ID & Quantity of Parts
part_ids = dc.get_data("validpart_ids")
part_num = part_ids.__len__()
Element_num=dc.get_data("num_elements")

part_num2=part_num

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~Overall Result table Export~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

wb = openpyxl.Workbook()
wb.save('EPS_lastState_EachPart.xlsx')#file name ???str ? ??Shock ?
# ?? Excel  ?? Sheet ??
wb = openpyxl.load_workbook('EPS_lastState_EachPart.xlsx', data_only=True)   
wb.create_sheet('EPS_each') #sheet name ???str ? ??Shock Direction
wb.create_sheet('EPS_each_HotZone_RiskArea') #sheet name ???str ? ??Shock Direction
wb.create_sheet('HotZone_RiskArea_Summary') #sheet name ???str ? ??Shock Direction 
s0 = wb['Sheet'] 
wb.remove(s0)
  

# ?? ??
s1 = wb['EPS_each'] 
s5 = wb['EPS_each_HotZone_RiskArea']
s6 = wb['HotZone_RiskArea_Summary']
# Define the column title
s1.cell(1,1).value = 'Part_id '
s1.cell(1,2).value = 'Part_name '
s1.cell(1,3).value = 'EPS_Max '
s1.cell(1,4).value = 'Pass or Fail based on criteria 0.01 '
s1.cell(1,5).value = 'Illustration_isoX '
s1.cell(1,6).value = 'Illustration_isoY '
s1.cell(1,7).value = 'Illustration_isoZ '

s5.cell(1,1).value = 'Part_id '
s5.cell(1,2).value = 'Part_name '
s5.cell(1,3).value = 'EPS_Max '
s5.cell(1,4).value = 'Pass or Fail based on criteria 0.01 '
s5.cell(1,5).value = 'Illustration_isoX '
s5.cell(1,6).value = 'Illustration_isoY '
s5.cell(1,7).value = 'Illustration_isoZ '


wb.save('EPS_lastState_EachPart.xlsx')
#Catch all Parts ID & Quantity of Parts
#part_ids = dc.get_data('validpart_ids')
#part_name = dc.get_data('part_name')
#expart_num = part_ids.__len__()

#Move to the last state
laststep=dc.get_data("num_states")
lspp.execute_command(f'state {laststep}')
#Close mesh line
command = 'mesh off '
lspp.execute_command(command)
command = 'selectpart all on'
lspp.execute_command(command)
#Hide RBE2
command = 'selectpart nrbody off '
exec(command)
#send command to fringe EPS (which corrsponds to the digit 7), once it is sent, LSPP would temporarily store element id and max fringe value for active parts, which can be retrieved later.
exec("fringe 7; pfringe")

#select each part to export EPS on overall table & extract part_name from part_data.csv
#df = pd.read_csv("part_data.csv")
for i in range(part_num2):
    part_id = part_ids[i] 
    s1.cell(i+2,1).value = part_id     
    #show part_id only to ensure that both element_id and max_eps LSPP stores are for current active part
    exec(f"selectpart on {part_id}")
    #retrieve element id and max fringe value of current active part from LSPP 
    element_id = crgv(0)    
    max_eps = crgv(1)
    s1.cell(i+2,3).value = max_eps    
    #print(f"max EPS of the part {part_id} is {max_eps} which happens at element {element_id}")
    #partname=df.loc[df["PartId"] == part_id,"PartName"].values[0]
    partname = dc.get_data("part_name",id = i)
    s1.cell(i+2,2).value = partname 
       
wb.save('EPS_lastState_EachPart.xlsx')
# ?? Excel  ?
wb = openpyxl.load_workbook('EPS_lastState_EachPart.xlsx', data_only=True)     
# ?? ??
s1 = wb['EPS_each'] 
s5 = wb['EPS_each_HotZone_RiskArea']

command = 'selectpart all on'
lspp.execute_command(command)
command = 'ac'
lspp.execute_command(command)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~Hot-zone & Risk area judgement~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
j=0
for i in range(part_num2):
    judgeEPS=s1.cell(i+2,3).value
    if  judgeEPS > 0.01:
     j=j+1
     s1.cell(i+2,4).value = 'Fail, need to check if element-go-through-the-section'
     s5.cell(j+1,1).value=s1.cell(i+2,1).value
     s5.cell(j+1,2).value=s1.cell(i+2,2).value
     s5.cell(j+1,3).value=s1.cell(i+2,3).value
     s5.cell(j+1,4).value=s1.cell(i+2,4).value     
#     img = Image('EPS_part_{}_isoX.png'.format(part_ids[i]))
#     img.width, img.height=50, 20
#     s5.add_image(img, 'E{}'.format(j+1))
#     img = Image('EPS_part_{}_isoY.png'.format(part_ids[i]))
#     img.width, img.height=50, 20
#     s5.add_image(img, 'F{}'.format(j+1))
#     img = Image('EPS_part_{}_isoZ.png'.format(part_ids[i]))
#     img.width, img.height=50, 20
#     s5.add_image(img, 'G{}'.format(j+1))    
    else:
     s1.cell(i+2,4).value = 'Pass, no risk' 

wb.save('EPS_lastState_EachPart.xlsx')

# ?? Excel  ?
wb = openpyxl.load_workbook('EPS_lastState_EachPart.xlsx', data_only=True)     
# ?? ??

s5 = wb['EPS_each_HotZone_RiskArea']
s6 = wb['HotZone_RiskArea_Summary']

command = 'selectpart all off'
lspp.execute_command(command)
command = 'ac'
lspp.execute_command(command)

#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~Hot-zone & Risk area illustration~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Highlight the Risk parts
command = 'shad'
lspp.execute_command(command)
command = 'selectpart all off'
lspp.execute_command(command)

for k in range(j):
   partid=s5.cell(k+2,1).value
   command = '+m {}'.format(partid)
   lspp.execute_command(command)

command = 'ident select 1 '
lspp.execute_command(command)
command = 'genselect target part '
lspp.execute_command(command)
command = 'genselect allvis '
lspp.execute_command(command)
command = 'ident partname off '
lspp.execute_command(command)
command = 'ident select 0 '
lspp.execute_command(command)
command = 'selectpart reverse '
lspp.execute_command(command)
command = 'color select 1 '
lspp.execute_command(command)
command = 'color option 1 '
lspp.execute_command(command)
command = 'color global 0.705882 0.705882 0.705882 '
lspp.execute_command(command)
command = 'genselect reverse '
lspp.execute_command(command)
command = 'color option 2 '
lspp.execute_command(command)
command = 'transp global 0.5    ; '
lspp.execute_command(command)
command = 'genselect reverse '
lspp.execute_command(command)
command = 'selectpart all on '
lspp.execute_command(command)
command = 'selectpart nrbody off '
lspp.execute_command(command)
#command = 'subset partlabel on '
#lspp.execute_command(command)

#Print isometric_X
command = 'isometric x'
lspp.execute_command(command)
command = 'ac'
lspp.execute_command(command)
command = (
        'print png HotZone_isoX.png LANDSCAPE nocompress '
        'gamma 1.000 opaque enlisted \"OGL1x1\"'
   )
lspp.execute_command(command)
 #Print isometric_Y
command = 'isometric y'
lspp.execute_command(command)
command = 'ac'
lspp.execute_command(command)
command = (
        'print png HotZone_isoY.png LANDSCAPE nocompress '
        'gamma 1.000 opaque enlisted \"OGL1x1\"'
   )
lspp.execute_command(command)
 #Print isometric_Z
command = 'isometric z'
lspp.execute_command(command)
command = 'ac'
lspp.execute_command(command)
command = (
        'print png HotZone_isoZ.png LANDSCAPE nocompress '
        'gamma 1.000 opaque enlisted \"OGL1x1\"'
   )
lspp.execute_command(command)

#Export 3 isometric view pictures of HorZone parts of all on overall table    
img = Image('HotZone_isoX.png')
img.width, img.height=500, 500
s6.add_image(img, 'A1')
img = Image('HotZone_isoY.png')
img.width, img.height=500, 500
s6.add_image(img, 'J1') 
img = Image('HotZone_isoZ.png')
img.width, img.height=500, 500
s6.add_image(img, 'S1') 

wb.save('EPS_lastState_EachPart.xlsx')

# ? ?
end_time = time.time()
elapsed = end_time - start_time

# ? ?
root = tk.Tk()
root.withdraw() #?? ??
print("LSPP BGA EPS completed")
try:
    act_elapsed_sec = _act_time.time() - _ACT_START_TIME
    log_usage("LSPP", "20250729", act_elapsed_sec, 5400)
except:
    pass
