import subprocess
import os
from datetime import datetime

SOLVER_PATH = "/home/jana/Documents/DIPLOMA/SOLVERJI/GLASGOW/glasgow-subgraph-solver/build/glasgow_subgraph_solver"  
TEST_DIR = "/home/jana/Documents/DIPLOMA/SOLVERJI/GLASGOW/glasgow-subgraph-solver/test-instances" 
OUTPUT_DIR = "./results/"  
SUMMARY_FILE = os.path.join(OUTPUT_DIR, "summary_results.txt")  


def run_test(original, subgraph):
    command = [
        SOLVER_PATH,
        "--format", "lad",
        os.path.join(TEST_DIR, subgraph),
        os.path.join(TEST_DIR, original)
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    
    is_isomorphic = "status = true" in result.stdout
    iso_result = 1 if is_isomorphic else 0

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"{OUTPUT_DIR}result_{original}_{subgraph}_{timestamp}.txt"
    
    with open(output_file, "w") as file:
        file.write(result.stdout)

    print(f"Test completed for {original} with {subgraph}. Results saved to {output_file}")
    
    return iso_result

def generate_summary(results):
    with open(SUMMARY_FILE, "w") as file:
        # Header
        file.write("Original Graph\tSubgraph_10\tSubgraph_20\tSubgraph_60\n")
        
        # Rows for each graph
        for original, result in results.items():
            row = f"{original}\t{result.get('_subgraph_10', 'NA')}\t{result.get('_subgraph_20', 'NA')}\t{result.get('_subgraph_60', 'NA')}\n"
            file.write(row)
    print(f"Summary file generated at {SUMMARY_FILE}")

# Run all tests
def run_all_tests():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # List all files in the test directory
    all_files = sorted(os.listdir(TEST_DIR))
    
    # Separate original graphs and subgraphs by filename pattern
    original_graphs = [f for f in all_files if f.endswith("original_graph")]
    subgraph_files = {f.split('_')[0]: [] for f in original_graphs}
    
    # Populate the subgraph files dictionary
    for f in all_files:
        base_id = f.split('_')[0]
        if base_id in subgraph_files:
            if "_subgraph_10" in f or "_subgraph_20" in f or "_subgraph_60" in f:
                subgraph_files[base_id].append(f)

    summary_results = {}
    
    # Run each original graph and its subgraphs
    for original in original_graphs:
        base_id = original.split('_')[0]
        summary_results[base_id] = {}

        # Specific subgraphs
        subgraph_10 = next((f for f in subgraph_files[base_id] if f.endswith("_subgraph_10")), None)
        subgraph_20 = next((f for f in subgraph_files[base_id] if f.endswith("_subgraph_20")), None)
        subgraph_60 = next((f for f in subgraph_files[base_id] if f.endswith("_subgraph_60")), None)
        
        # Run tests for each subgraph found
        for subgraph in [subgraph_10, subgraph_20, subgraph_60]:
            if subgraph:
                result = run_test(original, subgraph)
                summary_results[base_id][subgraph[-12:]] = result
            else:
                print(f"Warning: Subgraph {subgraph} for {original} not found.")
                summary_results[base_id][subgraph[-12:] if subgraph else 'Unknown'] = "NA"

    generate_summary(summary_results)

if __name__ == "__main__":
    run_all_tests()
