import os
import zipfile
import tempfile
import json
from concurrent.futures import ThreadPoolExecutor
"""
Created on Thu Nov  2 16:21:40 2023
@author: Somak Ray
Extracts sequences (if present by parsing the enclosed json file) in the NCBI taxid zipped files.
Adds TaxId at the begining of the fasta header.Required for SIP processing
Fast operation because of using multicore in Win11/ Win10
"""
def process_json(json_file, taxid, temp_dir, output_dir, parsed_info_file):
    with open(json_file) as file:
        data = json.load(file)
        for assembly in data['assemblies']:
            if any(f['fileType'] == 'PROTEIN_FASTA' for f in assembly.get('files', [])):
                gca_info = assembly['accession']
                gca_dir = os.path.join(temp_dir, 'ncbi_dataset', 'data', gca_info)

                if os.path.isdir(gca_dir):
                    protein_file_path = os.path.join(gca_dir, 'protein.faa')

                    if os.path.isfile(protein_file_path):
                        new_file_name = f"protein_{taxid}_{gca_info}.faa"
                        new_file_path = os.path.join(output_dir, new_file_name)

                        with open(protein_file_path) as pf, open(new_file_path, 'w') as nf:
                            for line in pf:
                                if line.startswith('>'):
                                    nf.write(f">TAX_{taxid}_{line[1:]}")
                                else:
                                    nf.write(line)

                        with open(parsed_info_file, 'a') as log_file:
                            log_file.write(f"{taxid}, {gca_info}, File Found, {new_file_name}\n")
                    else:
                        with open(parsed_info_file, 'a') as log_file:
                            log_file.write(f"{taxid}, {gca_info}, Protein File Not Found\n")
                else:
                    with open(parsed_info_file, 'a') as log_file:
                        log_file.write(f"{taxid}, {gca_info}, GCA Directory Not Found\n")

def process_zip_file(zip_file, output_dir, parsed_info_file):
    taxid = zip_file.split('.')[0].replace('taxid_', '')
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        json_file = os.path.join(temp_dir, 'ncbi_dataset', 'data', 'dataset_catalog.json')
        if os.path.isfile(json_file):
            process_json(json_file, taxid, temp_dir, output_dir, parsed_info_file)
        else:
            with open(parsed_info_file, 'a') as log_file:
                log_file.write(f"{taxid}, , JSON File Not Found\n")

def main():
    output_dir = "./C12_GCF_FAAProteins"
    os.makedirs(output_dir, exist_ok=True)

    parsed_info_file = "ZipSeq_C12GCF_ParsedInfo.txt"
    with open(parsed_info_file, 'w') as f:
        pass  # Clear the file content

    zip_files = [f for f in os.listdir('.') if f.endswith('.zip')]

    # This uses ThreadPoolExecutor to process zip files in parallel
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        for zip_file in zip_files:
            executor.submit(process_zip_file, zip_file, output_dir, parsed_info_file)

if __name__ == "__main__":
    main()
