/*
START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/

// creates video card element
function createGoogleDriveVideoCard(video) {
    // create div element 
    const videoGoogleDriveCard = document.createElement('div');

    // set class and width for video card
    videoGoogleDriveCard.className = 'card mr-2';
    videoGoogleDriveCard.style.width = '20rem';

    // creates and adds card header for video card
    const cardGoogleDriveHeader = createGoogleDriveCardHeader(video);
    videoGoogleDriveCard.appendChild(cardGoogleDriveHeader);

    // creates and ass video body for video card
    const videoGoogleDriveBody = createGoogleDriveVideoBody(video);
    videoGoogleDriveCard.appendChild(videoGoogleDriveBody);

    // creates and adds controls container for video card
    const controlsGoogleDriveContainer = createGoogleDriveControlsContainer(video);
    videoGoogleDriveCard.appendChild(controlsGoogleDriveContainer);

    // return video card element
    return videoGoogleDriveCard;
}

// creates card header element for video
function createGoogleDriveCardHeader(video) {
    const cardGoogleDriveHeader = document.createElement('div');
    cardGoogleDriveHeader.className = 'card-header d-flex justify-content-between';

    // create span for displaying detected objects
    const detectedObjectGoogleDriveSpan = document.createElement('span');
    detectedObjectGoogleDriveSpan.innerText = video.detected_objects ? toTitleCase(video.detected_objects) : 'No Object Detected';

    // create span for showing time
    const timeGoogleDriveSpan = document.createElement('span');
    timeGoogleDriveSpan.innerText = video.capture_time;

    // adds spans to card header
    cardGoogleDriveHeader.appendChild(detectedObjectGoogleDriveSpan);
    cardGoogleDriveHeader.appendChild(timeGoogleDriveSpan);

    return cardGoogleDriveHeader;
}


// creates video body element for video
function createGoogleDriveVideoBody(video) {
    // create div for video body without padding
    const videoGoogleDriveBody = document.createElement('div');
    videoGoogleDriveBody.className = 'card-body p-0';

    // creates container for video 
    const googleDriveVideoContainer = document.createElement('div');
    googleDriveVideoContainer.className = 'video-container-small-activity d-flex justify-content-center align-items-center pt-4 px-4';

    // creates iframe for video preview
    const previewIframeGoogleDrive = document.createElement('iframe');
    previewIframeGoogleDrive.src = video.link.replace('/view', '/preview');
    previewIframeGoogleDrive.className = 'w-100 border-0';
    previewIframeGoogleDrive.style.height = '160px';
    previewIframeGoogleDrive.allow = "autoplay";

    // adds preview iframe to video container
    googleDriveVideoContainer.appendChild(previewIframeGoogleDrive);

    // adss video container to video body
    videoGoogleDriveBody.appendChild(googleDriveVideoContainer);

    return videoGoogleDriveBody;
}

// creates controls container for video
function createGoogleDriveControlsContainer(video) {
    // create div for controls container 
    const controlsGoogleDriveContainer = document.createElement('div');
    controlsGoogleDriveContainer.className = 'video-controls mt-4 d-flex justify-content-between px-4 pb-4';

    // create container for metadata
    const metadataGoogleDriveContainer = document.createElement('div');
    metadataGoogleDriveContainer.className = 'video-metadata d-flex flex-column align-items-start';

    // creates span for showing detected objects 
    const detectedObjectGoogleDriveControlsSpan = document.createElement('span');
    detectedObjectGoogleDriveControlsSpan.innerText = `Detected: ${toTitleCase(video.detected_objects)}`;

    // creates span for showing intruder position
    const positionGoogleDriveSpan = document.createElement('span');
    positionGoogleDriveSpan.innerText = `Position: ${video.position}`;

    // creates span for showing intruder size
    const intruderSizeGoogleDriveSpan = document.createElement('span');
    intruderSizeGoogleDriveSpan.innerText = `Size: ${video.motion_size}`;

    // adds metadata elements to metadata container
    metadataGoogleDriveContainer.appendChild(detectedObjectGoogleDriveControlsSpan);
    metadataGoogleDriveContainer.appendChild(positionGoogleDriveSpan);
    metadataGoogleDriveContainer.appendChild(intruderSizeGoogleDriveSpan);

    // creates container for buttons
    const buttonContainerGoogleDrive = document.createElement('div');
    buttonContainerGoogleDrive.className = 'button-container d-flex flex-column align-items-end';

    // add "download" button for Google Drive videos
    if (video.source === 'google_drive') {
        const downloadLink = document.createElement('a');
        downloadLink.href = video.downloadLink;
        downloadLink.className = 'btn btn-secondary btn-sm mb-2 btn-fixed-width';
        downloadLink.innerText = 'Download';
        downloadLink.setAttribute('download', '');
        buttonContainerGoogleDrive.appendChild(downloadLink);
    }

    // adds delete button 
    const deleteButton = createGoogleDriveDeleteButton(video);
    deleteButton.className += ' btn-fixed-width';
    buttonContainerGoogleDrive.appendChild(deleteButton);

    // adds metadata and button containers to controlsGoogleDriveContainer
    controlsGoogleDriveContainer.appendChild(metadataGoogleDriveContainer);
    controlsGoogleDriveContainer.appendChild(buttonContainerGoogleDrive);

    return controlsGoogleDriveContainer;
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

/*
END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/