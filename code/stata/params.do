* ==============================================================================
* params.do -- Critical research parameters
* All values here must match the pipeline documentation
* Sourced by 00_run.do -- do not run independently
*
* BREAK THE GLASS: Changing values here affects ALL downstream analysis.
* Warn the user before modifying.
* ==============================================================================

* --- Sample Restrictions ---
* global sample_start_year = 2010
* global sample_end_year   = 2024

* --- Treatment Definition ---
* global treatment_var "treatment_indicator"
* global treat_date = "2020-01-01"

* --- Outcome Definitions ---
* global outcome_var "main_outcome"
* global alt_outcomes "outcome2 outcome3"

* --- Control Variables ---
* global controls "control1 control2 control3"

* --- Estimation Parameters ---
* global cluster_var "cluster_id"
* global fe_vars "unit_fe time_fe"
* global event_window = 5

* --- Random Seed ---
* global seed = 12345
