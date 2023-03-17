#!/bin/bash

# Create output directory with current date and time
output_dir="$(date +%Y-%m-%d-%H-%M)"
mkdir -p "$output_dir"

# Define dependencies and their installation commands
api=qiGpviWq57sMw56zXhu9mmnik4QcI14u
dependencies=("shodan:shodan" "jq:jq")
install_commands=("pip3 install shodan" "shodan init $api" "sudo apt-get install jq")

# Install dependencies if they are not already installed
for i in "${!dependencies[@]}"
do
    IFS=':' read -ra dep <<< "${dependencies[$i]}"
    if ! command -v "${dep[0]}" &> /dev/null
    then
        ${install_commands[$i]} > /dev/null 2>&1
    fi
done

echo "Port:"
read  port
echo "Keywords:"
read  keywords

# Use the inputs

if [ -n "$port" ] && [ -n "$keywords" ]
then
    shodan count "$keywords" port:"$port";
    shodan download --limit -1 "$keywords" "'$keywords' port:$port";
    gunzip -c "$keywords.json.gz" > "$output_dir/$keywords.json";
    jq . "$output_dir/$keywords.json" | grep ip_str | cut -d '"' -f 4 > "$output_dir/node-ips";
    sort "$output_dir/node-ips"
    jq . "$output_dir/$keywords.json" | grep data | cut -d '"' -f 4 > "$output_dir/peerdata";

    if [ -s "$output_dir/peerdata" ]; then
        grep -ro -E "([0-9]{1,3}\.){3}[0-9]{1,3}" "$output_dir/peerdata" > "$output_dir/peer-ips";
        sort "$output_dir/peer-ips"
        rm "$output_dir/peerdata"

        for ip in $(cat "$output_dir/peer-ips"); do
            curl "http://ip-api.com/json/$ip" >> "$output_dir/peers-geo.json"
            sleep 1.5
        done

        peers_output_file="peers.csv"
        echo "ip,country,latitude,longitude,isp" > "$output_dir/$peers_output_file"
        jq -r '. | [.query,.country,.lat,.lon,.isp] | @csv' "$output_dir/peers-geo.json" >> "$output_dir/$peers_output_file"
    fi

    for ip in $(cat "$output_dir/node-ips"); do
        curl "http://ip-api.com/json/$ip" >> "$output_dir/nodes-geo.json"
        sleep 1.5
    done

    nodes_output_file="nodes.csv"
    echo "ip,country,latitude,longitude,isp" > "$output_dir/$nodes_output_file"
    jq -r '. | [.query,.country,.lat,.lon,.isp] | @csv' "$output_dir/nodes-geo.json" >> "$output_dir/$nodes_output_file"

    # Call the Python script for visualization
    python3 map.py "$output_dir"
fi
