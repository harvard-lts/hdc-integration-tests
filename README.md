# docker-flask-template
This project will create a generic, Dockerized, Flask application ready for action!

This example shows two different use-cases for the Flask Application. An API and an HTML site. If you want just an HTML site, you can remove the API functionality by [deleting these lines in `app/resources.py`](app/resources.py#L9-L17).

After following the setup instructions and starting your Docker container, you should have a running Flask application with two routes:

* An API description that displays here: https://localhost:3001/
* An API endpoint that displays the version here: https://localhost:3001/version
* A "Hello, World" HTML page here: https://localhost:3001/hello-world
* A Health Check page here: https://localhost:3001/healthcheck


## Technology Stack
##### Language
Python

##### Framework
Flask

##### Development Operations
Docker Compose

## Local Development Environment Setup Instructions

### 1: Clone the repository to a local directory
```git clone git@github.com:harvard-lts/docker-flask-template.git```

### 2: Copy the cloned files into your own new project repository

After cloning your brand-new project repository, you can copy the files from this repository into it.

### 3: Create app config

##### Create config file for environment variables
- Make a copy of the config example file `./env-example.txt`
- Rename the file to `.env`
- Replace placeholder values as necessary

*Note: The config file .env is specifically excluded in .gitignore and .dockerignore, since it contains credentials it should NOT ever be committed to any repository.*

##### Create webapp.conf file for environment variables
- Make a copy of the config example file `./`
- Rename the file to `webapp.conf`
- Replace placeholder values as necessary (anything localhost will be changed in a deployed environment)

*Note: The config file webapp.conf is specifically excluded in .gitignore and .dockerignore, since it can contain credentials it should NOT ever be committed to any repository.*

### 4: Change container and network names in `docker-compose-local.yml`
- change container name on [lines 8-9](/docker-compose-local.yml#L8-L9)
- change network name on [line 21](/docker-compose-local.yml#L21)
- change network name on [lines 26-27](/docker-compose-local.yml#L26-L27)

### 5: Change image names in `docker-compose.yml`
- change image name on [lines 10-11](/docker-compose.yml#L10-L11)

### 6: Change log file names in `supervisord.conf`
- change log file name on [line 3](/supervisord.conf#L3)
- change log file name on [lines 14-15](/supervisord.conf#L14-L15)

### 7: Change titles and descriptions in `app/resources.py`
- change title and description on [lines 9-10](/app/resources.py#L9-L10)

### 7: Change uid and gid in `DockerfilePub`
- change uid and gid on [line 26](/DockerfilePub#L26)

### 8: Start

##### START

This command builds all images and runs all containers specified in the docker-compose-local.yml configuration.

```
docker-compose -f docker-compose-local.yml up --build --force-recreate
```

### 9: Install Packages (optional)
This step is only required if additional python packages must be installed during development. Update the requirements.txt inside the container to install new python packages.

##### Run docker exec to execute a shell in the container by name

Open a shell using the exec command to access the hgl-downloader container.

```
docker exec -it docker-flask-template bash
```

##### Install a new pip package

Once inside the mps-asset-validation container, run the pip install command to install a new package and update the requirements text file.

```
pip install packagename && pip freeze > requirements.txt
```

### 10: Stop

##### STOP AND REMOVE

This command stops and removes all containers specified in the docker-compose-local.yml configuration. This command can be used in place of the 'stop' and 'rm' commands.

```
docker-compose -f docker-compose-local.yml down
```

