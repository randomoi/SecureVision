/*
START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/

// display videos from both Google Drive and local sources
function displayVideosForSelectedDate() {
    const DateSelected = document.getElementById("date-selector").value || new Date().toISOString().substring(0, 10);
    const selectedDateCleaned = DateSelected.substring(0, 10);

    Promise.all([
            fetch(`/retrieve-google-videos-for-date?date=${selectedDateCleaned}`).then(response => response.json()),
            fetch(`/retrieve-local-videos-for-date?date=${selectedDateCleaned}`).then(response => response.json())
        ])
        .then(([googleDriveVideos, localVideos]) => {
            const allVideos = [...googleDriveVideos, ...localVideos];
            updateVideoContentOnPage(allVideos);
        })
        .catch(error => console.error('Error! Can not fetch videos:', error));
}

// updates video content on webpage for both local and google drive videos
function updateVideoContentOnPage(videos) {
    const videoScrollingContainer = document.querySelector('.video-scrolling-container');
    videoScrollingContainer.innerHTML = '';

    if (videos.length === 0) {
        videoScrollingContainer.innerHTML = '<p class="text-muted">Videos are unavailable.</p>';
        return;
    }

    videos.forEach(video => {
        const cardForVideo = (video.source === 'google_drive') ? createGoogleDriveVideoCard(video) : createLocalVideoCard(video);
        videoScrollingContainer.appendChild(cardForVideo);
    });
}

// populates dropdown dates and srts video loading
function populateDropdownWithDate() {
    fetch('/get-available-dates')
        .then(response => response.json())
        .then(data => {
            const availableDateSelector = document.getElementById('date-selector');
            availableDateSelector.innerHTML = '';
            data.unique_dates.forEach(dateStr => {
                const option = document.createElement('option');
                option.value = dateStr;
                option.textContent = dateStr;
                availableDateSelector.appendChild(option);
            });
            const recentDate = data.unique_dates.sort((a, b) => b.localeCompare(a))[0];
            availableDateSelector.value = recentDate || '';
            displayVideosForSelectedDate();
        })
        .catch(error => console.error('Error! Can not fetch dates:', error));
}

document.addEventListener("DOMContentLoaded", populateDropdownWithDate);
document.getElementById("date-selector").addEventListener("change", displayVideosForSelectedDate);

///////////////////////////////////////////////

function createLocalVideoCard(video) {
    // creates div element for video card
    const cardForVideo = document.createElement('div');

    // set class and width for video card
    cardForVideo.className = 'card mr-2';
    cardForVideo.style.width = '20rem';

    // uses video file name as ID (solved problem with conflict this way) for local videos
    const localVideoID = video.source === 'local' ? video.link.split('/').pop() : video.id;

    // updates video object with new ID
    video.id = localVideoID;

    // creates and adds card header for video card
    const cardLocalHeader = createLocalCardHeader(video);
    cardForVideo.appendChild(cardLocalHeader);

    // creates and adds video body for video card
    const videoLocalBody = createLocalVideoBody(video);
    cardForVideo.appendChild(videoLocalBody);

    // creates and adds controls container for video card
    const controlsLocalContainer = createLocalControlsContainer(video);
    cardForVideo.appendChild(controlsLocalContainer);

    // return constructed video card element
    return cardForVideo;
}


// creates card header element for video
function createLocalCardHeader(video) {
    const cardLocalHeader = document.createElement('div');
    cardLocalHeader.className = 'card-header d-flex justify-content-between';

    // create span for showing detected objects 
    const objectDetectedLocalSpan = document.createElement('span');
    objectDetectedLocalSpan.innerText = video.detected_objects ? toTitleCase(video.detected_objects) : 'No Object Detected';

    // create span for displaying time
    const localTimeSpan = document.createElement('span');
    localTimeSpan.innerText = video.capture_time;

    // adds spans to card header
    cardLocalHeader.appendChild(objectDetectedLocalSpan);
    cardLocalHeader.appendChild(localTimeSpan);

    return cardLocalHeader;
}

// creates video body element 
function createLocalVideoBody(video) {
    // creates div for video body
    const videoLocalBody = document.createElement('div');
    videoLocalBody.className = 'card-body p-0';
    // height and width for video
    const localVideoHeight = '160px';
    const localVideoWidth = '100%';

    const localVideoContainer = document.createElement('div');
    localVideoContainer.className = 'local-video-container d-flex justify-content-center align-items-center pt-4 px-4';

    // creates video element for  preview
    const videoElement = document.createElement('video');
    videoElement.src = video.link;
    videoElement.className = 'w-100';
    videoElement.controls = true;
    videoElement.style.height = localVideoHeight;
    videoElement.style.width = localVideoWidth;

    localVideoContainer.appendChild(videoElement);
    videoLocalBody.appendChild(localVideoContainer);

    return videoLocalBody;
}


// creates controls container for video
function createLocalControlsContainer(video) {
    // creates div for controls container
    const controlsLocalContainer = document.createElement('div');
    controlsLocalContainer.className = 'video-controls mt-4 d-flex justify-content-between px-4 pb-4';

    // creats ontainer for metadata
    const metadataLocalContainer = document.createElement('div');
    metadataLocalContainer.className = 'video-metadata d-flex flex-column align-items-start';

    // create span for showing detected objects 
    const detectedObjectLocalSpan = document.createElement('span');
    detectedObjectLocalSpan.innerText = `Detected: ${toTitleCase(video.detected_objects)}`;

    // create span for shoqing intruder position
    const positionLocalSpan = document.createElement('span');
    positionLocalSpan.innerText = `Position: ${video.position}`;

    // creates span for showing intruder size
    const intruderSizeLocalSpan = document.createElement('span');
    intruderSizeLocalSpan.innerText = `Size: ${video.motion_size}`;

    // adds metadata elements to metadata container
    metadataLocalContainer.appendChild(detectedObjectLocalSpan);
    metadataLocalContainer.appendChild(positionLocalSpan);
    metadataLocalContainer.appendChild(intruderSizeLocalSpan);

    // create container for buttons
    const buttonLocalContainer = document.createElement('div');
    buttonLocalContainer.className = 'button-container d-flex flex-column align-items-end';

    // adds "download" button for local videos
    if (video.source === 'local') {
        const downloadLink = document.createElement('a');
        downloadLink.href = video.link;
        downloadLink.className = 'btn btn-secondary btn-sm mb-2 btn-fixed-width';
        downloadLink.innerText = 'Download';
        downloadLink.setAttribute('download', '');
        buttonLocalContainer.appendChild(downloadLink);

        // add "delete" button for local videos 
        const localVideoDeleteButton = createLocalVideoDeleteButton(video);
        localVideoDeleteButton.className += ' btn-fixed-width';
        buttonLocalContainer.appendChild(localVideoDeleteButton);
    }

    // adds metadata and button containers to controlsLocalContainer
    controlsLocalContainer.appendChild(metadataLocalContainer);
    controlsLocalContainer.appendChild(buttonLocalContainer);

    return controlsLocalContainer;
}

// References:
// https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelector
// https://developer.mozilla.org/en-US/docs/Web/API/Document/getElementById
// https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener
// https://gist.github.com/cgkio/7268045
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/RegExp/test
// https://getbootstrap.com/docs/5.0/forms/validation/
// https://developer.mozilla.org/en-US/docs/Web/API/Document/createElement
// https://stackoverflow.com/questions/11620698/how-to-trigger-a-file-download-when-clicking-an-html-button-or-javascript
// https://getbootstrap.com/docs/4.4/components/buttons/
// https://www.w3schools.com/jsref/met_node_appendchild.asp
// https://www.w3schools.com/jsref/dom_obj_frame.asp
// https://developers.google.com/drive/api/guides/manage-downloads
// https://stackoverflow.com/questions/60839431/downloading-a-file-from-google-drive-in-javascript-client
// https://stackoverflow.com/questions/54896470/how-to-return-the-promise-all-fetch-api-json-data
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all
// https://stackoverflow.com/questions/66647728/how-can-i-control-a-set-of-videos-with-their-parent-containers
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/localeCompare
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort
// https://stackoverflow.com/questions/39202616/difference-between-sort-sortfunctiona-breturn-a-b-and-sortfunctiona

/*
END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/