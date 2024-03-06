# Org Meeting Expeller

Expel AI or guest users immediately after entry to a meeting (across the org).
<!--[![Vidcast Overview](https://github.com/wxsd-sales/custom-pmr-pin/assets/19175490/4861e7cd-7478-49cf-bada-223b30810691)](https://app.vidcast.io/share/3f264756-563a-4294-82f7-193643932fb3)-->
<!--[![Vidcast Overview](https://github-production-user-asset-6210df.s3.amazonaws.com/19175490/249649420-980de741-1a2c-4aea-883e-4da629bc8701.png)](https://app.vidcast.io/share/677cc9bc-b0bb-4419-9338-5f4bbe0100a3)-->


## Setup

### Prerequisites & Dependencies:

- Developed on MacOS Ventura (13.2.1) & Ubuntu Bionic (18.04)
- Developed on Python 3.8.1 & 3.8.3
-   Other OS and Python versions may work but have not been tested

<!-- GETTING STARTED -->

### Installation Steps:

Clone from source:  
```
git clone https://github.com/wxsd-sales/org-meeting-expeller.git
```

1. A ```.env``` file is required in ```.devcontainer/server``` regardless of whether you are running as a python script or as a container.  The ```.env``` file should contain the following variables:
```
MY_APP_PORT=8080

#A Bot is used to send a message to a preconfigured space whenever a person/bot matching the EXPEL_DOMAINS is expelled
WEBEX_ALERT_BOT_TOKEN="ABCD_EFGH_IJKL-mnop-qrst-uvwx"
WEBEX_ALERT_ROOM_ID="Y21234567890"

#Meeting Expeller (Integration) created on developer.webex.com with the scopes listed in the scopes variable below.
WEBEX_CLIENT_ID=
WEBEX_CLIENT_SECRET=
WEBEX_REFRESH_TOKEN=""
MY_URI="https://some.example.ngrok.io"
WEBEX_SCOPES="spark%3Akms%20meeting%3Acontrols_write%20meeting%3Aadmin_schedule_write%20meeting%3Aschedules_read%20meeting%3Aparticipants_read%20spark%3Apeople_read%20meeting%3Acontrols_read%20meeting%3Aadmin_participants_read%20meeting%3Aparticipants_write%20meeting%3Aadmin_schedule_read%20meeting%3Aschedules_write"

#The email address of the Webex Licensed Admin account that will be used as the account to expel bots, enter below:
ADMIN_EMAIL=""
EXPEL_DOMAINS="fireflies.ai,gong.io,read.ai"
```

2. The repo is designed to be run as a docker container, so you can build from the dockerfile by navigating to the .devcontainer directory and running:
```
docker build -t org-meeting-expeller .
```
```
docker run -i -p 8080:8080 -t org-meeting-expeller
```   
**- OR -**  
You can run this directly in python after installing the requirements.txt in ```.devcontainer/server```:
```
pip install -r requirements.txt
```
Then,
```
python server.py
```


## License

All contents are licensed under the MIT license. Please see [license](LICENSE) for details.

## Disclaimer

<!-- Keep the following here -->  
Everything included is for demo and Proof of Concept purposes only. Use of the site is solely at your own risk. This site may contain links to third party content, which we do not warrant, endorse, or assume liability for. These demos are for Cisco Webex usecases, but are not Official Cisco Webex Branded demos.
 
 
## Support

Please contact the Webex SD team at [wxsd@external.cisco.com](mailto:wxsd@external.cisco.com?subject=OrgMeetingExpeller) for questions. Or for Cisco internal, reach out to us on Webex App via our bot globalexpert@webex.bot & choose "Engagement Type: API/SDK Proof of Concept Integration Development". 
