# Import fuzzywuzzy 
from fuzzywuzzy import fuzz
from fuzzywuzzy	import process

# Import csv module
import csv

# Import regular expressions module 
import re 

# Import easygui 
import easygui

# Input csv files should be placed in the same folder as this python file 
# Get local procedure input csv file name from user using easygui 
local_procedure_msg = "Enter title of csv file containing procedure names to be matched in LOINC-RSNA PLAYBOOK (ex. procedures.csv)"
local_procedure_title = "LOCAL PROCEDURES CSV FILE NAME" 
filename_local_procedure = easygui.enterbox(local_procedure_msg, local_procedure_title)

# Default name of the LOINC-Playbook csv file, user must modify this if the default name is changed!
filename_loinc = "LoincRsnaRadiologyPlaybook.csv"

# Have user select output csv file name using easygui
output_msg = "Enter desired title for output csv file containing match results (ex. results.csv)"
output_title = "OUTPUT CSV FILE NAME" 
writefile = easygui.enterbox(output_msg, output_title)

# Create list to store local procedure names
local_procedure_list = []

# Create dictionary to store LOINC-Playbook procedures 
loinc_dict = {} 

# User selects modality from LOINC options 
modality_msg = "Please select 1 modality in LOINC-RSNA PLAYBOOK for matching."
modality_title = "SELECT MODALITY"
modality_choices = ["CT", "MR", "US", "NM", "PT", "XR", "MG", "DXA", "RF", "RP"]
modality = easygui.choicebox(modality_msg, modality_title, modality_choices)

# User selects body region from LOINC options
body_region_msg = "Please select 1 body region in LOINC-RSNA PLAYBOOK for matching. \n(You can select >1 choice but this may decrease the accuracy of the match results)"
body_region_title = "SELECT BODY REGION"
body_region_choices = ["Head", "Neck", "Chest", "Breast", "Abdomen", "Pelvis", "Extremity", "Upper extremity", "Lower extremity", "Whole body", "Unspecified"]
body_region = easygui.multchoicebox(body_region_msg, body_region_title, body_region_choices)

# Open and read through local procedure csv file 
with open(filename_local_procedure) as f_obj_local_procedure_list:
	reader_local_procedure_list = csv.reader(f_obj_local_procedure_list)

	for row_local_procedure_list in reader_local_procedure_list:

		# Store local procedure names in list 
		local_procedure_list.append(row_local_procedure_list[0])

# Open and read through LOINC-RSNA Playbook csv file 
with open(filename_loinc) as f_obj_loinc_dict:
	reader_loinc_dict = csv.reader(f_obj_loinc_dict)
	
	for row_loinc_dict in reader_loinc_dict:

		# Only include procedures in body region of interest specified by column 5 PartName in LOINC-RSNA Playbook 
		for body_region_selection in body_region:
			if row_loinc_dict[4] == body_region_selection:

				# key is LOINC name, values are LOINC number and RPID	 
				loinc_dict[row_loinc_dict[1]] = [row_loinc_dict[0], row_loinc_dict[8]]

# Create list to store fuzzy matches  
fuzz_list = []

# Loop through each local procedure name 
for local_procedure in local_procedure_list:

	# Capitalize all letters in all local procedure names to facilitate comparision 
	local_procedure = local_procedure.upper()

	# Partial string replacement to standardize contrast terms with respect to LOINC to improve fuzzy matching 
	local_procedure = local_procedure.replace("+", "AND")
	local_procedure = local_procedure.replace("WITHOUT", "WO")
	local_procedure = local_procedure.replace("WITH", "W")
	local_procedure = re.sub(r"\bCON\b", "CONTRAST", local_procedure) 
	
	# Account for preferred synonyms in LOINC 
	local_procedure = local_procedure.replace("CTA", "CT ANGIOGRAM")
	local_procedure = local_procedure.replace("MRA", "MR ANGIOGRAM") 
	local_procedure = local_procedure.replace("RENAL", "KIDNEY")
	local_procedure = local_procedure.replace("ENTEROGRAPHY", "SMALL BOWEL")
	local_procedure = local_procedure.replace("UROGRAM", "KIDNEY AND URETER AND URINARY BLADDER")
	local_procedure = local_procedure.replace("MRCP", "ABDOMEN MRCP")
	local_procedure = re.sub(r"\bANGIOGRA\w..", "VESSELS ANGIOGRAM", local_procedure)
	local_procedure = re.sub(r"\bVENOGRA\w..", "VEINS ANGIOGRAM", local_procedure)

	# Remove extraneous terms to improve fuzzy matching
	local_procedure = local_procedure.replace("PROTOCOL", " ")
	
	# Loop through each LOINC-RSNA Playbook procedure 
	for loinc_name, idnum in loinc_dict.items():

		# Capitalize all letters in all LOINC-RSNA Playbook procedure names to faciltate comparision 
		loinc_name = loinc_name.upper()

		# Account for lack of modality specification in name for SPECT procedures in LOINC-RSNA Playbook prior to modality selection in next step
		loinc_name = loinc_name.replace("SPECT", "SPECT NM")

		# Select modality via LOINC-RSNA Playbook procedure name using regular expressions 
		modality_regex = r"\b" + re.escape(modality) + r"."
		if re.search(modality_regex, loinc_name):

			# Utilize fuzzywuzzy for fuzzy matching. Generate token sort ratio and store this value in variable wuzzy 
			wuzzy = fuzz.token_sort_ratio(local_procedure, loinc_name)

			# Add token sort ratio, LOINC-RSNA Playbook procedure name, LOINC number, RPID to fuzz_list
			holder = (wuzzy, loinc_name, idnum[0], idnum[1])
			fuzz_list.append(holder)

	# Sort fuzz list to identify token sort ratios in descending order 
	fuzz_list.sort(reverse=True)

	# Store local procedure names as list to write to csv
	local_procedure_list = [local_procedure]

	# Open and append output csv file 
	with open(writefile, "a") as f:
		writer = csv.writer(f)
		writer.writerow(local_procedure_list)

		# List top 5 fuzzy matches for each local procedure 
		writer.writerow(fuzz_list[0])
		writer.writerow(fuzz_list[1])
		writer.writerow(fuzz_list[2])
		writer.writerow(fuzz_list[3])
		writer.writerow(fuzz_list[4])
	
	# Clear list for next local procedure  
	del fuzz_list[:] 

