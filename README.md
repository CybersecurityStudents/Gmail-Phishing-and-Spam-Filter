# Gmail-Phishing-and-Spam-Filter

# Docker Build and run 

 > docker build -t gmailphishingandspamfilter .

 > docker run -it --name gmailbot --rm --volume $(pwd):/usr/src/app --net=host gmailphishingandspamfilter:latest sh

## Initial test
Python script that works together with Gmail API to filter out any phishing/spam emails and report them to Google.