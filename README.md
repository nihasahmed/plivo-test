### API urls
**To get all messages under an account**: method:`get` url:`<deployment-server-url>/get/messages/<account_id>`
**To create messages under an account**:  method:`post` url:`<deployment-server-url>/create` with data 
```json
{
	"account_id": "id of account",
	"sender_number": "number of sender",
	"receiver_number": "number of receiver"
}
```
**To search messages under an account**:  method:`get` url:`<deployment-server-url>/search?` along with following query parameters which can be also used in combinations for adding and conditions to query 
- **message_id**: takes multiple values seperated comma and enclosed by quotes eg:  `?message_id='123-xyz,437-abc'`
- **sender_number**: takes multiple values seperated comma and enclosed by quotes eg:  `?sender_number='1235678,987654'`
- **receiver_number**: takes multiple values seperated comma and enclosed by quotes eg:  `?receiver_number='1235678,987654'`
- **account_id**:  takes a single value. If multiple values are given in comma like above it will be considered as one single value with comma in it. eg `?account_id=20`
- Values can be send as combinations also. Eg: to search message with sender_number in (1235678,987654) under the accound_id 20 use query string like this  `?sender_number='1235678,987654'&account_id='20'`

### Instructions to deploy message service API locally 

**Prerequisites** - Should have Docker, Python3, PIP installed 
**Steps to deploy** -  Run `docker-compose up ` from root of repo
**How to Access** -  Open browser and go to [localhost:5001](localhost:5001 "localhost:5001")

### Instructions to deploy message service API inside a new AKS cluster

**Prerequisites**  Should have Terraform, Azure CLI, Docker, Kubernetes, Python3, PIP installed
**Steps to deploy** 
- `az login`: login to azure-cli if not logged in already
- cd into the terraform folder `cd terraform`
	 - Change values in terraform.tfvars file as suitable
	 - `terraform init` initialises terraform project and download dependencies
	 - `terraform apply` shows resources that will be created, type yes and press enter to proceed with creating resource in azure
	 - take note of output values which will be used while building the docker image
	 - Use kubeconfig file generated as output to access new cluster `mv kubeconfig ~/.kube/config `
	 - run `kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.3.0/deploy/static/provider/cloud/deploy.yaml ` to set up ingress controller in newly created AKS
- cd into root of repo and run `docker build -t <value of acr_login_server output from terraform apply>/message-service:v1` to build and tag app image in correct format
- run `az acr login --name plivotestrepo` to login to ACR using azure-cli 
- run `docker push <value of acr_login_server output from terraform apply>/message-service:v1` to push the image build to ACR
- cd into k8s folder and apply the file in following order
	- kubectl apply -f mysql-statefulset.yaml 
	- kubectl apply -f mysql-service.yaml 
	- kubectl apply -f app-deployment.yaml 
	- kubectl apply -f app-service.yaml 
	- kubectl apply -f app-ingress.yaml 
	- kubectl apply -f app-pdb.yaml 
	- kubectl apply -f app-hpa.yaml 
- Verify the deployments by `kubectl get all`
- run `kubectl get ingress` to get the external public IP for using in browser as API server address.  `ADDRESS` field shows the IP's value which can be taken from azure console or cli as the clusters external IP. The IP can be mapped with a domain or application load balancer in front.



### Contents

-  **app/ **: Contains main source code of the message service API
-  **k8s/ **: Contains kubernetes manifest files required to deploy resources in the kubernetes cluster
- **mysql/ **: Contains a dummy Dockerfile that docker-compose will use while deploying locally (This is not required, will be deleted!)
- **terraform/** : Contains terraform IAC files required for creating resources required to setup a kubernetes cluster(AKS) and a docker-registry for pushing and pulling images
- **tests/** : Contain a python file with some unit tests to rest route functions 
- **.gitignore** : files and folders to ignore
- **docker-compose** : docker-compose file to run build and run both a mysql db and the message api server which consume it. Used for local testing
- **Jenkinsfile** : Jenkins declarative pipeline script to master code from git, run unit tests and if tests pass an image will be build and also the same will get deployed to the kubernetes cluster
- **requirements-pytest.txt** - file listing dependencies required for unit testing in jenkins
- **requirements.txt** - r - file listing dependencies required for running the message service API



