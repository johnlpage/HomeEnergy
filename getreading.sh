#!/bin/bash

libcamera-still -n -v 0 --hflip --vflip -o out.jpg

convert out.jpg -crop 600x200+170+600 -negate -gaussian-blur 20 -threshold 70% -rotate 10 -shear -15x0 -resize 25% new.jpg
tesseract  new.jpg new --psm 7  -l ssd --dpi 70

export READING=$(head -1 new.txt | sed 's/^0*//g' )
echo $READING
export TYPE="gas"
[ $(echo "$READING > 26000" |bc -l) -eq 1 ] && export TYPE="electric"
echo $TYPE

export APIKEY="XXXXXXXXXXXXXXXX-XXXXXXXX"
export EPOCHMILLIS=$(date +%s000)

 curl --location --request POST 'https://data.mongodb-api.com/app/data-amzuu/endpoint/data/beta/action/insertOne' \
--header 'Content-Type: application/json' \
--header 'Access-Control-Request-Headers: *' \
--header "api-key: $APIKEY" \
--data-raw "{
    \"collection\":\"meter\",
    \"database\":\"energy\",
    \"dataSource\":\"Cluster0\",
    \"document\": {\"type\": \"${TYPE}\",\"reading\": ${READING},\"date\" : { \"\$date\" : { \"\$numberLong\" : \"${EPOCHMILLIS}\" }}  }
}"

gpio -g mode 18 pwm
gpio pwm-ms
gpio pwmc 192
gpio pwmr 2000
gpio -g pwm 18 100
sleep 0.5
gpio -g pwm 18 200
sleep 0.5
gpio -g pwm 18 100

libcamera-still -n -v 0 --hflip --vflip -o out2.jpg

convert out2.jpg -crop 600x200+170+600 -negate -gaussian-blur 20 -threshold 70% -rotate 10 -shear -15x0 -resize 25% new2.jpg
tesseract  new2.jpg new2 --psm 7  -l ssd --dpi 70
export READING=$(head -1 new2.txt | sed 's/^0*//g' )
echo $READING

export TYPE="gas"
[ $(echo "$READING > 26000" |bc -l) -eq 1 ] && export TYPE="electric"
echo $TYPE

export EPOCHMILLIS=$(date +%s000)

 curl --location --request POST 'https://data.mongodb-api.com/app/data-amzuu/endpoint/data/beta/action/insertOne' \
--header 'Content-Type: application/json' \
--header 'Access-Control-Request-Headers: *' \
--header "api-key: $APIKEY" \
--data-raw "{
    \"collection\":\"meter\",
    \"database\":\"energy\",
    \"dataSource\":\"Cluster0\",
    \"document\": {\"type\": \"${TYPE}\", \"reading\": ${READING},\"date\" : { \"\$date\" : { \"\$numberLong\" : \"${EPOCHMILLIS}\" }}  }
}"
