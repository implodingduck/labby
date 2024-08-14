#!/bin/bash
source .env

packageName=$(cat manifest.json.template | jq -r '.packageName')
shortName=$(cat manifest.json.template | jq -r '.name.short')
teams_app_id=$(uuidgen -m -N $packageName.$shortName -n @url)
echo $teams_app_id

cat manifest.json.template | sed -e "s/\${{TEAMS_APP_ID}}/$teams_app_id/g" -e "s/\${{BOT_ID}}/$BOT_ID/g" -e "s/\${{BOT_DOMAIN}}/$BOT_DOMAIN/g" > manifest.json