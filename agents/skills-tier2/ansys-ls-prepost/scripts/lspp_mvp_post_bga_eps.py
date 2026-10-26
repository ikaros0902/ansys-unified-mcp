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

# Headless-safe parameter extraction
import os

proj_name = os.environ.get("SIMULATION_PROJECT_NAME", "Project_Analysis")
purpose = os.environ.get("SIMULATION_PURPOSE", "Drop Impact Post Processing")
simul_item = os.environ.get("SIMULATION_ITEM", "BGA Solder Ball")
simul_condition = os.environ.get("SIMULATION_CONDITION", "Standard JEDEC Drop")
cad_version = os.environ.get("CAD_VERSION", "V1.0")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~Preparation for part_data.csv~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
command = 'genselect target part'
lspp.execute_command(command)
command = 'selectpart select 1'
lspp.execute_command(command)
command = 'partsort sort'
lspp.execute_command(command)
command = 'partsort done'
lspp.execute_command(command)
command = 'selectpart select 0'
lspp.execute_command(command)
command = 'genselect target part'
lspp.execute_command(command)
command = 'selectpart select 1'
lspp.execute_command(command)
command = 'partsort sort'
lspp.execute_command(command)
command = 'partsort allpart'
lspp.execute_command(command)
command = 'partsort fieldset none'
lspp.execute_command(command)
command = 'partsort fieldset 1 1'
lspp.execute_command(command)
command = 'partsort fieldset 3 1'
lspp.execute_command(command)
command = 'partsort fieldset 16 1'
lspp.execute_command(command)
command = 'partsort write "part_data.csv"'
lspp.execute_command(command)
command = 'partsort done'
lspp.execute_command(command)
command = 'selectpart select 0'
lspp.execute_command(command)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~FE-Model illustration~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#select all parts to show on screen  
command = 'selectpart all on'
lspp.execute_command(command)
command = 'selectpart nrbody off '
lspp.execute_command(command)
command = 'genselect allvis '
lspp.execute_command(command)
command = 'shad'
lspp.execute_command(command)
 #Print isometric_X
command = 'isometric x'
lspp.execute_command(command)
command = 'ac'
lspp.execute_command(command)
command = 'clearpick '
lspp.execute_command(command)
command = (
        'print png FE-Model_all_isoX.png LANDSCAPE nocompress '
        'gamma 1.000 opaque enlisted \"OGL1x1\"'
   )
lspp.execute_command(command)
 #Print isometric_Y
command = 'isometric y'
lspp.execute_command(command)
command = 'ac'
lspp.execute_command(command)
command = (
        'print png FE-Model_all_isoY.png LANDSCAPE nocompress '
        'gamma 1.000 opaque enlisted \"OGL1x1\"'
   )
lspp.execute_command(command)
 #Print isometric_Z
command = 'isometric z'
lspp.execute_command(command)
command = 'ac'
lspp.execute_command(command)
command = (
        'print png FE-Model_all_isoZ.png LANDSCAPE nocompress '
        'gamma 1.000 opaque enlisted \"OGL1x1\"'
   )
lspp.execute_command(command)




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~EPS Curve~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Close all curve windows before .py execution

#Catch all Parts ID & Quantity of Parts
part_ids = dc.get_data("validpart_ids")
part_num = part_ids.__len__()
Element_num=dc.get_data("num_elements")

#Show all parts on screen
for i in range(part_num):
    # Build command to draw one part, also Auto center it 
    command = '+m {}'.format(part_ids[i])
    lspp.execute_command(command)
#select all parts to show on screen  
command = 'selectpart nrbody off '
lspp.execute_command(command)
command = 'clearpick '
lspp.execute_command(command)
command = 'genselect target part '
lspp.execute_command(command)
command = 'genselect allvis '
lspp.execute_command(command)
command = 'maxvalue 7 '
lspp.execute_command(command)
command = 'xyplot 1 legend off'
lspp.execute_command(command)
# Print the EPS Curve picture with png format
command = 'print png EPS_Curve.png LANDSCAPE nocompress transparent enlisted "PlotWindow-1" ' 
lspp.execute_command(command)
command ='xyplot 1 ymax 0.05 '
lspp.execute_command(command)
command = 'print png EPS_Curve_adjustYmax.png LANDSCAPE nocompress transparent enlisted "PlotWindow-1" ' 
lspp.execute_command(command)



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~Piture & Animation creation~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Catch all Parts ID & Quantity of Parts
#part_ids = dc.get_data('validpart_ids')
#part_num = part_ids.__len__()

