rem simple max test 2:
gen_chain 100000 1                      >tests/15.in

rem random tests (for correctness check)
gen_random 10 20 0                      >tests/16.in 
gen_random 9 20 1                       >tests/17.in 
gen_random 11 11 0                      >tests/18.in 
gen_random 12 100 0                     >tests/19.in 
gen_random 11 100 1                     >tests/20.in 
gen_random 9 100 2                      >tests/21.in 
gen_random 1000 5000 0                  >tests/22.in
gen_random 1000 5000 1                  >tests/23.in
gen_random 1000 1000 0                  >tests/24.in
gen_random 1000 800 0                   >tests/25.in
gen_cactus 5000 10000 4000 0.1 0        >tests/26.in 
gen_cactus 5000 10000 4000 0.1 1        >tests/27.in 


rem max tests:
gen_chain 100000 4                      >tests/28.in 
gen_chain 100000 30000                  >tests/29.in 

rem cactuses with long cycle (con / incon):
gen_cactus 99999 100000 50000 0.001 0   >tests/30.in 
gen_cactus 99999 100000 50000 0.001 1   >tests/31.in 

rem cycle (con / incon):
gen_cactus 99999 100000 100000 -1 0     >tests/32.in 
gen_cactus 99999 100000 100000 -1 2     >tests/33.in 

rem cactuses with random edges added on top (con / incon):
gen_cactus 98371 100000 50000 0.001 0   >tests/33.in 
gen_cactus 89999 100000 50000 0.001 1   >tests/34.in 

rem various stars (one element connected with many others):
gen_star 50000 100000 1 0               >tests/35.in 
gen_star 90000 100000 0 0               >tests/36.in 
gen_star 99990 100000 1 0               >tests/37.in 
gen_star 99990 100000 1 2               >tests/38.in 
gen_star 99997 100000 0 2               >tests/39.in 
