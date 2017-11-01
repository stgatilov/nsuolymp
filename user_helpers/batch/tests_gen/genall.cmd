compile  -q  --all
call geninputs
validate -q  --validator --samples --indices 
testsol  -q  --gen-output --tl=0 --ml=0  sol_sg_ok   --tests 3-99
