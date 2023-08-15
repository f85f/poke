#!/bin/bash

echo "Enter keyword:"
read keyword

# Download data
shodan download --limit -1 "$keyword" "$keyword"
if [ $? -ne 0 ]; then
    echo "Error downloading data"
    exit 1
fi

# Extract data
gunzip "${keyword}.json.gz"
if [ $? -ne 0 ]; then
    echo "Error extracting data"
    exit 1
fi

# Parse and save IP addresses
shodan parse "${keyword}.json" --fields ip_str > "${keyword}_ips.txt"
if [ $? -ne 0 ]; then
    echo "Error parsing data"
    exit 1
fi

# Call the Python script to process IP addresses and store banners, passing the filename
python3 key.py "${keyword}_ips.txt"

# Clean up
rm "${keyword}.json"

echo "IP addresses extracted and saved as ${keyword}_ips.txt"
