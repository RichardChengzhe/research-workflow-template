* ==============================================================================
* 00_run.do -- Master do-file
* Sets globals, runs all pipeline steps
*
* Project: [YOUR PROJECT NAME]
* ==============================================================================

clear all
set more off
set maxvar 32767

* --- Detect user and set project root ---
* CUSTOMIZE: Add each collaborator's path
* if "`c(username)'" == "yourusername" {
*     global root "C:/Users/you/Dropbox/Project"
* }
* if "`c(username)'" == "coauthor" {
*     global root "/Users/coauthor/Dropbox/Project"
* }

* --- Verify correct folder ---
capture confirm file "$root/pipeline.md"
if _rc != 0 {
    display as error "Cannot find pipeline.md -- wrong folder? Check root global."
    exit 601
}

* --- Define globals ---
global data      "$root/data"
global raw       "$root/data/raw"
global processed "$root/data/processed"
global code      "$root/code"
global stata     "$root/code/stata"
global python    "$root/code/python"
global programs  "$root/code/programs"
global output    "$root/output"
global figures   "$root/output/figures"
global tables    "$root/output/tables"
global results   "$root/output/results"
global logs      "$root/output/logs"
global manuscript "$root/manuscript"

* --- Load parameters ---
do "$stata/params.do"

* --- Run pipeline steps ---
* Uncomment as you build:
* do "$stata/01_import.do"
* do "$stata/05_merge.do"
* do "$stata/10_summary_stats.do"
* do "$stata/20_estimation.do"
* do "$stata/25_robustness.do"
