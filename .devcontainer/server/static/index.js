var CURRENT_PID = null;
var GUEST_ID = null;
var currentMeetingLocusUrl = null;
var currentMeetingSipAddress = null;
var demoMap = {};
var token = Cookies.get("access_token");
var destination = null;


function updateMainMessage(msg, messageType){
    if(messageType == 1){
        $('#status-message').removeClass("is-success");
        $('#status-message').removeClass("is-warning");
        $('#status-message').addClass("is-danger");
    } else if(messageType == 2){ 
        $('#status-message').removeClass("is-success");
        $('#status-message').removeClass("is-danger");
        $('#status-message').addClass("is-warning");
    } else {
        $('#status-message').removeClass("is-danger");
        $('#status-message').removeClass("is-warning");
        $('#status-message').addClass("is-success");
    }
    $('#status-message').text(msg);
    $('#status-message').css({"visibility":"visible"});
}


$('#logout').on('click', function(e){
    window.location = "/logout";
})


$('#terminate').on('click', function(e){
    if(CURRENT_PID){
        $(this).addClass('is-loading');
        let data = {pid:CURRENT_PID, token:token};
        $.post("/kill", JSON.stringify(data), function(resp){
            console.log(resp);
            if(resp.success){
                $('#terminate').attr('disabled', true);
                enableDemoButtons();
                updateMainMessage(`${resp.demo} terminated.`, 2);
            } else {
                updateMainMessage("An error occurred ending the process.", 1);
            }
            $('#terminate').removeClass('is-loading');
        });
    } else {
        updateMainMessage("No running processes found.", 1);
        $('#terminate').attr('disabled', true);
    }
});

function enableDemoButtons(){
    $('.demo-button').attr('disabled', false);
}

function disableDemoButtons(){
    $('.demo-button').attr('disabled', true);
}

function setProcRunningUI(resp){
    let terminate_disabled = $('#terminate').attr('disabled')
    console.log(`setProcRunningUI count:${resp.count}`);
    console.log(`setProcRunningUI terminate_disabled:${terminate_disabled}`);
    if(resp.count && resp.count > 0){
        if(!$("#terminate").hasClass('is-loading')){
            disableDemoButtons();
            $('#terminate').attr('disabled',false);
            let pids = Object.keys(resp.procs);
            CURRENT_PID = pids[0];
            let demo = resp.procs[CURRENT_PID].demo;
            updateMainMessage(`Running ${demo}`);
            console.log(`setProcRunningUI running ${demo}`);
        }
    } else if(!terminate_disabled){
        enableDemoButtons();
        $('#terminate').attr('disabled',true);
        $('#status-message').css({"visibility":"hidden"});
    }
}

function checkProcs(){
    console.log('checkProcs');
    let data = {token:token};
    $.post("/procs", JSON.stringify(data), function(resp){
        setProcRunningUI(resp);
    });
}

function load(meetingId){
    let data = {meeting_id: meetingId};
    $.post("/", JSON.stringify(data), function(resp){
        //TODO: What happens if I refresh the page in web app mode?  In EA Mode?
        //      Should I even be able to start a second one into the same meeting with the same token?
        //let resp = JSON.parse(result);
        console.log(resp);
        if(resp.avatar){
            $('#webex-avatar').attr("src", resp.avatar);
        }
        if(resp.destination){
            destination = resp.destination;
        }

        if(resp.demos){
            for(let demo of resp.demos){
                console.log(demo);
                let cleanName = demo.replace(/ /g,"_");
                demoMap[cleanName] = demo;
                $('#demos').append(
                    $('<div class="columns is-mobile is-centered mb-0" style="">').append(
                        $('<div class="column is-2-fullhd is-3-widescreen is-4-desktop is-5-tablet is-three-quarters-mobile is-centered">').append(
                            $(`<button id="${cleanName}" class="button demo-button is-fullwidth is-rounded is-info mr-1">`).append(
                                $('<span class="icon">').append(
                                    $('<i class="fas fa-play">')
                                ),
                                $('<span class="pb-1">').text(demo)
                            ).on('click', function(e){
                                $(this).addClass('is-loading');
                                disableDemoButtons();
                                updateMainMessage(`Launching ${demo}`);
                                let sipAddress = destination;
                                //#destination-input and meeting buttons are only relevant if loaded outside of EAF.
                                //#destination-input is disabled if a meeting button is selected, and enabled if not
                                if(!sipAddress && $('#destination-input').attr('disabled') != "disabled"){
                                    sipAddress = $('#destination-input').val();
                                } else if(!sipAddress && $('#destination-input').attr('disabled')){
                                    sipAddress = currentMeetingSipAddress;
                                }
                                let data = {destination:sipAddress, 
                                            locus_url:currentMeetingLocusUrl,
                                            demo:demo, 
                                            token:token}
                                $.post("/launch", JSON.stringify(data), function(resp){
                                    console.log(resp);
                                    if(resp.pid){
                                        CURRENT_PID = resp.pid;
                                        GUEST_ID = resp.guest_id;
                                        updateMainMessage(`Running ${demo}`);
                                        $('#terminate').attr('disabled',false);
                                    } else {
                                        if(resp.error){
                                            updateMainMessage(resp.error, 1);
                                        } else {
                                            updateMainMessage(`An error occurred with ${demo}`, 1);
                                        }
                                        enableDemoButtons();
                                    }
                                    $(`#${cleanName}`).removeClass('is-loading');
                                })
                            })
                        )
                    )
                )
            }
        }
        
        setProcRunningUI(resp);

        if(resp.error){
            console.log(`/demos response ERROR: ${resp.error}`);
            updateMainMessage(resp.error, 1);
        }
        
    });
}

