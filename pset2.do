clear all
capture log close
set more off
/**************************************************************************************
	ECONOMICS OF EDUCATION
	PROBLEM SET 2
	AKANKSHA SONI AND BIANCA ONWUKWE


**************************************************************************************/

***********User globals***************
		
		
		if "`c(username)'" == "b"  {
		global user "/Users/b/Desktop/PhD"
		}
		
		if "`c(username)'" == "akankshasoni" {
		global user "/Users/akankshasoni/Dropbox" 
		}	
 
******** Path tree*****************

	global input "$user/Econ of Ed/Pset2"
	global output "$user/Econ of Ed/Pset2/output"

***********************************************************************************************


/*1. Estimating preferences over school attributes */
//Importing data file from Econ of Ed
	clear
	import delimited "${input}/school-choice-data.csv"
	save scdata, replace
	desc
	tab student_id 
	// max number of options =30, student applications are exhaustive for every student 
	tab school_id (ranking) 
	
	// what schools are commonly ranked in a students top 5? or top 3?- what are 
	//their characterisitics?
	//are students sensitive to distance?
	//what schools are they most likley to rank?
	//what is the distribution of minority students? what schools are they more likely to rank why?
	//are minority, low ses, or high ses students more sensitive to distance?
	//are minority, low ses, or high ses students more sensitive to school va?
	//are minority, low ses, or high ses students more sensitive to sports?
	//are minority, low ses, or high ses students more sensitive to higher  
	// ranking sportts schools?
	

/*a. Table 1: Students */
	egen medhh= median(student_hhincome) 
	gen ses=0
	replace ses=student_hhincome>=medhh
	label var ses "Student Socioeconomic Status"
	label define ses 1 "High-SES" 0 "Low-SES"
	label values ses ses
	
	label var student_minority "Minority"
	label define student_minority 1 "Minority" 0 "Non-Minority"
	label values student_minority student_minority
	
	label var student_sibling "Has Sibling"
	label define student_sibling 1 "Yes" 0 "No"
	label values student_sibling student_sibling
	
	label var student_hhincome "Household Income"
	
	preserve
	duplicates drop student_id, force
	tab student_sibling

	
	dtable student_hhincome i.student_minority i.student_sibling, by(ses) continuous(student_hhincome, stat(mean) test(none)) sample (, statistics (freq) place(seplabels)) sformat("(N=%s)" frequency) note(Total sample: N= ) nformat(%7.2f mean) title(Table 1. Student Demographics) export(table1.tex, replace)

	restore

/*a. Table 2: Schools */
	label var school_needs "Serves SPED"
	label define school_needs 1 "Yes" 0 "No"
	label values school_needs school_needs
	
	gen sports_rank=0
	replace sports_rank=school_sports>=5
	label var sports_rank "Sports Performance Ranking"
	label define sports_rank 1 "High" 0 "Low"
	label values sports_rank sports_rank
	
	preserve
	duplicates drop school_id, force
	tab school_sports
	dtable school_va school_cap i.sports_rank, by(school_needs) continuous(school_va, stat(mean) test(none)) continuous(school_cap, stat(mean) test(none)) sample (, statistics (freq) place(seplabels)) sformat("(N=%s)" frequency) note(Total sample: N= ) nformat(%7.2f mean) title(Table 1. School Statistics) export(table2.tex, replace)
	restore
	
	
	
/*b. Denote the utility of household i of type r obtains from school j as:
urij = -ardij + x0jbr + #ij
where dij is the distance between to school j and xj is a vector of school attributes that includes
school value added, the sports index and whether the school covers special needs,
and #ij is an i.i.d. preference shock that follows a T1EV distribution.
One way in which to utilize this data for estimation of preferences over school attributes is
to use a exploded logit. Describe this strategy and write down the likelihood function for
the data.

 */
	
*******C
	gen choice1School=0 
	replace choice1School=1 if ranking==1
	cmset student_id school_id
	cmrologit choice1School school_va distance sports_rank school_needs //need to add cluster later 
	
*******D. 
cmset student_id school_id
cmrologit ranking school_va distance sports_rank school_needs, reverse //need to add cluster later 

******E 
********If SES=high 

preserve
keep if ses==1
cmset student_id school_id
cmrologit ranking school_va distance sports_rank school_needs, reverse //need to add cluster later 
restore

preserve
keep if ses==0
cmset student_id school_id
cmrologit ranking school_va distance sports_rank school_needs, reverse //need to add cluster later 
restore

	
	

	
	
	
	
	
	
	
	
	
	
