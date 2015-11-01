# Used third-party libraries

* pyst
  Interface with Asterisk using either AGI or Manager interfaces
* sqlalchemy
  Database interface

# Setup developemnt enrironment

```bash
$ virtualenv venv
$ source venv/bin/activate
$ pip install --allow-external pyst --allow-unverified pyst -r requirements.txt
```

## Database setup

Each SIP user must be inserted in the database of users with a balance. The python code snippet bellow is an example of a insertion of two users.

```python
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from apiConfig import db
from models import User

admin = User('admin', 'adm123', '999999999', '9999', True)
guest = User('guest', '123123', '999999999', '0000', False)

db.session.add(admin)
db.session.add(guest)
db.session.commit()
```

please check test_initial_user.py

## Using curl to test api

login

```bash
curl -c cookiefile -d "username=admin&password=adm123" -X POST -s http://localhost:5000/login
```

add user

```bash
curl -b cookiefile -H "Content-Type: application/json" -X POST -d '{"username":"yourusername","password":"yourpassword","clid":"999999999","balance":"0","admin":'false'}' -s http://localhost:5000/api/users
```

update user

```bash
curl -X PATCH -H "Content-Type: application/json" -d '{"username":"yournewusername","password":"yournewpassowrd"}' -s http://localhost:5000/api/users/youroldusername -b cookiefile
```
remove user

```bash
curl -X DELETE -s http://localhost:5000/api/users/yourusername -b cookiefile
```

## Asterisk setup

With a working Asterisk server you must have at least two SIP accounts. An example of the corresponding section of `sip.conf` follows.

```
[1000000000]
type=friend
secret=laps
host=dynamic
context=celcom

[2000000000]
type=friend
secret=laps
host=dynamic
context=celcom
```

The referenced context in `sip.conf` must exist in the `extensions.conf` the code bellow is an example.

```
[celcom]
exten => _ZXXXXXXXX,1,AGI(celcombiller)
```

celcombiller is an AGI, implemented in the file [celcombiller.py](celcombiller.py) and it must run in the virtual environment created in the first section, a file with something like the content bellow should be created in `/var/lib/asterisk/agi-bin` with execution permission.

```bash
#!/bin/bash
/home/psb/Dropbox/git-projects/celcombiller/venv/bin/python /home/psb/git-projects/celcombiller/celcombiller.py
```
