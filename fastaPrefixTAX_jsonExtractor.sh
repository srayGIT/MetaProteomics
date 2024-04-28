#!/bin/bash

# Extract the 'faa' sequence files from ncbi zipped files and parsing the json file
# To be used for Northeastern Discovery Linux HPC 
output_dir="./PreFixTAX_GCF_FAAs"
mkdir -p "$output_dir"

# Append json info to info. file
parsed_info_file="PreFixTAX_GCF_unzip_ParsedInfo.txt"
> "$parsed_info_file"  # Clear the file content if it already exists

# Process the json file
process_json() {
    local json_file=$1
    local taxid=$2
    local temp_dir=$3

    jq -c '.assemblies[] | select(.files[]?.fileType == "PROTEIN_FASTA")' "$json_file" | while read -r assembly; do
        gca_info=$(echo "$assembly" | jq -r '.accession')
        gca_dir="$temp_dir/ncbi_dataset/data/$gca_info"
        
        if [[ -d "$gca_dir" ]]; then
            protein_file_path="$gca_dir/protein.faa"

            if [[ -f "$protein_file_path" ]]; then
                new_file_name="protein_${taxid}_${gca_info}.faa"
                new_file_path="$output_dir/$new_file_name"

                # Process each line in the protein file
                while IFS= read -r line; do
                    if [[ $line == '>'* ]]; then
                        # Prepend the taxid to the header line
                        echo ">TAX${taxid}_${line:1}" >> "$new_file_path"
                    else
                        echo "$line" >> "$new_file_path"
                    fi
                done < "$protein_file_path"

                echo "$taxid, $gca_info, File Found, $new_file_name" >> "$parsed_info_file"
            else
                echo "$taxid, $gca_info, Protein File Not Found" >> "$parsed_info_file"
            fi
        else
            echo "$taxid, $gca_info, GCA Directory Not Found" >> "$parsed_info_file"
        fi
    done
}

# Process each zip file
for zip_file in *.zip; do
    echo "Processing $zip_file..."

    # file name -> taxid
    taxid=$(basename "$zip_file" .zip | sed 's/taxid_//')

    
    temp_dir=$(mktemp -d)

    
    unzip -q "$zip_file" -d "$temp_dir"

    # Process the JSON file if it exists
    json_file="$temp_dir/ncbi_dataset/data/dataset_catalog.json"
    if [[ -f "$json_file" ]]; then
        process_json "$json_file" "$taxid" "$temp_dir"
    else
        echo "$taxid, , JSON File Not Found" >> "$parsed_info_file"
    fi

    
    rm -rf "$temp_dir"
done

echo "Renaming and extraction done. Information appended to $parsed_info_file."