function runBackup(){
    if(!embedded_app.about){
        $('#webapp-view').show();
        load();
    }
}

function admitMember(meeting, delta){
    for(let added of delta){
        console.log(added);
        if(added.status == "IN_LOBBY"){
            console.log("user in lobby.");
            if(added.participant.identity == GUEST_ID){
                console.log('Admitting this user');
                meeting.admit(added.id);
            }
        }
    }
}

function listenForDemoJoin(meeting){
    let locusId = meeting.locusId;
    if(currentMeetingLocusUrl && currentMeetingLocusUrl.indexOf(locusId) >= 0){
        console.log(`listening to member changes for meeting:${locusId}`);
        meeting.members.on('members:update', (payload) => {
        try{
            console.log("<members:update>", payload);
            admitMember(meeting, payload.delta.added);
            admitMember(meeting, payload.delta.updated);
        } catch (e){
            console.log('members.on(members:update) - error:');
            console.log(e);
        }
        });
    } else {
        console.log(`Not tracking meeting outside of this EA with LocusId:${locusId}`)
    }
}

function addMeeting(event){
    console.log('meeting:added event');
    console.log(event.meeting);
    let name = event.meeting.meetingInfo.meetingName;
    if(!name){
        name = event.meeting.meetingInfo.topic;
    }
    if(!name){
        try{
            name = event.meeting.partner.person.name;
        } catch (e){
            console.log("Trying to determine meeting name...");
            name = event.meeting.meetingInfo.sipUri
        }
    }
    
    $("#my-meetings").append(
        $(`<div id="mtg_${event.meeting.id}" class="columns is-centered"/>`).append(
          $('<div class="column is-centered pb-0"/>').append(
            $(`<button id="${event.meeting.id}" class="button meeting-button is-primary is-outlined is-rounded"/>`).text(name).on('click', function(e){
                $('.meeting-button').addClass('is-outlined');
                if(currentMeetingLocusUrl == event.meeting.locusUrl){
                    $(this).blur();
                    currentMeetingLocusUrl = null;
                    currentMeetingSipAddress = null;
                    $('#demos').hide();
                    $('#destination-input').attr('disabled', false);
                } else {
                    $(this).removeClass('is-outlined');
                    currentMeetingLocusUrl = event.meeting.locusUrl;
                    currentMeetingSipAddress = event.meeting.sipUri;
                    listenForDemoJoin(event.meeting);
                    $('#demos').show();
                    $('#destination-input').attr('disabled', true);
                }
            })
          )
        )
    );
    $('#select-meeting-label').show();
    $('#enter-destination-label').show();
    listenForDemoJoin(event.meeting);
}

function removeMeeting(event){
    console.log('meeting:removed event');
    console.log(event.meeting);
    $(`#mtg_${event.meetingId}`).remove();
    if(Object.keys(webex_sdk.meetings.meetingCollection.meetings).length == 0){
        $('#select-meeting-label').hide();
        $('#enter-destination-label').hide();
    }
  }

window.addEventListener('load', function () {
    console.log("Hello, app.");
    const webex_sdk = (window.webex_sdk = Webex.init({
        credentials: {
            access_token: token
        }
    }));

    webex_sdk.meetings.register()
      .then((data) => {
        console.log(data);
      })
      .catch(err => {
        console.error(err);
        alert(err);
        throw err;
      });

    webex_sdk.meetings.on('meeting:added', (event) => {
        addMeeting(event);
    });

    webex_sdk.meetings.on('meeting:removed', (event) => {
        removeMeeting(event);
    });

    $("#destination-input").on("input", function() {
        let input = $(this).val();
        if(/^\S+@\S+\.\S+$/.test(input)){
            $('.meeting-button').attr('disabled', true);
            $('#demos').show();
        } else {
            $('.meeting-button').attr('disabled', false);
            $('#demos').hide();
        }
        
     });

    setInterval(checkProcs, 8000);

    //console.log(window.webex);
    webex_sdk.meetings.syncMeetings();
    embedded_app = new window.webex.Application();
    setTimeout(runBackup, 3500);
    
    if(embedded_app.isSDKInitialized()){
        embedded_app.onReady().then(() => {
            console.log("onReady()", { message: "EA is ready." });
            console.log(embedded_app.application.states.user);
            //console.log(embedded_app.application.states.user.token);
            embedded_app.context.getMeeting().then((meeting) => {
                console.log(meeting);
                currentMeetingLocusUrl = meeting.url;
                $('#demos').show();
                load(meeting.id);
            });
        });
    }

});