/*
START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/

// event listener to run after  DOM is loaded
document.addEventListener('DOMContentLoaded', async function() {
    // initialize DOM elements and CSRF token 
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const liveStreamButton = document.getElementById('live-streaming-btn');
    const videoDisplayFeed = document.getElementById('video-display-feed');
    const VideoMicPermissionMessage = document.getElementById('video-mic-permission-message');

    // flag to track if permission for camera and microphone was given
    let isVideoMicPermissionGranted = false;

    // checks permissions for camera and microphone on page load
    async function checkPermissions() {
        try {
            const cameraPermission = await navigator.permissions.query({ name: 'camera' });
            const microphonePermission = await navigator.permissions.query({ name: 'microphone' });

            // update flag if both camera and microphone permissions were given
            if (cameraPermission.state === 'granted' && microphonePermission.state === 'granted') {
                isVideoMicPermissionGranted = true;
            }
        } catch (error) {
            console.error("Error querying permissions:", error);
        }
    }

    // calls function 
    checkPermissions();

    // requests access to user's mic and camera
    async function requestMicAndCameraAccess() {
        // check if getUserMedia API is supported
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            console.error("getUserMedia is not supported");
            showPermissionMessage('Your browser does not support access to camera and microphone. Please check another browser', 'alert-warning');
            updateForCameraStateUI(false);
            return;
        }
        // if permission hasn't been give, show message 
        if (!isVideoMicPermissionGranted) {
            showPermissionMessage('If you are using Chrome browser, please manually allow camera and microphone access by visiting chrome settings page.', 'alert-info');
        }

        try {
            // requests access to user's camera and mic
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
            isVideoMicPermissionGranted = true; // update flag once permission is given
            VideoMicPermissionMessage.style.display = 'none';

            // setups video feed if permission is given
            if (videoDisplayFeed) {
                videoDisplayFeed.srcObject = stream;
                videoDisplayFeed.onloadedmetadata = () => videoDisplayFeed.play();
            }

            // updates UI to show current state of camera
            updateForCameraStateUI(true);
            await fetchRequestWithCSRF('/enable_camera', true);

        } catch (error) {
            // handles errors if user denies permission
            console.error("Error! Can not access audio and video:", error);
            showPermissionMessage('Access to camera and mic was denied.', 'alert-danger');
            updateForCameraStateUI(false);
        }
    }

    // displays permission message 
    function showPermissionMessage(message, className) {
        VideoMicPermissionMessage.textContent = message;
        VideoMicPermissionMessage.className = `alert ${className}`;
        VideoMicPermissionMessage.style.display = 'block';
    }

    // updates UI based oncamera state
    function updateForCameraStateUI(isCameraTurnedOn) {
        liveStreamButton.classList.toggle('btn-primary', isCameraTurnedOn);
        liveStreamButton.classList.toggle('btn-outline-primary', !isCameraTurnedOn);
        liveStreamButton.innerHTML = isCameraTurnedOn ? '<i class="fa-solid fa-circle-play icon-margin"></i>Live Streaming' : '<i class="fa-solid fa-circle-stop icon-margin"></i>Not Streaming';
        videoDisplayFeed.style.display = isCameraTurnedOn ? 'block' : 'none';
        document.getElementById('video-placeholder').style.display = isCameraTurnedOn ? 'none' : 'block';
    }

    // stop the video stream
    function stopVideoStreaming() {
        if (videoDisplayFeed.srcObject) {
            videoDisplayFeed.srcObject.getTracks().forEach(track => track.stop());
            videoDisplayFeed.srcObject = null;
        }
    }

    // make secure POST request 
    async function fetchRequestWithCSRF(url, isCameraTurnedOn) {
        try {
            // sends POST request with CSRF token 
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken }
            });
            const data = await response.json();
            updateForCameraStateUI(isCameraTurnedOn);

            // stops video streaming if camera is turned off
            if (!isCameraTurnedOn) {
                stopVideoStreaming();
            }
        } catch (error) {
            console.error(`Error in fetchRequestWithCSRF: ${error}`);
        }
    }

    // event listeners for camera on and off buttons
    document.getElementById("cameraon").addEventListener("click", () => requestMicAndCameraAccess());
    document.getElementById("cameraoff").addEventListener("click", () => {
        stopVideoStreaming(); // stop streaming before turning camera off
        fetchRequestWithCSRF('/disable_camera', false);
        updateForCameraStateUI(false); // updates UI
    });

    // updates video container based on state of video feed
    function updateVideoContainer() {
        const videoContainer = document.querySelector('.video-container');
        videoContainer.style.paddingTop = videoDisplayFeed.style.display === 'block' ? '0' : '56.25%';
    }

    // event listener for metadata loading
    videoDisplayFeed.addEventListener('loadedmetadata', () => {
        updateVideoContainer();
    });
});

// References:
// https://developer.mozilla.org/en-US/docs/Web/API/Document/DOMContentLoaded_event
// https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
// https://developer.mozilla.org/en-US/docs/Web/API/Navigator/getUserMedia
// https://www.w3schools.com/jsref/event_onloadedmetadata.asp
// https://github.com/renderedtext/render_async/issues/90
// https://wiki.selfhtml.org/wiki/JavaScript/DOM/Event/DOMContentLoaded
// https://stackoverflow.com/questions/34215937/getusermedia-not-supported-in-chrome
// https://stackoverflow.com/questions/40893537/fetch-set-cookies-and-csrf
// https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
// https://flask-wtf.readthedocs.io/en/1.0.x/csrf/
// https://stackoverflow.com/questions/60510765/flask-ajax-bad-request-the-csrf-token-is-missing
// https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Build_a_phone_with_peerjs/Connect_peers/Get_microphone_permission
// https://stackoverflow.com/questions/15993581/reprompt-for-permissions-with-getusermedia-after-initial-denial
// https://medium.com/joinglimpse/how-to-build-beautiful-camera-microphone-permission-checking-for-websites-e6a08415fa76
// https://www.freecodecamp.org/news/handling-mic-input-permissions-and-speech-recognition-in-chrome-extensions-ff7e3ca84cb0/
// https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamTrack/stop
// https://stackoverflow.com/questions/11642926/stop-close-webcam-stream-which-is-opened-by-navigator-mediadevices-getusermedia
// https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/srcObject
// https://stackoverflow.com/questions/77450213/sending-csrftoken-using-fetch-api-from-react-to-django
// https://dmitripavlutin.com/javascript-fetch-async-await/
// https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch


/*
END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/