#Move to the last state
laststep=dc.get_data("num_states")
lspp.execute_command(f'state {laststep}')
#Hide RBE2
command = 'selectpart nrbody off '
lspp.execute_command(command)
#Close mesh line
command = 'mesh off '
lspp.execute_command(command)


#Show all parts to show on screen & print EPS contour with png format
for i in range(part_num): 
    command = '+m {}'.format(part_ids[i])
    lspp.execute_command(command)
command = 'fringe 7 '
lspp.execute_command(command)
command = 'pfringe '
lspp.execute_command(command)
command = 'clearpick '
lspp.execute_command(command)
command =('range userdef 0 0.01'   )
lspp.execute_command(command)
command =('range fringelimit ucolor 1 0 1'   )
lspp.execute_command(command)
command =('range fringelimit lower_off upper_on')
lspp.execute_command(command)
command =('range pal hue max 66')
lspp.execute_command(command)
command = 'range identmax 1'
lspp.execute_command(command)
 #Print isometric_X
command = 'isometric x'
lspp.execute_command(command)
command = 'ac'
lspp.execute_command(command)
command = (
        'print png EPS_AllPart_isoX.png LANDSCAPE nocompress '
        'gamma 1.000 opaque enlisted \"OGL1x1\"'
   )
lspp.execute_command(command)
 #Print isometric_Y
command = 'isometric y'
lspp.execute_command(command)
command = 'ac'
lspp.execute_command(command)
command = (
        'print png EPS_AllPart_isoY.png LANDSCAPE nocompress '
        'gamma 1.000 opaque enlisted \"OGL1x1\"'
   )
lspp.execute_command(command)
 #Print isometric_Z
command = 'isometric z'
lspp.execute_command(command)
command = 'ac'
lspp.execute_command(command)
command = (
        'print png EPS_AllPart_isoZ.png LANDSCAPE nocompress '
        'gamma 1.000 opaque enlisted \"OGL1x1\"'
   )
lspp.execute_command(command)
#Export animation with gif format
command = 'shad'
lspp.execute_command(command)
command = 'selectpart all on'
lspp.execute_command(command)
 #Animation isometric_X
command = 'isometric x'
lspp.execute_command(command)
command = 'ac'
lspp.execute_command(command)
command = (
        'movie gif 1478x884 Animation_AllPart_isoX  '
        '1 10'
   )
lspp.execute_command(command)
 #Animation isometric_Y
command = 'isometric y'
lspp.execute_command(command)
command = 'ac'
lspp.execute_command(command)
command = (
        'movie gif 1478x884 Animation_AllPart_isoY '
        '1 10'
   )
lspp.execute_command(command)
 #Animation isometric_Z
command = 'isometric z'
lspp.execute_command(command)
command = 'ac'
lspp.execute_command(command)
command = (
        'movie gif 1478x884 Animation_AllPart_isoZ '
        '1 10'
   )
lspp.execute_command(command)



