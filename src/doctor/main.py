import sys
import os
import warnings
from datetime import datetime
from doctor.crew import Diagnosis

# Suppress syntax warnings from pysbd
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the diagnostic workflow with all tools integrated.
    
    The patient name and condition will be extracted from the patient history file
    using the FileReadTool rather than being provided as inputs.
    """
    # Ensure output directory exists
    os.makedirs("outputs", exist_ok=True)
    
    # Set up minimal inputs - only the current year
    # Patient details will be extracted from files using FileReadTool
    inputs = {
        'current_year': str(datetime.now().year)
    }
    
    try:
        # Initialize and run the diagnostic workflow
        Diagnosis().crew().kickoff(inputs=inputs)
        print("Comprehensive diagnostic workflow completed")
        print("Output files have been saved to the outputs directory")
    except Exception as e:
        raise Exception(f"An error occurred while running the diagnostic workflow: {e}")

if __name__ == "__main__":
    run()