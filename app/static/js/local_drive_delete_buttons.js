/*
START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/

// local video delete functionality
function createLocalVideoDeleteButton(video) {
    // verifies if video path is valid
    if (!video.link) {
        return null;
    }

    // gets file name from video link
    const localVideoFileName = video.link.split('/').pop();

    // creates delete button
    const deleteButton = document.createElement('button');
    deleteButton.className = 'btn btn-danger btn-sm';
    deleteButton.innerText = 'Delete';

    // event handler for  delete button click
    deleteButton.onclick = function(event) {
        event.preventDefault();

        // clear existing attributes
        clearConfirmationButtonData();

        // sets video file name and type
        const confirmDeletionButton = document.getElementById('confirmDeletionButton');
        confirmDeletionButton.setAttribute('data-video-identifier', localVideoFileName);
        confirmDeletionButton.setAttribute('data-video-type', 'local');

        // dislpay delete confirmation modal
        $('#confirmationDeleteModal').modal('show');
    };

    return deleteButton;
}

function deleteLocalVideo(localVideoFileName) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch(`/delete-local-video/${localVideoFileName}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response not ok');
            }
            return response.json();
        })
        .then(data => {
            displayToast(data.success);
            displayVideosForSelectedDate();
        })
        .catch(error => {
            console.error('Error! Can not delete local video:', error);
            alert('Error! Can not delete local video.');
        });
}

/////////////////////////////////////////////////////////////////////////////// 
// google drive delete functionality
// create delete button for google drive video
function createGoogleDriveDeleteButton(video) {
    // verifies if video path is valid
    if (!video.google_drive_file_id) {
        return null;
    }

    // creates delete button
    const deleteButton = document.createElement('button');
    deleteButton.className = 'btn btn-danger btn-sm';
    deleteButton.innerText = 'Delete';

    // event handler for delete button click
    deleteButton.onclick = function(event) {
        event.preventDefault();

        // clears existing attributes
        clearConfirmationButtonData();

        // sets video ID and type
        const confirmDeletionButton = document.getElementById('confirmDeletionButton');
        confirmDeletionButton.setAttribute('data-video-identifier', video.google_drive_file_id);
        confirmDeletionButton.setAttribute('data-video-type', 'google_drive');

        // displays delete confirmation modal
        $('#confirmationDeleteModal').modal('show');
    };
    return deleteButton;
}

function deleteGoogleDriveVideo(videoId) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch(`/delete-google-drive-video/${videoId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response not ok');
            }
            return response.json();
        })
        .then(data => {
            displayToast(data.success);
            displayVideosForSelectedDate();
        })
        .catch(error => {
            console.error('Error! Can not delete video:', error);
            alert('Error! Can not delete video.');
        });
}

/////////////////////// common functionality
function clearConfirmationButtonData() {
    const confirmDeletionButton = document.getElementById('confirmDeletionButton');
    confirmDeletionButton.removeAttribute('data-video-identifier');
    confirmDeletionButton.removeAttribute('data-video-type');
}

document.getElementById('confirmDeletionButton').addEventListener('click', function(event) {
    const identifier = event.target.getAttribute('data-video-identifier');
    const type = event.target.getAttribute('data-video-type');

    if (type === 'google_drive') {
        deleteGoogleDriveVideo(identifier);
    } else if (type === 'local') {
        deleteLocalVideo(identifier);
    }

    // hides modal after deletion
    $('#confirmationDeleteModal').modal('hide');

    // clears button data to avoid confusion between local and google drive deletion
    clearConfirmationButtonData();
});


// References: 
// https://developers.google.com/drive/api/reference/rest/v3/files/delete
// https://dev.to/kamalhossain/download-and-delete-via-google-drive-api-17i3
// https://www.w3schools.com/jsref/event_onclick.asp
// https://www.freecodecamp.org/news/html-button-onclick-javascript-click-event-tutorial/
// https://developer.mozilla.org/en-US/docs/Web/API/Element/setAttribute
// https://developer.mozilla.org/en-US/docs/Web/API/Document/getElementById
// https://laracasts.com/discuss/channels/vue/cant-read-csrf-token-from-meta-tag
// https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
// https://stackoverflow.com/questions/65048558/django-x-csrf-token-cannot-be-set-in-javascript-fetch
// https://stackoverflow.com/questions/16522158/delete-file-in-google-drive-with-javascript
// https://www.basedash.com/blog/how-to-delete-a-file-in-javascript#
// https://stackoverflow.com/questions/19721621/how-to-delete-file-from-folder-using-javascript
// https://www.oreilly.com/library/view/pure-javascript/0672315475/0672315475_ch09lev2sec56.html

/*
END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/