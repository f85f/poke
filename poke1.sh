#!/bin/bash

# Create output directory with current date and time
output_dir="$(date +%Y-%m-%d-%H-%M)"
mkdir -p "$output_dir"

# Define dependencies and their installation commands
api=<your shodan API>
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
    sort "$output_dir/node-ips" > "$output_dir/nodes"
    jq . "$output_dir/$keywords.json" | grep data | cut -d '"' -f 4 > "$output_dir/peerdata";
    grep -ro -E "([0-9]{1,3}\.){3}[0-9]{1,3}" "$output_dir/peerdata" > "$output_dir/peer-ips";
    rm "$output_dir/peerdata"
    sort "$output_dir/peer-ips" > "$output_dir/peers"
    rm "$output_dir/node-ips" "$output_dir/peer-ips"

    # Call the geo-location script with rate limit of 42 requests per minute
    for ip in $(cat "$output_dir/nodes"); do
        curl "http://ip-api.com/json/$ip" >> "$output_dir/nodes-geo"
        sleep 1.5
    done
    for ip in $(cat "$output_dir/peers"); do
        curl "http://ip-api.com/json/$ip" >> "$output_dir/peers-geo"
        sleep 1.5
    done
fi

