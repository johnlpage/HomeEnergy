raspistill -hf -vf -o out.jpg
convert out.jpg -crop 400x200+1200+300 -negate -gaussian-blur 20 -threshold 70% new.jpg 
tesseract  new.jpg badtext  -c tessedit_char_whitelist=0123456789 --psm 13
export READING=$(head -1 badtext.txt | tr 'QOEBTS,' '008875 ' | sed 's/^0*//g'| sed 's/ //g')
echo $READING
export APIKEY="XXXXXXXXX"
curl --location --request POST 'https://data.mongodb-api.com/app/data-amzuu/endpoint/data/beta/action/insertOne' \
--header 'Content-Type: application/json' \
--header 'Access-Control-Request-Headers: *' \
--header "api-key: $APIKEY" \
--data-raw "{
    \"collection\":\"meter\",
    \"database\":\"energy\",
    \"dataSource\":\"Cluster0\",
    \"document\": {\"reading\": ${READING}  }
}"
