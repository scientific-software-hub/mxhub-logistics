## ISPyB logistics

The ISPyB logistics is a project originally created by Diamond Light Source.

The original repository is here:
[https://github.com/DiamondLightSource/flask-ispyb-logistics](https://github.com/DiamondLightSource/flask-ispyb-logistics)

Clemente forked the repository under:
[https://github.com/clemenbor/flask-ispyb-logistics](https://github.com/clemenbor/flask-ispyb-logistics)

Since the Version of Diamond uses a SynchWeb connection to update the dewars in the database Thorben created a Version that works without SxnchWeb

### Example video from Diamond

Check the following video to see an example on how ISPyB logistics works at Diamond Light Source:<br>
[https://photos.app.goo.gl/X22s8y1MDWfyHd5a9](https://photos.app.goo.gl/X22s8y1MDWfyHd5a9)

## Installation

ISPyB logistics requires Python 3.8. The ispybdev machine has Python 3.8 installed on the Operating System. However, is better to use a virtual environment to be able to install all the ISPyB logistincs dependencies isolated.

First you have to make sure to install the **python3-venv** library:
```
sudo apt install python3-venv
```

Then you may clone the ISPyB logistics project. In this example we make the installation under the ispybdev user:
```
cd /home/ispybdev/projects/
git clone https://github.com/clemenbor/flask-ispyb-logistics
```

After that, you just need to create the virtual environment:
```
cd /home/ispybdev/projects/flask-ispyb-logistics
python3 -m venv venv
```

Finally, activate the virtual environment within the project:
```
source venv/bin/activate
```

### Install dependencies

Now that we have a Python3.8 virtual environment let's install the dependencies:
```
# Make sure to install wheel first
pip install wheel
pip install -r requirements.txt
```

If you want to run the flask test you may need also to install the following dependencies:
```
pytest
flask_testing
```

### Setting up the database connection

Adapt the following file to setup the database connection:
```
/home/ispybdev/projects/flask-ispyb-logistics/api/tests/test.cfg
```

### Running the API flask server:

Before running the API flask server, you have to fisrt setup the following environment variables:
```
export ISPYB_CONFIG_FILE=/home/ispybdev/projects/flask-ispyb-logistics/api/tests/test.cfg
export ISPYB_CONFIG_SECTION=ispyb_dev
export FLASK_ENV=development
```

To run the API server then execute:
```
flask run --host 131.169.73.83 --port 8008
```

**131.169.73.83** is the current IP of the ispybdev machine and we use port **8008** to avoid any conflicts with the Java version of ISPyB.

### Running the VUE.js client (User interface)

To run the Vue client with a specific port read the following:
[https://stackoverflow.com/questions/47219819/how-to-change-port-number-in-vue-cli-project](https://stackoverflow.com/questions/47219819/how-to-change-port-number-in-vue-cli-project)

Some installation instructions for the client are here:
[https://github.com/clemenbor/flask-ispyb-logistics/tree/master/client](https://github.com/clemenbor/flask-ispyb-logistics/tree/master/client)

Before running the project you have to [make sure npm is installed](https://gitlab.desy.de/p11-controls/ispyb/ispyb-documentation/-/blob/main/docs/java/exi.md#install-npm) and then run:
```
cd /home/ispybdev/projects/flask-ispyb-logistics/client
npm install
```

Now adapt the VUE configuration file to point to the right api target URL (The one running the flask server. Ex: http://131.169.73.83:8008):
```
/home/ispybdev/projects/flask-ispyb-logistics/client/vue.config.js
```

Finally to run the client server:
```
cd /home/ispybdev/projects/flask-ispyb-logistics/client
npm run serve -- --port 3000
```

### Relevant URLs

#### Main ISPyB logistics menu
[http://131.169.73.83:3001/](http://131.169.73.83:3001/)

#### Stores Dewar Management Zone
To handle dewars coming into or out of the facility
[http://131.169.73.83:3001/stores/](http://131.169.73.83:3001/stores/)

#### Zone 6

Zone 6 has been renamed for DESY purposes.

The zone 6 user interface:
[http://131.169.73.83:3001/zone6/](http://131.169.73.83:3001/zone6/)

The API call the user interface is doing:
[http://131.169.73.83:3001/api/dewars/locations/zone6](http://131.169.73.83:3001/api/dewars/locations/zone6)

Note: I manually set the storageLocation in the ISPyB database for DESY0313859 to STORES-IN (both in the DewarTransportHistory and the Dewar table.

### ISPyB database tables involved within the ISPyB logistics project

Tables involved:<br>

Dewar, DewarTransportHistory, BLSession, Proposal, Person, Shipping


