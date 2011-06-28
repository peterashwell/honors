from run_test import lcExperiment
lce = lcExperiment()
lce.parse_options()
lce.preliminary()
lce.do_experiment()
lce.print_cm()
lce.finish()
