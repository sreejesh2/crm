sudo docker build -t crm .

sudo docker tag crm:latest 727516060995.dkr.ecr.us-east-1.amazonaws.com/crm:latest

service docker stop
rm ~/.docker/config.json
service docker start

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 727516060995.dkr.ecr.us-east-1.amazonaws.com
docker push 727516060995.dkr.ecr.us-east-1.amazonaws.com/crm:latest
