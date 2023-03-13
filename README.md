# poke

##A quick script to run shodan for specific port and keyword settings

##add this line crontab with the command 'crontab -e' in your terminal

0 2 */3 * * cd /path/to/script && bash script.sh <<< "80\napache"

##Replace "/path/to/script" with the actual path to your script file. The <<< operator passes the string "80\napache" as input to the script. Update accordingly.
