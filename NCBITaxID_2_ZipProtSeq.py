# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 15:47:48 2023

@author: Somak Ray
"""

import subprocess
import pandas as pd
import argparse
           
def download_proteins(taxid_list, log_file):
    """
    Downloads protein data for a list of taxonomic IDs from NCBI.
    
    Parameters:
    taxid_list (list of int): List of taxonomic IDs for which to download data.
    log_file (str): Path to the log file for recording download activities.
    
    Each taxonomic ID is processed, and any errors encountered are logged.
    """
    with open(log_file, 'w') as log:
        for taxid in taxid_list:
            try:
                command = f"datasets download genome taxon {taxid} --include protein --filename taxid_{taxid}.zip"
                print(f"Running command: {command}")
                subprocess.run(command, check=True, shell=True)
            except subprocess.CalledProcessError as e:
                error_msg = f"Error occurred with taxid {taxid}: {e}\n"
                print("\n" + error_msg)
                log.write(error_msg)
def main():
    """Download protein sequences for selected tax IDs."""
    parser = argparse.ArgumentParser(description="Download protein sequences from NCBI using taxonomic IDs.")
    parser.add_argument('input_file', type=str, help='The path to the input Excel file containing taxonomic IDs.')
    args = parser.parse_args()
    df = pd.read_excel(args.input_file)
    select_df = df[df['taxid'].notna()]
    select_df = select_df[~select_df['code'].str.contains('\+', na=False)]
    taxid_list = [int(x) for x in select_df["taxid"].tolist()]
    #taxid_list = taxid_list[:10] 
    log_report = "NCBI_RetrieveError_log.txt"
    download_proteins(taxid_list, log_report)

if __name__ == "__main__":
    main()