#select each part to show on screen  & print EPS contour with png format sequently_isometric_view
for i in range(part_num):
# Build command to draw one part, also Auto center it 
    command = 'm {}'.format(part_ids[i])
    lspp.execute_command(command)
    command = 'fringe 7 '
    lspp.execute_command(command)
    command = 'clearpick '
    lspp.execute_command(command)
    command = 'pfringe '
    lspp.execute_command(command)
    command = 'range identmax 1'
    lspp.execute_command(command)
    command = 'ac'
    lspp.execute_command(command)
    command = 'isometric x'
    lspp.execute_command(command)
    command = (
    'print png EPS_part_{}_isoX.png LANDSCAPE nocompress '
    'gamma 1.000 opaque enlisted \"OGL1x1\"'.format(part_ids[i])
    )
    lspp.execute_command(command)
    command = 'ac'
    lspp.execute_command(command)
    command = 'isometric y'
    lspp.execute_command(command)
    command = (
    'print png EPS_part_{}_isoY.png LANDSCAPE nocompress '
    'gamma 1.000 opaque enlisted \"OGL1x1\"'.format(part_ids[i])
    )
    lspp.execute_command(command)
    command = 'ac'
    lspp.execute_command(command)
    command = 'isometric z'
    lspp.execute_command(command)
    command = (
    'print png EPS_part_{}_isoZ.png LANDSCAPE nocompress '
    'gamma 1.000 opaque enlisted \"OGL1x1\"'.format(part_ids[i])
    )
    lspp.execute_command(command)



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~Overall Result table Export~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

wb = openpyxl.Workbook()
wb.save('EPS_lastState_EachPart.xlsx')#file name ???str ? ??Shock ?
# ?? Excel  ?? Sheet ??
wb = openpyxl.load_workbook('EPS_lastState_EachPart.xlsx', data_only=True)   
wb.create_sheet('Overall_FE-Model_illustration') #sheet name ???str ? ??Shock Direction 
wb.create_sheet('HotZone_RiskArea_Summary') #sheet name ???str ? ??Shock Direction 
wb.create_sheet('EPS_all_curve') #sheet name ???str ? ??Shock Direction
wb.create_sheet('EPS_all_pic') #sheet name ???.3?str ? ??Shock Direction    
wb.create_sheet('EPS_each') #sheet name ???str ? ??Shock Direction
wb.create_sheet('EPS_each_HotZone_RiskArea') #sheet name ???str ? ??Shock Direction
s0 = wb['Sheet'] 
wb.remove(s0)
  

# ?? ??
s1 = wb['EPS_each'] 
s2 = wb['EPS_all_pic'] 
s3 = wb['EPS_all_curve'] 
s4 = wb['Overall_FE-Model_illustration']
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
s4.cell(1,1).value = 'Project name?'
s4.cell(1,2).value = proj_name #??str ? ???
s4.cell(2,1).value = 'Purpose?'
s4.cell(2,2).value = purpose  #??str ? ???
s4.cell(3,1).value = 'Simulation item?'
s4.cell(3,2).value = simul_item #??str ? ???
s4.cell(4,1).value = 'Simulation condition?'
s4.cell(4,2).value = simul_condition#??str ? ???
s4.cell(5,1).value = 'CAD version?'
s4.cell(5,2).value = cad_version#??str ? ???
s4.cell(6,1).value = 'Total weight of FE-Model(kg)?'
s4.cell(7,1).value = 'Element size?'
s4.cell(8,1).value = 'Result in brief?'
s4.cell(9,1).value = 'Illustration'



#total mass calculation and export
df = pd.read_csv("part_data.csv")
print(df["Mass"])
total_mass=df["Mass"].sum()
total_mass_kg=total_mass*1000
s4.cell(6,2).value = total_mass_kg


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
df = pd.read_csv("part_data.csv")
for i in range(part_num):
    part_id = part_ids[i] 
    s1.cell(i+2,1).value = part_id     
    #show part_id only to ensure that both element_id and max_eps LSPP stores are for current active part
    exec(f"selectpart on {part_id}")
    #retrieve element id and max fringe value of current active part from LSPP 
    element_id = crgv(0)    
    max_eps = crgv(1)
    s1.cell(i+2,3).value = max_eps    
    print(f"max EPS of the part {part_id} is {max_eps} which happens at element {element_id}")
    #part_name=df.loc[df["PartId"] == part_id,"PartName"].values[0]
    part_name = dc.get_data("part_name",id = i)
    s1.cell(i+2,2).value = part_name 
       
