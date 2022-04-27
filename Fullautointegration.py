 '''
Automated integration of 2D images to 1D patterns using pyFAI
Separate directories for each subset of data are created in a specified location
Notes to user:
-provide calibration (.poni) and edge / beamstop mask (.tif)
-define integration method, X units, number of azimuthal points, etc. in first block of code
-lines2skip is to remove metadata in pyFAI generated files which is currently 23 
Written by Adam Corrao: October, 2021.
Last edited: April 27th, 2022
'''
import fabio,pyFAI,os
from time import time
import pandas as pd
############################################EDIT BELOW HERE################################################################
keyword = 'Si' #keyword to look for to autointegrate

calib_dir = os.path.join('D:',os.sep,'Integration_test','calib')
ponif = 'Si_allrings.poni'
maskf = 'Si_mask.tif' #must save mask as a tiff to open with fabio, as an array, or convert file to an array properly
static_mask = fabio.open(calib_dir + os.sep + maskf).data

intmethod = 'Full' #full pixel splitting method, change as needed - defaults to CSR
xunit = '2th_deg' #integrates images to 2theta space, change as needed: q_nm^-1 , q_A^-1, 2th_rad, r_mm, r_m, d*2_nm^-2, d*2_A^-2, etc.
azim_points = int(6000) #number of azimuthal points to integrate 2D image over
neg_mask = float(-1e-10) #automask pixels in 2D image below this value (all negative pixels)
errormodel = 'None' #no error model used, change to 'poisson' for variance = I or 'azimuthal' for variance = (I - <I>)^2

lines2skip = int(23) #number of lines to skip in pyfai generated .xy file - these contain int / calib info

main_dir = os.path.join('D:',os.sep,'Integration_test')
os.chdir(main_dir)

tiff_dir = os.path.join('D:',os.sep,'Integration_test','tiff_base') #location of directory containing tiff folders, main data dump
xy_dir = os.path.join('D:',os.sep,'Integration_test','XY') #directory where you want xy folders to be created

###########################################DON'T EDIT BELOW HERE###########################################################
#This section is to create directories for 1D patterns to be placed based on tiff directory names

if 'XY' in os.listdir(main_dir):
    print('XY directory already exists')
if 'XY' not in os.listdir(main_dir):
    os.mkdir(xy_dir)
    print('Created XY directory')

tiff_folders = []
xy_folders = []

for fold in os.listdir(tiff_dir):
    if keyword in fold: #some string to search for
        tiff_folders.append(fold)

for folder in tiff_folders:
    try:
        os.mkdir(os.path.join(xy_dir, folder))
    except:
        print('folder for ' + folder + ' already exists')

for fold in os.listdir(xy_dir):  #checking that os.mkdir was successful for all indices
    if keyword in fold:
        xy_folders.append(fold)
print('Done making folders, checking if same number of tiff and XY folders')

#check if folders copied properly by len of folder names in each dir
#in future change this to check for matches
if len(os.listdir(tiff_dir)) != len(os.listdir(xy_dir)):
    print('Mismatch in number of tiff and XY folders')
if len(os.listdir(tiff_dir)) == len(os.listdir(xy_dir)):
    print('Same number of tiff and XY folders in respective directories \n\nGood to go - proceeed with integration!')

#############################below here is integration############################################
#This section is to integrate all 2D images in folders matching the keyword and place 1D patterns in relevant directories
ai = pyFAI.load(calib_dir + os.sep + ponif)

dircounter = 0
totalintcount = 0
numtiffdirs = len(os.listdir(tiff_dir))#number of total directories to integrate

t_start = time()
for fold in os.listdir(tiff_dir):
    if keyword in fold: #remove conditional if integrating all or set keyword to character present in all names
        t_fold_start = time() #start time for a tiff folder
        dircounter += 1
        print('\n\nIntegrating folder #' + str(dircounter) + ' of ' + str(numtiffdirs))

        int_dir = tiff_dir + os.sep + fold + os.sep + 'dark_sub' + os.sep #for NSLS-II / xpdacq file paths
        numftoint = len(os.listdir(int_dir)) #number of files to integrate in subdirectory
        xy_toplace = xy_dir + os.sep + fold + os.sep #xy directory to save 1D patterns to
        int_counter = 0
        for file in os.listdir(int_dir):
            if file.endswith('.tiff'):
                int_counter += 1
                totalintcount += 1
                t_int_start = time()
                print('\n\nIntegrating image #' + str(int_counter) + ' of ' + str(numftoint) + ' for ' + str(fold))

                darksub_img = fabio.open(int_dir + file).data
                xy_name = xy_toplace + os.sep + file.strip('.tiff') + '.xy'
                ai.integrate1d(data=darksub_img,mask=static_mask,dummy=neg_mask,method=intmethod,npt=azim_points,error_model=errormodel,filename=xy_name,correctSolidAngle=False,unit=xunit)
                xy_f = pd.read_csv(xy_name,skiprows=lines2skip,delim_whitespace=True,header=None) #dtype=str
                xy_f.columns = ['tth','I']
                xy_f.to_csv(xy_name,index=False,float_format='%.8f',sep='\t')

                t_int_e = time()
                inttime = (t_int_e - t_int_start)
                print('\nTime for single integration and saving: ' + str(inttime) + ' s')
        t_fold_e = time();
        fold_time = (t_fold_e - t_fold_start);
        print('\n\nTime to integrate folder #' + str(dircounter) +' named ' + str(fold) + ' = ' + str(fold_time) + ' s');
t_e = time()
totaltime = (t_e - t_start);
avginttime = (totaltime / totalintcount);
print('\n\nTotal elapsed time:' + str(totaltime) + ' s')
print('\n\nAverage time for full process per image: ' + str(avginttime) + ' s')