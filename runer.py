# TO DO
""""
Script that first copy and paste all test into correct folders:

Glasgow: 
mapo prilepi tukaj noter:
/home/jana/Documents/DIPLOMA/SOLVERJI/GLASGOW/glasgow-subgraph-solver/test-instances

LAD:
mapo prilepi tukaj noter:
/home/jana/Documents/DIPLOMA/SOLVERJI/LAD/pathLAD

RI:
mapo prilepi tukej noter:
/home/jana/Documents/DIPLOMA/SOLVERJI/RI/RI

VF3:
mapo prlepi tukej noter:
/home/jana/Documents/DIPLOMA/SOLVERJI/VF3/vf3lib/test

SICS:
--nisem še--

Then it needs to run solvers but not all at the same time first the glasgow, lad, ri, vf3, sics and mby i need different scripts for all these solvers?
Wait for them to run to find first solution, and write time for finding first solution.

Lines for how to run (še vedno nevem če rabm še tu makeat al ne i guess da ne)

Glasgow: 
odpri terminal tukaj:
/home/jana/Documents/DIPLOMA/SOLVERJI/GLASGOW/glasgow-subgraph-solver
napiši ta line:
./build/glasgow_subgraph_solver --induced --format lad ./test-instances/test_instances_scale_free_lad/1_subgraph_60 ./test-instances/test_instances_scale_free_lad/1_original_graph

LAD:
odpri teminal tukaj:
/home/jana/Documents/DIPLOMA/SOLVERJI/LAD/pathLAD
napiši ta line:
./main -i -p ./test_instances_scale_free_lad/1_subgraph_60 -t ./test_instances_scale_free_lad/1_original_graph

RI:
odpri terminal tukej:
/home/jana/Documents/DIPLOMA/SOLVERJI/RI/RI
napiši ta line:
./ri36 ind gfu ./test_instances_scale_free_ri/2_original_graph.gfu ./test_instances_scale_free_ri/2_subgraph_60.gfu

VF3 (rabi ful cajta al nevem kaj se dogaja):
odpri terminal tukej:
/home/jana/Documents/DIPLOMA/SOLVERJI/VF3/vf3lib
napiši ta line:
./bin/vf3 -u ./test/test_instances_scale_free_vf3/1graph60.sub.grf ./test/test_instances_scale_free_vf3/1graph.grf

SICS:
--nesm še--

"""