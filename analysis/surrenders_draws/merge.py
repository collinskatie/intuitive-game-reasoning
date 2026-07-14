import pickle
import numpy as np
import glob
import os

def aggregate_pickles_to_lists(pickle_dir, output_file):
    """
    Process multiple pickle files with a specific format and create a new pickle file 
    with the same format, but with the target keys containing transposed lists where
    each index position contains all values from that position across files.
    
    Args:
        pickle_dir (str): Directory containing the pickle files to process
        output_file (str): File path to save the results
    
    Returns:
        dict: The complete data structure with transposed lists for the specified keys
    """
    # Keys to extract and aggregate into lists
    target_keys = [
        'p1_pwin_heuristics',
        'p1_plose_heuristics',
        'game_length_heuristics',
        'game_length_hs',
        'p1_pwin_hs',
        'p1_plose_hs'
    ]
    
    # Get all pickle files in the directory
    pickle_files = glob.glob(os.path.join(pickle_dir, "*.pkl"))
    
    if not pickle_files:
        raise ValueError(f"No pickle files found in {pickle_dir}")
    
    print(f"Found {len(pickle_files)} pickle files to process.")
    
    # Initialize a template data structure from the first file
    with open(pickle_files[0], 'rb') as f:
        template_data = pickle.load(f)
    
    # Initialize dictionary to store values from each file
    all_values = {}
    for key in target_keys:
        if key in template_data:
            # Create a list of lists: one list for each position in the array
            array_length = len(template_data[key])
            all_values[key] = [[] for _ in range(array_length)]
        else:
            print(f"Warning: Key '{key}' not found in the first pickle file")
            all_values[key] = None
    
    # Process each pickle file
    files_processed = 0
    for file_path in pickle_files:
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            # Process each target key
            for key in target_keys:
                if key in data and all_values[key] is not None:
                    # Check if array has the expected length
                    if len(data[key]) == len(all_values[key]):
                        # Add each value to its corresponding position list
                        for i, value in enumerate(data[key]):
                            all_values[key][i].append(value)
                    else:
                        print(f"Warning: Array length mismatch in {file_path} for key {key}. Expected {len(all_values[key])}, got {len(data[key])}. Skipping this key for this file.")
                elif all_values[key] is not None:
                    print(f"Warning: Key {key} not found in {file_path}. Skipping this key for this file.")
            
            files_processed += 1
                
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}. Skipping this file.")
    
    # Check if we processed any files successfully
    if files_processed == 0:
        raise ValueError("No valid data was processed from any pickle file.")
    
    # Update the template_data with transposed aggregated lists
    for key in target_keys:
        if all_values[key] is not None:
            template_data[key] = all_values[key]
            print(f"Aggregated '{key}' with {len(all_values[key])} positions, each containing up to {files_processed} values")
        else:
            print(f"Warning: Could not aggregate '{key}' as it was not found in the template")
    
    # Save the updated template data to the output file
    with open(output_file, 'wb') as f:
        pickle.dump(template_data, f)
    
    print(f"Results saved to {output_file}")
    
    return template_data

# Example usage:
if __name__ == "__main__":
    # Replace with your actual directory containing pickle files
    pickle_directory = "/orcd/data/jbt/001/barba/intuitive-game-theory/analysis/surrenders_draws/draws_heuristics_depth"
    
    # Specify output file path
    output_path = "analysis/surrenders_draws/draws_heuristic_search_eg_merged.pkl"
    
    try:
        results = aggregate_pickles_to_lists(pickle_directory, output_path)
        
        # Print some statistics about the results
        for key in ['p1_pwin_heuristics', 'p1_plose_heuristics', 'p1_pwin_hs', 'p1_plose_hs', 'game_length_heuristics', 'game_length_hs']:
            if key in results:
                print(f"{key}: Contains {len(results[key])} positions")
                # Check the first few positions to understand structure
                for i in range(min(3, len(results[key]))):
                    print(f"  Position {i}: {len(results[key][i])} values, e.g., {results[key][i][:3]}...")
    
    except Exception as e:
        print(f"Error: {str(e)}")