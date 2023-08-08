#!/bin/bash

echo "Provider (aws, gcp, azure):"
read provider
echo "Port:"
read port

output_file="${provider}${port}"

batch_size=100  # Adjust the batch size as needed

# Read IP address ranges from the file
mapfile -t ip_ranges < "${provider}blocks"

# Loop through IP ranges in batches
for (( i = 0; i < ${#ip_ranges[@]}; i += batch_size )); do
    batch=("${ip_ranges[@]:i:batch_size}")
    ip_range_batch=$(IFS=, ; echo "${batch[*]}")
    
    sudo masscan -p"${port}" --rate 10000 "$ip_range_batch" | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' >> "$output_file"
done

echo "Scanning completed."