wb.save('EPS_lastState_EachPart.xlsx')
# ?? Excel  ?
wb = openpyxl.load_workbook('EPS_lastState_EachPart.xlsx', data_only=True)     
# ?? ??
s1 = wb['EPS_each'] 
s2 = wb['EPS_all_pic'] 
s3 = wb['EPS_all_curve'] 
s4 = wb['Overall_FE-Model_illustration']
s5 = wb['EPS_each_HotZone_RiskArea']
s6 = wb['HotZone_RiskArea_Summary']

command = 'selectpart all on'
lspp.execute_command(command)
command = 'ac'
lspp.execute_command(command)
s4.cell(7,2).value = Element_num

#Export 3 isometric view pictures of each part on overall table
for i in range(part_num):
    img = Image('EPS_part_{}_isoX.png'.format(part_ids[i]))
    img.width, img.height=50, 20
    s1.add_image(img, 'E{}'.format(i+2))
    img = Image('EPS_part_{}_isoY.png'.format(part_ids[i]))
    img.width, img.height=50, 20
    s1.add_image(img, 'F{}'.format(i+2))
    img = Image('EPS_part_{}_isoZ.png'.format(part_ids[i]))
    img.width, img.height=50, 20
    s1.add_image(img, 'G{}'.format(i+2))

#Export 3 isometric view pictures of all parts on overall table    
img = Image('EPS_AllPart_isoX.png')
img.width, img.height=500, 500
s2.add_image(img, 'A1')
img = Image('EPS_AllPart_isoY.png')
img.width, img.height=500, 500
s2.add_image(img, 'J1') 
img = Image('EPS_AllPart_isoZ.png')
img.width, img.height=500, 500
s2.add_image(img, 'S1') 
  
#Export 3 isometric view animations of all parts on overall table
img = Image('Animation_AllPart_isoX.gif')
img.width, img.height=500, 500
s2.add_image(img, 'A27')
img = Image('Animation_AllPart_isoY.gif')
img.width, img.height=500, 500
s2.add_image(img, 'J27') 
img = Image('Animation_AllPart_isoZ.gif')
img.width, img.height=500, 500
s2.add_image(img, 'S27')   

#Export 3 isometric view pictures of all parts_FE-Model on overall table
img = Image('EPS_Curve.png')
img.width, img.height=500, 500
s3.add_image(img, 'A1') 
img = Image('EPS_Curve_adjustYmax.png')
img.width, img.height=500, 500
s3.add_image(img, 'J1')   

img = Image('FE-Model_all_isoX.png')
img.width, img.height=500, 500
s4.add_image(img, 'B9')
img = Image('FE-Model_all_isoY.png')
img.width, img.height=500, 500
s4.add_image(img, 'K9') 
img = Image('FE-Model_all_isoZ.png')
img.width, img.height=500, 500
s4.add_image(img, 'T9')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~Hot-zone & Risk area judgement~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
j=0
for i in range(part_num):
    judgeEPS=s1.cell(i+2,3).value
    if  judgeEPS > 0.01:
     j=j+1
     s1.cell(i+2,4).value = 'Fail, need to check if element-go-through-the-section'
     s5.cell(j+1,1).value=s1.cell(i+2,1).value
     s5.cell(j+1,2).value=s1.cell(i+2,2).value
     s5.cell(j+1,3).value=s1.cell(i+2,3).value
     s5.cell(j+1,4).value=s1.cell(i+2,4).value     
     img = Image('EPS_part_{}_isoX.png'.format(part_ids[i]))
     img.width, img.height=50, 20
     s5.add_image(img, 'E{}'.format(j+1))
     img = Image('EPS_part_{}_isoY.png'.format(part_ids[i]))
     img.width, img.height=50, 20
     s5.add_image(img, 'F{}'.format(j+1))
     img = Image('EPS_part_{}_isoZ.png'.format(part_ids[i]))
     img.width, img.height=50, 20
     s5.add_image(img, 'G{}'.format(j+1))    
    else:
     s1.cell(i+2,4).value = 'Pass, no risk' 

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
# root.withdraw() bypassed #?? ??
print("LSPP extraction completed")
try:
    act_elapsed_sec = _act_time.time() - _ACT_START_TIME
    log_usage("LSPP", "20250920", act_elapsed_sec, 5400)
except:
    pass
